from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_keyboard(user_role: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()

    kb.add(KeyboardButton(text="🧑‍💼 Личный кабинет"))

    if user_role == "sender":
        kb.add(KeyboardButton(text="📝 Создать заявку"))
    else:
        kb.add(KeyboardButton(text="🔍 Найти заказы"))

    kb.add(KeyboardButton(text="📋 Мои заявки"))
    kb.add(KeyboardButton(text="✏️ Редактировать профиль"))  # ← добавляем сюда
    kb.add(KeyboardButton(text="ℹ️ Информация"))

    return kb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие"
    )



def get_start_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="🚀 Зарегистрироваться"))
    kb.add(KeyboardButton(text="ℹ️ Информация"))

    return kb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Начать работу"
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="❌ Отмена"))

    return kb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Вы можете отменить действие"
    )


def get_back_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="◀️ Назад"))

    return kb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Вернуться назад"
    )


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"))
    kb.add(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel"))

    return kb.as_markup()


def get_order_actions_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="📄 Детали", callback_data="order_details"))
    kb.add(InlineKeyboardButton(text="📎 Документы", callback_data="order_documents"))

    return kb.as_markup()
