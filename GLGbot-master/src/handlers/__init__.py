from aiogram import Dispatcher, Bot


from src.handlers.start import router as start_router
from src.handlers.registration import router as registration_router
from src.handlers.orders import router as orders_router
from src.handlers.documents import router as documents_router
from src.handlers import edit_profile
from src.handlers.delivery import router as delivery_router

def register_all_handlers(dp: Dispatcher, bot: Bot):
    dp.include_router(start_router)
    dp.include_router(registration_router)
    dp.include_router(orders_router)
    dp.include_router(documents_router)
    dp.include_router(edit_profile.router)
    dp.include_router(delivery_router)  