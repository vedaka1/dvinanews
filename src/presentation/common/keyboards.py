from aiogram import types

from domain.users.user import User


class Keyboards:

    def request_access_keyboard(self, from_user: int):
        buttons = [
            [
                types.InlineKeyboardButton(
                    text="Принять", callback_data=f"requestAccess_accept_{from_user}"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="Отказать", callback_data=f"requestAccess_reject_{from_user}"
                )
            ],
        ]
        return buttons

    def newsletter_keyboard(self, user: User):
        buttons = []

        if user.is_subscribed:
            buttons.append(
                [
                    types.InlineKeyboardButton(
                        text="Отписаться",
                        callback_data=f"newsletter_unsubscribe",
                    )
                ]
            )
        else:
            buttons.append(
                [
                    types.InlineKeyboardButton(
                        text="Подписаться",
                        callback_data=f"newsletter_subscribe",
                    )
                ]
            )
        return buttons

    @property
    def image_keyboard(self):
        buttons = [
            [
                types.InlineKeyboardButton(text="Да", callback_data="image_yes"),
                types.InlineKeyboardButton(text="Нет", callback_data="image_no"),
            ]
        ]
        return buttons

    @property
    def send_announcement_keyboard(self):
        buttons = [
            [
                types.InlineKeyboardButton(text="Отправить", callback_data="send_yes"),
                types.InlineKeyboardButton(text="Отменить", callback_data="send_no"),
            ]
        ]
        return buttons


kb = Keyboards()
