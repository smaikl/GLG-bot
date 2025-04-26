from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.utils.states import RegistrationStates
from src.utils.helpers import is_valid_phone, is_valid_email
from src.database.models import User
from src.database.crud import add_user, get_user
from src.keyboards.registration_kb import get_role_keyboard, get_skip_keyboard, get_phone_keyboard
from src.keyboards.main_kb import get_main_keyboard, get_confirmation_keyboard

router = Router()

@router.message(F.text == "🚀 Зарегистрироваться")
async def registration_start(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id
    existing_user = await get_user(user_id)

    if existing_user:
        await message.answer(
            f"Вы уже зарегистрированы как {existing_user.role}.\n"
            "Используйте кнопки для навигации по боту.",
            reply_markup=get_main_keyboard(existing_user.role)
        )
        return

    await message.answer(
        "👤 Начинаем регистрацию!\n\n"
        "Для начала выберите вашу роль:",
        reply_markup=get_role_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_role)


@router.message(RegistrationStates.waiting_for_role)
async def process_role(message: Message, state: FSMContext):
    role_text = message.text

    if role_text == "📦 Я отправитель":
        role = "sender"
    elif role_text == "🚚 Я перевозчик":
        role = "carrier"
    else:
        await message.answer(
            "❌ Пожалуйста, выберите роль через кнопки ниже.",
            reply_markup=get_role_keyboard()
        )
        return

    await state.update_data(role=role)

    await message.answer(
        "👤 Укажите ваше имя и фамилию:",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_name)


@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    if message.text == "⏭️ Пропустить":
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"
    else:
        full_name = message.text

    await state.update_data(full_name=full_name)

    await message.answer(
        "📱 Укажите ваш номер телефона для связи.\n"
        "Отправьте контакт кнопкой или введите вручную в формате +XXXXXXXXXXX.",
        reply_markup=get_phone_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_phone)


@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def process_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number

    await state.update_data(phone=phone)
    await ask_for_email(message, state)


@router.message(RegistrationStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()

    if not is_valid_phone(phone):
        await message.answer(
            "❌ Неверный номер телефона. Введите корректный номер или отправьте контакт.",
            reply_markup=get_phone_keyboard()
        )
        return

    await state.update_data(phone=phone)
    await ask_for_email(message, state)


async def ask_for_email(message: Message, state: FSMContext):
    await message.answer(
        "📧 Укажите ваш email (опционально). Вы можете пропустить этот шаг.",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_email)


@router.message(RegistrationStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    if message.text == "⏭️ Пропустить":
        email = None
    else:
        email = message.text.strip()
        if not is_valid_email(email):
            await message.answer(
                "❌ Неверный формат email. Введите корректный email или пропустите.",
                reply_markup=get_skip_keyboard()
            )
            return

    await state.update_data(email=email)

    await message.answer(
        "🏢 Укажите название вашей компании (опционально):",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_company)


@router.message(RegistrationStates.waiting_for_company)
async def process_company(message: Message, state: FSMContext):
    company = None if message.text == "⏭️ Пропустить" else message.text.strip()
    await state.update_data(company=company)

    user_data = await state.get_data()

    role_text = "Отправитель" if user_data["role"] == "sender" else "Перевозчик"
    email_text = user_data.get("email") or "Не указан"
    company_text = user_data.get("company") or "Не указана"

    await message.answer(
        f"👤 <b>Проверьте введенные данные:</b>\n\n"
        f"Роль: {role_text}\n"
        f"ФИО: {user_data['full_name']}\n"
        f"Телефон: {user_data['phone']}\n"
        f"Email: {email_text}\n"
        f"Компания: {company_text}\n\n"
        "Всё верно?",
        reply_markup=get_confirmation_keyboard()
    )
    await state.set_state(RegistrationStates.confirmation)


@router.callback_query(RegistrationStates.confirmation, F.data == "confirm")
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()

    user = User(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=user_data["full_name"],
        phone=user_data["phone"],
        email=user_data.get("email"),
        company=user_data.get("company"),
        role=user_data["role"]
    )

    await add_user(user)

    role_text = "отправителя" if user.role == "sender" else "перевозчика"

    await callback.message.answer(
        f"✅ Поздравляем! Вы зарегистрированы как {role_text}.\n\n"
        "Теперь вы можете пользоваться ботом.",
        reply_markup=get_main_keyboard(user.role)
    )

    await callback.answer()
    await state.clear()


@router.callback_query(RegistrationStates.confirmation, F.data == "cancel")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "❌ Регистрация отменена. Начните заново, выбрав роль:",
        reply_markup=get_role_keyboard()
    )
    await callback.answer()
    await state.set_state(RegistrationStates.waiting_for_role)
