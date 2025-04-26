from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from src.config import logger
from src.database.crud import get_user
from src.keyboards.main_kb import (
    get_start_keyboard,
    get_main_keyboard,
)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id
    user = await get_user(user_id)

    if user:
        text = (
            f"👋 Добро пожаловать обратно, {user.full_name}!\n\n"
            "Я бот для организации грузоперевозок. "
            "Вы можете создавать заявки или брать заказы на исполнение.\n\n"
            "Используйте кнопки ниже для навигации."
        )
        keyboard = get_main_keyboard(user.role)
    else:
        text = (
            f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
            "Я бот для организации грузоперевозок.\n"
            "Для начала работы необходимо пройти регистрацию."
        )
        keyboard = get_start_keyboard()

    await message.answer(text, reply_markup=keyboard)


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Информация")
async def cmd_help(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    text = (
        "🤖 <b>Бот для грузоперевозок</b>\n\n"
        "Вы можете:\n"
        "• Создавать заявки на перевозку (отправители)\n"
        "• Принимать заказы (перевозчики)\n"
        "• Управлять своими заявками\n"
        "• Обмениваться контактами\n\n"
        "<b>Основные команды:</b>\n"
        "/start - Начать\n"
        "/help - Справка\n"
    )

    keyboard = get_main_keyboard(user.role) if user else get_start_keyboard()
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()

    user_id = message.from_user.id
    user = await get_user(user_id)

    keyboard = get_main_keyboard(user.role) if user else get_start_keyboard()
    await message.answer("❌ Действие отменено. Выберите дальнейшее действие:", reply_markup=keyboard)


@router.message(F.text == "◀️ Назад")
async def back_handler(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id
    user = await get_user(user_id)

    keyboard = get_main_keyboard(user.role) if user else get_start_keyboard()
    await message.answer("Вы вернулись в главное меню. Выберите действие:", reply_markup=keyboard)


@router.message(F.text == "🧑‍💼 Личный кабинет")
async def personal_account(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        await message.answer(
            "Для доступа к личному кабинету необходимо зарегистрироваться.",
            reply_markup=get_start_keyboard()
        )
        return

    role_text = "Отправитель" if user.role == "sender" else "Перевозчик"

    profile_info = (
        f"👤 <b>Личный кабинет</b>\n\n"
        f"🆔 ID: <code>{user.user_id}</code>\n"
        f"👤 Имя: {user.full_name}\n"
        f"📱 Телефон: {user.phone}\n"
        f"✉️ Email: {user.email or 'Не указан'}\n"
        f"🏢 Компания: {user.company or 'Не указана'}\n"
        f"🔖 Роль: {role_text}\n"
        f"📅 Регистрация: {user.registration_date[:10] if user.registration_date else 'Не указана'}\n\n"
        "Выберите дальнейшее действие:"
    )

    await message.answer(profile_info, reply_markup=get_main_keyboard(user.role))
