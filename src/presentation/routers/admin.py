from aiogram import Bot, F, Router, filters, types
from aiogram.fsm.context import FSMContext
from dishka import AsyncContainer

from application.usecases.users.get_user import GetAllAdmins
from application.usecases.users.update_user import DemoteUser, PromoteUserToAdmin
from domain.common.response import Response
from presentation.common.keyboards import kb
from presentation.common.texts import text
from presentation.middlewares.admin import AdminMiddleware

admin_router = Router()
admin_router.message.middleware(AdminMiddleware())


@admin_router.message(filters.Command("info"))
async def cmd_info(message: types.Message):
    await message.answer(Response(text.info).value)


@admin_router.message(filters.Command("admins"))
async def cmd_admins(message: types.Message, container: AsyncContainer):
    async with container() as di_container:
        get_admins_interactor = await di_container.get(GetAllAdmins)
        result = await get_admins_interactor()
        await message.answer(Response(result).value)


@admin_router.message(filters.Command("promote_user"))
async def cmd_promote_user(
    message: types.Message,
    container: AsyncContainer,
    command: filters.command.CommandObject,
):
    async with container() as di_container:
        user_id = command.args
        if not user_id:
            await message.answer("Укажите id пользователя через пробел после команды")
        promote_user_interactor = await di_container.get(PromoteUserToAdmin)
        result = await promote_user_interactor(int(user_id.split()[0]))
        await message.answer(result)


@admin_router.message(filters.Command("demote_user"))
async def cmd_demote_user(
    message: types.Message,
    container: AsyncContainer,
    command: filters.command.CommandObject,
):
    async with container() as di_container:
        demote_user_interactor = await di_container.get(DemoteUser)
        result = await demote_user_interactor(command.args)
        await message.answer(result)
