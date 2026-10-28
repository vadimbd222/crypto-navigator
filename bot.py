import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import BOT_TOKEN, PROXY_URL
from models.db import init_db
from handlers import convert, learn, news, price, rating, settings, start

# Меню команд (синяя кнопка меню слева от поля ввода)
COMMANDS_MENU = [
    BotCommand(command="start", description="Приветствие и мой XP"),
    BotCommand(command="help", description="Список команд"),
    BotCommand(command="price", description="Курс монеты"),
    BotCommand(command="convert", description="Конвертер валют"),
    BotCommand(command="news", description="Свежие новости"),
    BotCommand(command="learn", description="Обучающие карточки"),
    BotCommand(command="top", description="Таблица лидеров"),
    BotCommand(command="settings", description="Настройки и профиль"),
]


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    await init_db()
    logging.info("База данных готова")

    if PROXY_URL:
        session = AiohttpSession(proxy=PROXY_URL)
        logging.info("Работаю через прокси")
    else:
        session = AiohttpSession()
        logging.info("Прокси не задан, работаю напрямую")

    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await bot.set_my_commands(COMMANDS_MENU)
    logging.info("Меню команд обновлено")

    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(price.router)
    dp.include_router(convert.router)
    dp.include_router(news.router)
    dp.include_router(learn.router)
    dp.include_router(rating.router)
    dp.include_router(settings.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())