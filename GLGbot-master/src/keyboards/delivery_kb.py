# src/keyboards/delivery_kb.py

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_delivery_stages_keyboard(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(text="🏗 Погрузка началась", callback_data=f"stage:loading:{order_id}"),
        InlineKeyboardButton(text="🚚 В пути", callback_data=f"stage:on_way:{order_id}")
    )
    kb.row(
        InlineKeyboardButton(text="⏳ Ожидание разгрузки", callback_data=f"stage:waiting:{order_id}"),
        InlineKeyboardButton(text="✅ Завершено", callback_data=f"stage:completed:{order_id}")
    )

    return kb.as_markup()
