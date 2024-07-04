import os
import pickle
from datetime import datetime
from logging import getLogger

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramNotFound
from dishka import AsyncContainer

from application.usecases.commands.get_news import GetNews
from application.usecases.users.get_user import GetAllSubscribedUsers
from domain.common.news import News
from domain.common.response import Link, Response

logger = getLogger()


async def send_news_task(bot: Bot, container: AsyncContainer) -> None:
    async with container() as di_container:
        if not os.path.exists("./infrastructure/tasks/last_post_date.pkl"):
            with open("./infrastructure/tasks/last_post_date.pkl", "wb") as file:
                pickle.dump(datetime(2024, 1, 1, 9, 0, 0), file)
        get_news_interactor = await di_container.get(GetNews)
        get_users_interactor = await di_container.get(GetAllSubscribedUsers)
        news = await get_news_interactor()
        users = await get_users_interactor()
        latest_news: News = news[0]
        last_recorded_date: datetime = None
        with open("./infrastructure/tasks/last_post_date.pkl", "rb") as file:
            last_recorded_date = pickle.load(file)
        if latest_news.posted_at > last_recorded_date:
            with open("./infrastructure/tasks/last_post_date.pkl", "wb") as file:
                pickle.dump(latest_news.posted_at, file)
            if not users:
                return
            text = "На сайте появилась новая новость:\n{0}\n[{1}]({2})".format(
                latest_news.posted_at.strftime("%H:%M"),
                Response(latest_news.title).value,
                Link(latest_news.link).value,
            )
            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=text,
                    )
                except (TelegramNotFound, TelegramForbiddenError):
                    pass
