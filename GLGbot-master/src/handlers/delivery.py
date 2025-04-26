# src/handlers/delivery.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from src.database.crud import update_order_status
from src.utils.states import DeliveryStates

router = Router()

@router.callback_query(F.data.startswith("stage:"))
async def handle_delivery_stage(callback: CallbackQuery):
    data_parts = callback.data.split(":")
    stage = data_parts[1]
    order_id = int(data_parts[2])

    stage_mapping = {
        "loading": "Погрузка началась 🏗",
        "on_way": "Груз в пути 🚚",
        "waiting": "Ожидает разгрузки ⏳",
        "completed": "Перевозка завершена ✅"
    }

    status_text = stage_mapping.get(stage)

    if not status_text:
        await callback.answer("Неизвестный этап!", show_alert=True)
        return

    # Обновляем статус заказа в БД
    await update_order_status(order_id, stage)

    await callback.message.answer(
        f"Статус заказа #{order_id} обновлён:\n{status_text}"
    )

    await callback.answer("Статус обновлён ✅")
