import uuid
from dataclasses import dataclass

from domain.common.role import Roles


@dataclass
class User:
    id: uuid.UUID
    telegram_id: str
    username: str
    role: str
    is_subscribed: bool

    @staticmethod
    def create(
        telegram_id: str, username: str = "", role: str = Roles.USER.value
    ) -> "User":
        return User(
            id=uuid.uuid4(),
            telegram_id=telegram_id,
            username=username,
            is_subscribed=False,
            role=role,
        )
