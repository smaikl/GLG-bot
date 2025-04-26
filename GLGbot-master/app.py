import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from src.config import config, logger
from src.database.db import init_db

async def main():
    logger.info("Запуск бота для грузоперевозок")

    storage = MemoryStorage()
    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=storage)

    from src.handlers import register_all_handlers
    register_all_handlers(dp, bot)  # <-- ПЕРЕДАЁМ bot сюда

    from src.middlewares import register_all_middlewares
    register_all_middlewares(dp)

    await init_db()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}", exc_info=True)
        sys.exit(1)
