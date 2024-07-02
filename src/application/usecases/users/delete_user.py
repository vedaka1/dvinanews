from dataclasses import dataclass
from logging import Logger

from application.common.transaction import BaseTransactionManager
from domain.users.repository import BaseUserRepository


@dataclass
class DeleteUser:
    user_repository: BaseUserRepository
    transaction_manager: BaseTransactionManager
    logger: Logger

    async def __call__(self, user_id: int) -> None:
        try:
            await self.user_repository.delete(user_id)
        except Exception as e:
            self.logger.error("usecase: DeleteUser error: {0}".format(e))
            return None

        await self.transaction_manager.commit()
        return None
