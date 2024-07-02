import uuid

from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.persistence.models.base import Base


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True)
    telegram_id: Mapped[str] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str]
    is_subscribed: Mapped[bool]
