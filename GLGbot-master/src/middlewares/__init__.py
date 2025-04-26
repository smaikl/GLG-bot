from aiogram import Dispatcher

from src.middlewares.auth import AuthMiddleware


def register_all_middlewares(dp: Dispatcher):
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
