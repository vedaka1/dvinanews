from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from domain.users.repository import BaseUserRepository
from domain.users.user import User


@dataclass
class UserRepository(BaseUserRepository):

    __slots__ = ("session",)
    session: AsyncSession

    async def create(self, user: User) -> None:
        query = text(
            """
                INSERT INTO users (id, telegram_id, username, role, is_subscribed)
                VALUES (:id, :telegram_id, :username, :role, :is_subscribed)
            """
        )
        await self.session.execute(
            query,
            {
                "id": user.id,
                "telegram_id": str(user.telegram_id),
                "username": user.username,
                "role": user.role,
                "is_subscribed": user.is_subscribed,
            },
        )
        return None

    async def delete(self, telegram_id: int) -> None:
        query = text(
            """
                DELETE FROM users
                WHERE telegram_id = :value;
                """
        )
        await self.session.execute(
            query,
            {
                "value": str(telegram_id),
            },
        )
        return None

    async def get_by_id(self, telegram_id: int) -> User | None:
        query = text("""SELECT * FROM users WHERE telegram_id = :value;""")
        result = await self.session.execute(query, {"value": str(telegram_id)})
        result = result.mappings().one_or_none()
        if result is None:
            return None

        return User(**result)

    async def get_admin_by_id(self, telegram_id: int) -> User | None:
        query = text(
            """SELECT * FROM users WHERE telegram_id = :value and role = 'admin';"""
        )
        result = await self.session.execute(query, {"value": str(telegram_id)})
        result = result.mappings().one_or_none()
        if result is None:
            return None

        return User(**result)

    async def get_all(self, limit: int = 10, offset: int = 0) -> list[User]:
        query = text("""SELECT * FROM users LIMIT :limit OFFSET :offset;""")
        result = await self.session.execute(query, {"limit": limit, "offset": offset})
        result = result.mappings().all()
        return [User(**data) for data in result]

    async def get_all_subscribed(self) -> list[User]:
        query = text("""SELECT * FROM users WHERE users.is_subscribed = true;""")
        result = await self.session.execute(query)
        result = result.mappings().all()
        return [User(**data) for data in result]

    async def update(self, user: User) -> None:
        query = text(
            """
                UPDATE users
                SET role = :role, is_subscribed = :is_subscribed
                WHERE telegram_id = :telegram_id;
            """
        )
        await self.session.execute(
            query,
            {
                "telegram_id": str(user.telegram_id),
                "role": user.role,
                "is_subscribed": user.is_subscribed,
            },
        )
        return None
