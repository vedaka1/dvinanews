from dataclasses import dataclass
from logging import Logger

from application.common.transaction import BaseTransactionManager
from domain.users.repository import BaseUserRepository
from domain.users.user import User


@dataclass
class GetAllUsers:
    user_repository: BaseUserRepository

    async def __call__(self) -> list[User]:
        result = await self.user_repository.get_all()
        return result


@dataclass
class GetAllSubscribedUsers:
    user_repository: BaseUserRepository

    async def __call__(self) -> list[User]:
        result = await self.user_repository.get_all_subscribed()
        return result


@dataclass
class GetUserByTelegramId:
    user_repository: BaseUserRepository
    transaction_manager: BaseTransactionManager
    logger: Logger

    async def __call__(self, user_id: int, username: str = "") -> User | None:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            user = User.create(telegram_id=user_id, username=username)
            try:
                await self.user_repository.create(user)
                await self.transaction_manager.commit()
            except Exception as e:
                self.logger.error("usecase: GetUserByTelegramId error: {0}".format(e))
                return None
        return user


@dataclass
class GetAllAdmins:
    user_repository: BaseUserRepository

    async def __call__(self) -> str:
        users_list = await self.user_repository.get_all()
        admins = [user for user in users_list if user.role == "admin"]

        result = "Список администраторов:\n"
        if admins:
            for admin in admins:
                result += " - id: `{0}` username: {1}\n".format(
                    admin.telegram_id, admin.username
                )
        else:
            result = "Нет администраторов"
        return result
