from dataclasses import dataclass
from logging import Logger

from application.common.transaction import BaseTransactionManager
from domain.users.repository import BaseUserRepository


@dataclass
class PromoteUserToAdmin:
    user_repository: BaseUserRepository
    transaction_manager: BaseTransactionManager
    logger: Logger

    async def __call__(self, user_id: int) -> None:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return "Пользователь не найден"
        if user.role == "admin":
            return "Пользователь уже имеет права администратора"
        try:
            user.role = "admin"
            await self.user_repository.update(user)
        except Exception as e:
            self.logger.error("usecase: UpdateUserRole error: {0}".format(e))
            return "Возникла ошибка"

        await self.transaction_manager.commit()
        return f"Пользователь {user.telegram_id} теперь имеет права администратора"


@dataclass
class DemoteUser:
    user_repository: BaseUserRepository
    transaction_manager: BaseTransactionManager
    logger: Logger

    async def __call__(self, command_args: str) -> str:
        if not command_args:
            return "Укажите id пользователя через пробел после команды"

        user = await self.user_repository.get_by_id(int(command_args.split()[0]))
        if not user:
            return "Пользователь не найден"

        if user.role == "user":
            return f"Пользователь {user.telegram_id} понижен в правах"

        try:
            user.role = "user"
            await self.user_repository.update(user)
        except Exception as e:
            self.logger.error("usecase: UpdateUserRole error: {0}".format(e))
            return "Возникла ошибка"

        await self.transaction_manager.commit()
        return f"Пользователь {user.telegram_id} понижен в правах"


@dataclass
class SubscribeUser:
    user_repository: BaseUserRepository
    transaction_manager: BaseTransactionManager
    logger: Logger

    async def __call__(self, user_id: int) -> str:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return "Пользователь не найден"

        if user.is_subscribed:
            return "Вы уже подписаны"

        try:
            user.is_subscribed = True
            await self.user_repository.update(user)
        except Exception as e:
            self.logger.error("usecase: UpdateUserRole error: {0}".format(e))
            return "Возникла ошибка"

        await self.transaction_manager.commit()
        return "Вы подписались на рассылку"


@dataclass
class UnsubscribeUser:
    user_repository: BaseUserRepository
    transaction_manager: BaseTransactionManager
    logger: Logger

    async def __call__(self, user_id: int) -> str:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return "Пользователь не найден"

        try:
            user.is_subscribed = False
            await self.user_repository.update(user)
        except Exception as e:
            self.logger.error("usecase: UpdateUserRole error: {0}".format(e))
            return "Возникла ошибка"

        await self.transaction_manager.commit()
        return "Вы отписались от рассылки"
