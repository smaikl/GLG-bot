from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_delivery_action_keyboard(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text="🏗 Погрузка", callback_data=f"order_action_loading_{order_id}"))
    kb.add(InlineKeyboardButton(text="🚚 В пути", callback_data=f"order_action_in_transit_{order_id}"))
    kb.add(InlineKeyboardButton(text="⏳ Ожидание разгрузки", callback_data=f"order_action_waiting_unload_{order_id}"))
    kb.add(InlineKeyboardButton(text="✅ Завершено", callback_data=f"order_action_completed_{order_id}"))

    return kb.as_markup()

def get_cargo_type_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="📦 Стандартный"))
    kb.add(KeyboardButton(text="📏 Негабаритный"))
    kb.add(KeyboardButton(text="🔶 Хрупкий"))
    kb.add(KeyboardButton(text="🔒 Ценный"))
    kb.add(KeyboardButton(text="❌ Отмена"))
    
    return kb.as_markup(resize_keyboard=True)


def get_document_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="📎 Добавить документ"))
    kb.add(KeyboardButton(text="✅ Завершить"))
    kb.add(KeyboardButton(text="❌ Отмена"))
    
    return kb.as_markup(resize_keyboard=True)


def get_accept_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="✅ Принять заказ", 
        callback_data=f"accept_order:{order_id}"
    ))
    kb.add(InlineKeyboardButton(
        text="👁️ Подробнее", 
        callback_data=f"view_order:{order_id}"
    ))
    
    return kb.as_markup()


def get_order_details_keyboard(order_id: int, status: str, user_role: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    
    if status == "new" and user_role == "carrier":
        kb.add(InlineKeyboardButton(
            text="✅ Принять заказ", 
            callback_data=f"accept_order:{order_id}"
        ))
    
    if status == "accepted" and user_role == "carrier":
        kb.add(InlineKeyboardButton(
            text="🚚 Отметить как доставленный", 
            callback_data=f"mark_delivered:{order_id}"
        ))
    
    if status == "delivered" and user_role == "sender":
        kb.add(InlineKeyboardButton(
            text="🏁 Подтвердить получение", 
            callback_data=f"confirm_delivery:{order_id}"
        ))
    
    kb.add(InlineKeyboardButton(
        text="📎 Документы", 
        callback_data=f"view_documents:{order_id}"
    ))
    
    kb.add(InlineKeyboardButton(
        text="◀️ Назад", 
        callback_data="back_to_orders"
    ))
    
    return kb.as_markup()


def get_orders_navigation_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    
    if page > 1:
        kb.add(InlineKeyboardButton(
            text="◀️ Назад", 
            callback_data=f"orders_page:{page-1}"
        ))
    
    kb.add(InlineKeyboardButton(
        text=f"Страница {page}/{total_pages}", 
        callback_data="current_page"
    ))
    
    if page < total_pages:
        kb.add(InlineKeyboardButton(
            text="▶️ Вперед", 
            callback_data=f"orders_page:{page+1}"
        ))
    
    return kb.as_markup()


def get_skip_keyboard():
    """Возвращает клавиатуру с кнопкой 'Пропустить'"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⏩ Пропустить", callback_data="skip")
    builder.button(text="◀️ Назад", callback_data="back")
    builder.adjust(2)
    return builder.as_markup()


def get_create_order_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="📝 Создать заявку"))
    kb.add(KeyboardButton(text="❌ Отмена"))
    
    return kb.as_markup(resize_keyboard=True)


def get_confirm_order_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data="confirm_order")
    kb.button(text="❌ Отменить", callback_data="cancel_order")
    kb.adjust(2)
    
    return kb.as_markup()


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="❌ Отмена"))
    
    return kb.as_markup(resize_keyboard=True)
