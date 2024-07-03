from aiogram import Bot, F, Router, filters, types
from aiogram.fsm.context import FSMContext
from dishka import AsyncContainer

from application.usecases.commands.get_news import GetNews
from application.usecases.commands.send_message import SendMessage
from application.usecases.users.create_user import CreateUser
from application.usecases.users.get_user import GetUserByTelegramId
from application.usecases.users.update_user import (
    PromoteUserToAdmin,
    SubscribeUser,
    UnsubscribeUser,
)
from domain.common.response import Link, Response
from domain.common.role import Roles
from infrastructure.config import settings
from presentation.common.keyboards import kb
from presentation.common.texts import text

news_router = Router()


@news_router.message(filters.Command("start"))
async def cmd_start(
    message: types.Message,
    bot: Bot,
    container: AsyncContainer,
):
    async with container() as di_container:
        user_id = message.from_user.id
        username = message.from_user.username
        create_user_interactor = await di_container.get(CreateUser)
        await create_user_interactor(user_id, username)
        await message.answer(Response(text.start).value)


@news_router.message(filters.Command("news"))
async def cmd_news(
    message: types.Message,
    container: AsyncContainer,
):
    async with container() as di_container:
        get_news_interactor = await di_container.get(GetNews)
        news = await get_news_interactor()
        text = "Последние новости за сегодня:\n"
        for news_item in news:
            sep = "<-------->\n"
            text += "{0}\n[{1}]({2})\n{3}".format(
                news_item.posted_at.strftime("%H:%M"),
                Response(news_item.title).value,
                Link(news_item.link).value,
                Response(sep).value,
            )
        await message.answer(text)


@news_router.message(filters.Command("send"))
async def cmd_newsletter(
    message: types.Message,
    container: AsyncContainer,
):
    async with container() as di_container:
        username = message.from_user.username
        send_message = await di_container.get(SendMessage)
        result = send_message(content=username)
        await message.answer(Response(result).value)


@news_router.message(filters.Command("newsletter"))
async def cmd_newsletter(
    message: types.Message,
    container: AsyncContainer,
):
    async with container() as di_container:
        user_id = message.from_user.id
        username = message.from_user.username
        get_user_interactor = await di_container.get(GetUserByTelegramId)
        user = await get_user_interactor(user_id, username)
        if user.is_subscribed:
            text = "Вы подписаны на новостную рассылку"
        else:
            text = "Хотите подписаться на новостную расылку?"

        await message.answer(
            text,
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=kb.newsletter_keyboard(user)
            ),
        )


@news_router.callback_query(F.data.startswith("newsletter_"))
async def callback_newsletter(callback: types.CallbackQuery, container: AsyncContainer):
    async with container() as di_container:
        choices = {"subscribe": SubscribeUser, "unsubscribe": UnsubscribeUser}
        user_id = callback.from_user.id
        user_choice = callback.data.split("_")[1]
        newsletter_user_interactor = await di_container.get(choices[user_choice])
        result = await newsletter_user_interactor(user_id)
        await callback.message.edit_text(Response(result).value, reply_markup=None)


@news_router.message(filters.Command("request_access"))
async def cmd_request_access(
    message: types.Message,
    bot: Bot,
    state: FSMContext,
    container: AsyncContainer,
    users: list,
):
    async with container() as di_container:
        await state.clear()
        user_id = message.from_user.id
        username = message.from_user.username
        if user_id in users:
            return await message.answer("Вы уже отправили запрос")
        get_admin_interactor = await di_container.get(GetUserByTelegramId)
        user = await get_admin_interactor(user_id, username)
        if user.role == Roles.ADMIN.value:
            return await message.answer("У вас уже есть права администратора")
        await bot.send_message(
            chat_id=settings.HEAD_ADMIN_TG_ID,
            text=Response(text.request_access(user_id, username)).value,
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=kb.request_access_keyboard(user_id)
            ),
            parse_mode="MarkDownV2",
        )
        users.append(user_id)
        await message.answer("Запрос отправлен")


@news_router.callback_query(F.data.startswith("requestAccess_"))
async def callback_request_access(
    callback: types.CallbackQuery, bot: Bot, container: AsyncContainer, users: list
):
    async with container() as di_container:
        user_choice = callback.data.split("_")[1]
        from_user = int(callback.data.split("_")[2])
        if user_choice == "accept":
            request_access_callback_interactor = await di_container.get(
                PromoteUserToAdmin
            )
            result = await request_access_callback_interactor(from_user)
            await callback.message.answer(result)
            await bot.send_message(
                chat_id=from_user,
                text="Ваш запрос на права администратора был одобрен",
            )
        if user_choice == "reject":
            await bot.send_message(
                chat_id=from_user, text="Ваш запрос на права администратора отклонен"
            )
        users.remove(from_user)
        await callback.message.delete()
