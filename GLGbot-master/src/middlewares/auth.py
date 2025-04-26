from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.dispatcher.flags import get_flag

from src.database.crud import get_user
from src.config import logger


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        need_auth = get_flag(data, "auth")
        
        if need_auth is None or need_auth is False:
            return await handler(event, data)
        
        user_id = event.from_user.id
        
        user = await get_user(user_id)
        data["user"] = user
        
        return await handler(event, data)
