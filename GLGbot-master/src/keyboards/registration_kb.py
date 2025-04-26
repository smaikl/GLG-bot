from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_role_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="📦 Я отправитель"))
    kb.add(KeyboardButton(text="🚚 Я перевозчик"))
    kb.add(KeyboardButton(text="❌ Отмена"))
    
    return kb.as_markup(resize_keyboard=True)


def get_skip_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="⏭️ Пропустить"))
    kb.add(KeyboardButton(text="❌ Отмена"))
    
    return kb.as_markup(resize_keyboard=True)


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="📱 Отправить телефон", request_contact=True))
    kb.add(KeyboardButton(text="❌ Отмена"))
    
    return kb.as_markup(resize_keyboard=True)
