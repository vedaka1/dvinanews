from typing import Any, Dict

from aiogram import Bot, F, Router, filters, types
from aiogram.exceptions import TelegramForbiddenError, TelegramNotFound
from aiogram.fsm.context import FSMContext
from dishka import AsyncContainer

from application.usecases.users.get_user import GetAllUsers
from presentation.common.keyboards import kb
from presentation.common.states import Announcement
from presentation.middlewares.admin import AdminMiddleware

announcement_router = Router()
announcement_router.message.middleware(AdminMiddleware())


@announcement_router.message(filters.Command("announcement"))
async def send_post(message: types.Message, state: FSMContext):
    await state.set_state(Announcement.text)
    await message.answer(
        "Введите текст обьявления",
    )


@announcement_router.message(Announcement.text)
async def process_text(message: types.Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    await state.set_state(Announcement.image)
    await message.answer(
        f"Нужна картинка?",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb.image_keyboard),
    )


@announcement_router.callback_query(
    Announcement.image, F.data.casefold() == "image_yes"
)
async def process_image_yes(callback: types.CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer("Отправьте картинку")


@announcement_router.callback_query(Announcement.image, F.data.casefold() == "image_no")
async def process_image_no(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot
) -> None:
    data = await state.get_data()
    await callback.message.delete()
    await callback.message.answer("Объявление будет выглядеть так:")
    await send_announcement_preview(message=callback.message, data=data)


@announcement_router.message(Announcement.image, F.photo)
async def process_add_image(
    message: types.Message, state: FSMContext, bot: Bot
) -> None:
    image_from_url = message.photo[-1].file_id
    data = await state.update_data(image=image_from_url)
    await message.answer("Объявление будет выглядеть так:")
    await send_announcement_preview(message=message, data=data)


async def send_announcement_preview(
    message: types.Message, data: Dict[str, Any]
) -> None:
    text = data["text"]
    image = data.get("image", "")
    if image:
        await message.answer_photo(
            image,
            caption=text,
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=kb.send_announcement_keyboard
            ),
        )
    else:
        await message.answer(
            text=text,
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=kb.send_announcement_keyboard
            ),
        )


@announcement_router.callback_query(F.data.casefold() == "send_yes")
async def process_send_announcement_yes(
    callback: types.CallbackQuery,
    state: FSMContext,
    bot: Bot,
    container: AsyncContainer,
) -> None:
    async with container() as di_container:
        get_subscribed_users_interactor = await di_container.get(GetAllUsers)
        users = await get_subscribed_users_interactor()
        data = await state.get_data()
        text = data["text"]
        image = data.get("image", "")
        await callback.message.delete()
        await callback.message.answer(
            f"Объявление отправлено {len(users)} пользователям"
        )
        await state.clear()
        if image:
            for user in users:
                try:
                    await bot.send_photo(
                        chat_id=user.telegram_id, photo=image, caption=text
                    )
                except (TelegramNotFound, TelegramForbiddenError):
                    pass
            return

        for user in users:
            try:
                await bot.send_message(chat_id=user.telegram_id, text=text)
            except (TelegramNotFound, TelegramForbiddenError):
                pass


@announcement_router.callback_query(F.data.casefold() == "send_no")
async def process_send_announcement_no(
    callback: types.CallbackQuery, state: FSMContext
) -> None:
    await cancel_handler(message=callback.message, state=state)


@announcement_router.message(filters.Command("cancel"))
@announcement_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer(
        "Отменено",
    )
