from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import AsyncContainer

from .send_news import send_news_task

MINUTE = 10


def set_scheduler_tasks(
    scheduler: AsyncIOScheduler, bot: Bot, container: AsyncContainer
):
    scheduler.add_job(
        send_news_task,
        "cron",
        day_of_week="*",
        hour="8-23",
        minute=f"*/{MINUTE}",
        second="00",
        kwargs={"bot": bot, "container": container},
        id="send_news_task",
    )
