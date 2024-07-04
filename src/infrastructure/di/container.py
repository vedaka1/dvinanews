import logging
from functools import lru_cache
from smtplib import SMTP_SSL
from typing import AsyncGenerator

import aiosmtplib
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from application.common.client import AsyncAppClient
from application.common.parser import Parser
from application.common.transaction import BaseTransactionManager
from application.usecases.commands import GetNews
from application.usecases.commands.send_message import SendMessage
from application.usecases.users import *
from application.usecases.users.get_user import GetAllSubscribedUsers
from application.usecases.users.update_user import SubscribeUser, UnsubscribeUser
from domain.users.repository import BaseUserRepository
from infrastructure.config import settings
from infrastructure.persistence.main import (
    create_session_factory,
    get_async_engine,
    get_sync_engine,
)
from infrastructure.persistence.repositories.user import UserRepository
from infrastructure.persistence.transaction import TransactionManager
from infrastructure.smtp.main import AsyncSMTPServer, BaseSMTPServer, SyncSMTPServer


@lru_cache(1)
def init_logger() -> logging.Logger:
    logging.basicConfig(
        # filename="log.log",
        level=logging.INFO,
        encoding="UTF-8",
        format="%(asctime)s %(levelname)s: %(message)s",
    )


class SettingsProvider(Provider):
    @provide(scope=Scope.APP)
    def async_engine(self) -> AsyncEngine:
        return get_async_engine()

    @provide(scope=Scope.APP)
    def sync_engine(self) -> Engine:
        return get_sync_engine()

    @provide(scope=Scope.APP)
    def logger(self) -> logging.Logger:
        return logging.getLogger()

    @provide(scope=Scope.APP)
    def async_app_client(self) -> AsyncAppClient:
        return ClientSession()

    @provide(scope=Scope.APP)
    async def app_smtp_server(self) -> BaseSMTPServer:
        server = AsyncSMTPServer(
            aiosmtplib.SMTP(
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_EMAIL,
                password=settings.SMTP_PASSWORD,
                use_tls=True,
            ),
            settings.SMTP_EMAIL,
            settings.SMTP_PASSWORD,
            settings.SMTP_EMAIL,
            settings.SMTP_SUBJECT,
        )
        await server.start()
        return server

    @provide(scope=Scope.APP)
    def parser(self) -> Parser:
        return BeautifulSoup()

    @provide(scope=Scope.APP)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
        return create_session_factory(engine)


class DatabaseConfigurationProvider(Provider):
    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def provide_db_connection(
        self, session_factory: async_sessionmaker
    ) -> AsyncGenerator[AsyncSession, None]:
        session = session_factory()
        yield session
        await session.close()


class DatabaseAdaptersProvider(Provider):
    scope = Scope.REQUEST

    user_repository = provide(UserRepository, provides=BaseUserRepository)
    transaction_manager = provide(TransactionManager, provides=BaseTransactionManager)


class UseCasesProvider(Provider):
    scope = Scope.REQUEST

    get_user_by_id = provide(GetUserByTelegramId)
    get_users = provide(GetAllUsers)
    get_subscribed_users = provide(GetAllSubscribedUsers)
    get_admins = provide(GetAllAdmins)
    delete_user = provide(DeleteUser)
    create_user = provide(CreateUser)
    promote_user = provide(PromoteUserToAdmin)
    demote_user = provide(DemoteUser)
    get_news = provide(GetNews)
    subscribe_user = provide(SubscribeUser)
    unsubscribe_user = provide(UnsubscribeUser)
    send_message = provide(SendMessage)


@lru_cache(1)
def get_container() -> AsyncContainer:
    return make_async_container(
        UseCasesProvider(),
        DatabaseAdaptersProvider(),
        DatabaseConfigurationProvider(),
        SettingsProvider(),
    )
