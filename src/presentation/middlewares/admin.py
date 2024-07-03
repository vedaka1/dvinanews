from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from application.usecases.users.get_user import GetUserByTelegramId
from domain.common.response import Response
from domain.common.role import Roles
from infrastructure.config import settings
from infrastructure.di.container import get_container
from presentation.common.texts import text


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User = data["event_from_user"]
        container = get_container()
        if user.id == settings.HEAD_ADMIN_TG_ID:
            return await handler(event, data)
        async with container() as di_container:
            get_user = await di_container.get(GetUserByTelegramId)
            db_user = await get_user(user.id, user.username)
            if db_user.role != Roles.ADMIN.value:
                return await event.answer(Response(text.permission_denied).value)
        return await handler(event, data)
