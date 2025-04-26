from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


from src.database.crud import get_user, update_user_field
from src.keyboards.registration_kb import get_skip_keyboard
from src.keyboards.main_kb import get_main_keyboard
from src.utils.states import EditProfileStates
from src.utils.helpers import is_valid_phone, is_valid_email

router = Router()

FIELDS = {
    "Имя": "full_name",
    "Телефон": "phone",
    "Email": "email",
    "Компания": "company",
}

@router.message(F.text == "✏️ Редактировать профиль")
async def edit_profile_start(message: Message, state: FSMContext):
    buttons = [KeyboardButton(text=field) for field in FIELDS.keys()]
    kb = ReplyKeyboardMarkup(keyboard=[buttons], resize_keyboard=True, one_time_keyboard=False)

    await message.answer("Что хотите изменить?", reply_markup=kb)
    await state.set_state(EditProfileStates.choosing_field)


@router.message(EditProfileStates.choosing_field)
async def choose_field(message: Message, state: FSMContext):
    field_text = message.text
    field = FIELDS.get(field_text)

    if not field:
        await message.answer("Пожалуйста, выберите параметр для изменения через кнопки ниже.")
        return

    await state.update_data(field=field)
    await message.answer(f"Введите новое значение для {field_text}:", reply_markup=get_skip_keyboard())
    await state.set_state(EditProfileStates.entering_new_value)


@router.message(EditProfileStates.entering_new_value)
async def update_field(message: Message, state: FSMContext):
    user_data = await state.get_data()
    field = user_data["field"]
    new_value = message.text

    if new_value == "⏭️ Пропустить":
        await message.answer("Редактирование отменено.", reply_markup=get_main_keyboard("sender"))
        await state.clear()
        return

    # Валидация если нужно
    if field == "phone" and not is_valid_phone(new_value):
        await message.answer("❌ Введите корректный номер телефона в формате +XXXXXXXXXXX.")
        return
    if field == "email" and not is_valid_email(new_value):
        await message.answer("❌ Введите корректный email.")
        return

    user_id = message.from_user.id
    await update_user_field(user_id, field, new_value)

    await message.answer("✅ Данные успешно обновлены!", reply_markup=get_main_keyboard("sender"))
    await state.clear()
