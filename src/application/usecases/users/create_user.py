from dataclasses import dataclass
from logging import Logger

from application.common.transaction import BaseTransactionManager
from domain.users.repository import BaseUserRepository
from domain.users.user import User


@dataclass
class CreateUser:
    user_repository: BaseUserRepository
    transaction_manager: BaseTransactionManager
    logger: Logger

    async def __call__(self, user_id: int, username: str = "") -> User | str:
        user_exists = await self.user_repository.get_by_id(user_id)
        if user_exists:
            return "Данный пользователь уже существует"

        user = User.create(telegram_id=user_id, username=username)
        try:
            await self.user_repository.create(user)
        except Exception as e:
            self.logger.error("usecase: CreateUser error: {0}".format(e))
            return "Ошибка при создании пользователя"

        await self.transaction_manager.commit()
        return user
