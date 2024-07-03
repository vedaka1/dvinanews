import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from infrastructure.config import settings
from infrastructure.di.container import get_container, init_logger, init_smtp_server
from infrastructure.smtp.main import BaseSMTPServer
from infrastructure.tasks.main import set_scheduler_tasks
from presentation.routers.admin import admin_router
from presentation.routers.announcement import announcement_router
from presentation.routers.news import news_router


def init_routers(dp: Dispatcher):
    dp.include_router(admin_router)
    dp.include_router(news_router)
    dp.include_router(announcement_router)


async def main():
    init_logger()
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
    )
    dp = Dispatcher()
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    init_routers(dp)
    init_smtp_server()
    container = get_container()
    dp["container"] = container
    dp["users"] = []
    scheduler.start()
    set_scheduler_tasks(scheduler, bot, container)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
