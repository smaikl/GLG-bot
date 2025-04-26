import os
import re
from datetime import datetime
from typing import Optional

from aiogram import Bot

from src.config import config, logger


def format_order_info(
    order_id: int,
    cargo_type: str,
    weight: float,
    pickup_address: str,
    delivery_address: str,
    pickup_date: str,
    dimensions: Optional[str] = None,
    status: str = "Новая"
) -> str:
    dimensions_str = f"Габариты: {dimensions}\n" if dimensions else ""

    return (
        f"📦 <b>Заказ #{order_id}</b>\n\n"
        f"Тип груза: {cargo_type}\n"
        f"Вес: {weight} кг\n"
        f"{dimensions_str}"
        f"Откуда: {pickup_address}\n"
        f"Куда: {delivery_address}\n"
        f"Дата загрузки: {pickup_date}\n"
        f"Статус: {status}"
    )


def get_status_emoji(status: str) -> str:
    statuses = {
        "new": "🆕",
        "accepted": "✅",
        "in_progress": "🚚",
        "completed": "🏁",
        "cancelled": "❌"
    }
    return statuses.get(status, "❓")


def get_role_text(role: str) -> str:
    return "Отправитель" if role == "sender" else "Перевозчик"


async def save_document(bot: Bot, file_id: str, order_id: int, file_name: str) -> str:
    file_info = await bot.get_file(file_id)
    file_path_bot = file_info.file_path

    file_extension = os.path.splitext(file_path_bot)[1]
    if not file_extension:
        file_extension = ".unknown"

    directory = os.path.join(config.files_dir, str(order_id))
    os.makedirs(directory, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{timestamp}_{file_name}{file_extension}"
    file_path = os.path.join(directory, new_filename)

    await bot.download(file_id, destination=file_path)

    logger.info(f"Файл сохранён: {file_path}")
    return file_path


def normalize_phone(phone: str) -> str:
    """Нормализует телефон: удаляет лишние символы, приводит к формату +XXXXXXXXXXX"""
    phone = re.sub(r"[^\d+]", "", phone)  # Убираем всё кроме цифр и +
    if not phone.startswith("+"):
        phone = "+" + phone
    return phone


def is_valid_phone(phone: str) -> bool:
    pattern = r'^\+[0-9]{10,15}$'  # Только с плюсом в начале
    return bool(re.match(pattern, phone))


def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))


def is_valid_weight(weight_str: str) -> bool:
    try:
        weight = float(weight_str.replace(",", "."))
        return weight > 0
    except ValueError:
        return False
