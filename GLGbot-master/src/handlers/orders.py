from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import os

from src.utils.states import OrderCreationStates, OrderSearchStates
from src.utils.helpers import (
    format_order_info, 
    is_valid_weight, 
    get_status_emoji,
    save_document
)
from src.database.models import User, Order, Document
from src.database.crud import (
    get_user, 
    add_order, 
    add_document, 
    get_order, 
    update_order,
    get_available_orders,
    get_user_orders,
    get_order_documents
)
from src.keyboards.orders_kb import (
    get_create_order_keyboard, 
    get_cargo_type_keyboard, 
    get_cancel_keyboard,
    get_confirm_order_keyboard,
    get_document_keyboard,
    get_skip_keyboard,
    get_accept_order_keyboard,
    get_order_details_keyboard,
    get_orders_navigation_keyboard
)
from src.keyboards.main_kb import (
    get_main_keyboard, 
    get_confirmation_keyboard,
    get_cancel_keyboard
)
from src.config import config, logger


router = Router()
ORDERS_PER_PAGE = 5


@router.message(F.text == "📝 Создать заявку")
async def create_order_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)
    
    if not user:
        await message.answer(
            "❌ Для создания заявки необходимо зарегистрироваться.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    if user.role != "sender":
        await message.answer(
            "❌ Создавать заявки могут только отправители грузов.",
            reply_markup=get_main_keyboard(user.role)
        )
        return
    
    await message.answer(
        "📦 <b>Создание новой заявки на перевозку</b>\n\n"
        "Выберите тип груза:",
        reply_markup=get_cargo_type_keyboard()
    )
    
    await state.set_state(OrderCreationStates.waiting_for_cargo_type)


@router.message(OrderCreationStates.waiting_for_cargo_type)
async def process_cargo_type(message: Message, state: FSMContext):
    cargo_type = message.text
    
    valid_types = ["📦 Стандартный", "📏 Негабаритный", "🔶 Хрупкий", "🔒 Ценный"]
    
    if cargo_type not in valid_types:
        await message.answer(
            "❌ Пожалуйста, выберите тип груза из предложенных вариантов.",
            reply_markup=get_cargo_type_keyboard()
        )
        return
    
    cargo_type = cargo_type.split(" ")[1]
    await state.update_data(cargo_type=cargo_type)
    
    await message.answer(
        "⚖️ Укажите вес груза в килограммах (например, 10.5):",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(OrderCreationStates.waiting_for_weight)


@router.message(OrderCreationStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    weight_str = message.text
    
    if not is_valid_weight(weight_str):
        await message.answer(
            "❌ Пожалуйста, введите корректный вес в килограммах.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    weight = float(weight_str.replace(",", "."))
    await state.update_data(weight=weight)
    
    await message.answer(
        "📏 Укажите габариты груза в формате ДxШxВ в сантиметрах (например, 100x50x30).\n"
        "Или нажмите 'Пропустить', если не хотите указывать габариты.",
        reply_markup=get_skip_keyboard()
    )
    
    await state.set_state(OrderCreationStates.waiting_for_dimensions)


@router.message(OrderCreationStates.waiting_for_dimensions)
async def process_dimensions(message: Message, state: FSMContext):
    if message.text == "⏭️ Пропустить":
        dimensions = None
    else:
        dimensions = message.text
    
    await state.update_data(dimensions=dimensions)
    
    await message.answer(
        "📍 Укажите адрес загрузки:",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(OrderCreationStates.waiting_for_pickup_address)


@router.message(OrderCreationStates.waiting_for_pickup_address)
async def process_pickup_address(message: Message, state: FSMContext):
    pickup_address = message.text
    
    await state.update_data(pickup_address=pickup_address)
    
    await message.answer(
        "🏁 Укажите адрес доставки:",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(OrderCreationStates.waiting_for_delivery_address)


@router.message(OrderCreationStates.waiting_for_delivery_address)
async def process_delivery_address(message: Message, state: FSMContext):
    delivery_address = message.text
    
    await state.update_data(delivery_address=delivery_address)
    
    await message.answer(
        "📅 Укажите дату загрузки в формате ДД.ММ.ГГГГ или ДД.ММ.ГГГГ ЧЧ:ММ:",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(OrderCreationStates.waiting_for_pickup_date)


@router.message(OrderCreationStates.waiting_for_pickup_date)
async def process_pickup_date(message: Message, state: FSMContext):
    pickup_date = message.text
    
    await state.update_data(pickup_date=pickup_date)
    
    await message.answer(
        "💬 Укажите дополнительные комментарии или особые требования к перевозке.\n"
        "Или нажмите 'Пропустить', если комментариев нет.",
        reply_markup=get_skip_keyboard()
    )
    
    await state.set_state(OrderCreationStates.waiting_for_comment)


@router.message(OrderCreationStates.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    if message.text == "⏭️ Пропустить":
        comment = None
    else:
        comment = message.text
    
    await state.update_data(comment=comment)
    
    user_data = await state.get_data()
    dimensions_text = f"Габариты: {user_data.get('dimensions')}\n" if user_data.get('dimensions') else ""
    comment_text = f"Комментарий: {user_data.get('comment')}\n" if user_data.get('comment') else ""
    
    await message.answer(
        f"📦 <b>Проверьте данные заявки:</b>\n\n"
        f"Тип груза: {user_data['cargo_type']}\n"
        f"Вес: {user_data['weight']} кг\n"
        f"{dimensions_text}"
        f"Адрес загрузки: {user_data['pickup_address']}\n"
        f"Адрес доставки: {user_data['delivery_address']}\n"
        f"Дата загрузки: {user_data['pickup_date']}\n"
        f"{comment_text}\n"
        f"Всё верно?",
        reply_markup=get_confirmation_keyboard()
    )
    
    await state.set_state(OrderCreationStates.confirmation)


@router.callback_query(OrderCreationStates.confirmation, F.data == "confirm")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    
    order = Order(
        sender_id=callback.from_user.id,
        cargo_type=user_data["cargo_type"],
        weight=user_data["weight"],
        dimensions=user_data.get("dimensions"),
        pickup_address=user_data["pickup_address"],
        delivery_address=user_data["delivery_address"],
        pickup_date=user_data["pickup_date"],
        comment=user_data.get("comment")
    )
    
    order_id = await add_order(order)
    
    await callback.message.answer(
        f"✅ Заявка #{order_id} успешно создана!\n\n"
        f"Теперь вы можете добавить документы к заявке (фото груза, ТТН и т.д.) "
        f"или завершить создание заявки.",
        reply_markup=get_document_keyboard()
    )
    
    await state.update_data(order_id=order_id)
    await state.set_state(OrderCreationStates.waiting_for_documents)
    
    await callback.answer()


@router.callback_query(OrderCreationStates.confirmation, F.data == "cancel")
async def cancel_order_confirmation(callback: CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    
    await callback.message.answer(
        "❌ Создание заявки отменено. Вы можете начать заново или вернуться в главное меню.",
        reply_markup=get_main_keyboard(user.role)
    )
    
    await callback.answer()
    await state.clear()


@router.message(OrderCreationStates.waiting_for_documents, F.text == "📎 Добавить документ")
async def add_document_prompt(message: Message):
    await message.answer(
        "📎 Отправьте документ (фото или файл), который нужно прикрепить к заявке.",
        reply_markup=get_document_keyboard()
    )


@router.message(OrderCreationStates.waiting_for_documents, F.photo | F.document)
async def process_document(message: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    order_id = user_data["order_id"]
    
    if not os.path.exists(config.files_dir):
        os.makedirs(config.files_dir, exist_ok=True)
    
    if message.photo:
        file_id = message.photo[-1].file_id
        file_name = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_type = "photo"
    else:
        file_id = message.document.file_id
        file_name = message.document.file_name
        file_type = "document"
    
    file_path = await save_document(bot, file_id, order_id, file_name)
    
    document = Document(
        order_id=order_id,
        file_path=file_path,
        file_name=file_name,
        file_type=file_type
    )
    
    doc_id = await add_document(document)
    
    await message.answer(
        f"✅ Документ успешно добавлен к заявке #{order_id}.\n\n"
        f"Вы можете добавить еще документы или завершить создание заявки.",
        reply_markup=get_document_keyboard()
    )


@router.message(OrderCreationStates.waiting_for_documents, F.text == "✅ Завершить")
async def finish_order_creation(message: Message, state: FSMContext):
    user_data = await state.get_data()
    order_id = user_data["order_id"]
    user = await get_user(message.from_user.id)
    
    await message.answer(
        f"✅ Создание заявки #{order_id} завершено!\n\n"
        f"Перевозчики уже могут видеть вашу заявку и откликаться на нее. "
        f"Как только кто-то примет заказ, вы получите уведомление.",
        reply_markup=get_main_keyboard(user.role)
    )
    
    await state.clear()


@router.message(F.text == "🔍 Найти заказы")
async def find_orders(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)
    
    if not user:
        await message.answer(
            "❌ Для поиска заказов необходимо зарегистрироваться.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    if user.role != "carrier":
        await message.answer(
            "❌ Искать заказы могут только перевозчики.",
            reply_markup=get_main_keyboard(user.role)
        )
        return
    
    await show_available_orders(message, state, 1)


async def show_available_orders(message: Message, state: FSMContext, page: int = 1):
    available_orders = await get_available_orders()
    
    if not available_orders:
        await message.answer(
            "📭 На данный момент нет доступных заказов.\n"
            "Проверьте позже или подпишитесь на уведомления.",
            reply_markup=get_main_keyboard("carrier")
        )
        return
    
    start_idx = (page - 1) * ORDERS_PER_PAGE
    end_idx = start_idx + ORDERS_PER_PAGE
    page_orders = available_orders[start_idx:end_idx]
    
    total_pages = (len(available_orders) + ORDERS_PER_PAGE - 1) // ORDERS_PER_PAGE
    
    for order in page_orders:
        order_text = (
            f"🆕 <b>Заказ #{order.order_id}</b>\n\n"
            f"Тип груза: {order.cargo_type}\n"
            f"Вес: {order.weight} кг\n"
            f"Откуда: {order.pickup_address}\n"
            f"Куда: {order.delivery_address}\n"
            f"Дата загрузки: {order.pickup_date}"
        )
        
        await message.answer(
            order_text,
            reply_markup=get_accept_order_keyboard(order.order_id)
        )
    
    if total_pages > 1:
        await message.answer(
            f"Страница {page} из {total_pages}",
            reply_markup=get_orders_navigation_keyboard(page, total_pages)
        )


@router.callback_query(F.data.startswith("orders_page:"))
async def navigate_orders(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split(":")[1])
    await show_available_orders(callback.message, state, page)
    await callback.answer()


@router.callback_query(F.data.startswith("view_order:"))
async def view_order_details(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split(":")[1])
    user = await get_user(callback.from_user.id)
    
    order = await get_order(order_id)
    if not order:
        await callback.message.answer("❌ Заказ не найден.")
        await callback.answer()
        return
    
    dimensions_text = f"Габариты: {order.dimensions}\n" if order.dimensions else ""
    comment_text = f"Комментарий: {order.comment}\n" if order.comment else ""
    
    order_text = (
        f"📦 <b>Детали заказа #{order.order_id}</b>\n\n"
        f"Тип груза: {order.cargo_type}\n"
        f"Вес: {order.weight} кг\n"
        f"{dimensions_text}"
        f"Откуда: {order.pickup_address}\n"
        f"Куда: {order.delivery_address}\n"
        f"Дата загрузки: {order.pickup_date}\n"
        f"{comment_text}"
        f"Статус: {get_status_emoji(order.status)} {order.status}"
    )
    
    await callback.message.answer(
        order_text,
        reply_markup=get_order_details_keyboard(order.order_id, order.status, user.role)
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("accept_order:"))
async def accept_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    order_id = int(callback.data.split(":")[1])
    carrier_id = callback.from_user.id
    
    order = await get_order(order_id)
    if not order:
        await callback.message.answer("❌ Заказ не найден.")
        await callback.answer()
        return
    
    if order.status != "new":
        await callback.message.answer(
            "❌ Этот заказ уже принят другим перевозчиком."
        )
        await callback.answer()
        return
    
    carrier = await get_user(carrier_id)
    sender = await get_user(order.sender_id)
    
    order.carrier_id = carrier_id
    order.status = "accepted"
    await update_order(order)
    
    await callback.message.answer(
        f"✅ Вы успешно приняли заказ #{order.order_id}!\n\n"
        f"Теперь вы можете связаться с отправителем:\n"
        f"Имя: {sender.full_name}\n"
        f"Телефон: {sender.phone}\n"
        f"Email: {sender.email or 'Не указан'}"
    )
    
    try:
        await bot.send_message(
            order.sender_id,
            f"🎉 Ваш заказ #{order.order_id} был принят перевозчиком!\n\n"
            f"Данные перевозчика:\n"
            f"Имя: {carrier.full_name}\n"
            f"Телефон: {carrier.phone}\n"
            f"Email: {carrier.email or 'Не указан'}\n\n"
            f"Вы можете связаться с ним для уточнения деталей."
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление отправителю: {e}")
    
    await callback.answer()


@router.message(F.text == "📋 Мои заявки")
async def show_my_orders(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)
    
    if not user:
        await message.answer(
            "❌ Для просмотра заявок необходимо зарегистрироваться.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    orders = await get_user_orders(user_id, user.role)
    
    if not orders:
        role_text = "созданных заявок" if user.role == "sender" else "принятых заказов"
        await message.answer(
            f"📭 У вас пока нет {role_text}.",
            reply_markup=get_main_keyboard(user.role)
        )
        return
    
    await message.answer(
        f"📋 <b>Ваши {'заявки' if user.role == 'sender' else 'заказы'}:</b>"
    )
    
    for order in orders:
        status_emoji = get_status_emoji(order.status)
        status_text = {
            "new": "Новая",
            "accepted": "Принята",
            "in_progress": "В пути",
            "completed": "Завершена",
            "cancelled": "Отменена"
        }.get(order.status, order.status)
        
        order_text = format_order_info(
            order.order_id, 
            order.cargo_type, 
            order.weight, 
            order.pickup_address, 
            order.delivery_address, 
            order.pickup_date,
            order.dimensions,
            f"{status_emoji} {status_text}"
        )
        
        await message.answer(
            order_text,
            reply_markup=get_order_details_keyboard(order.order_id, order.status, user.role)
        )


@router.callback_query(F.data.startswith("mark_delivered:"))
async def mark_delivered(callback: CallbackQuery, state: FSMContext, bot: Bot):
    order_id = int(callback.data.split(":")[1])
    
    order = await get_order(order_id)
    if not order:
        await callback.message.answer("❌ Заказ не найден.")
        await callback.answer()
        return
    
    if order.status != "accepted":
        await callback.message.answer("❌ Невозможно отметить заказ как доставленный.")
        await callback.answer()
        return
    
    order.status = "delivered"
    await update_order(order)
    
    await callback.message.answer(
        f"✅ Заказ #{order.order_id} отмечен как доставленный.\n"
        f"Ожидаем подтверждения от отправителя."
    )
    
    try:
        await bot.send_message(
            order.sender_id,
            f"🚚 Перевозчик отметил заказ #{order.order_id} как доставленный.\n"
            f"Пожалуйста, подтвердите получение груза."
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление отправителю: {e}")
    
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delivery:"))
async def confirm_delivery(callback: CallbackQuery, state: FSMContext, bot: Bot):
    order_id = int(callback.data.split(":")[1])
    
    order = await get_order(order_id)
    if not order:
        await callback.message.answer("❌ Заказ не найден.")
        await callback.answer()
        return
    
    if order.status != "delivered":
        await callback.message.answer("❌ Невозможно подтвердить получение.")
        await callback.answer()
        return
    
    order.status = "completed"
    await update_order(order)
    
    await callback.message.answer(
        f"✅ Доставка заказа #{order.order_id} подтверждена.\n"
        f"Заказ успешно завершен!"
    )
    
    try:
        await bot.send_message(
            order.carrier_id,
            f"🎉 Отправитель подтвердил получение заказа #{order.order_id}.\n"
            f"Заказ успешно завершен!"
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление перевозчику: {e}")
    
    await callback.answer()


@router.callback_query(F.data.startswith("view_documents:"))
async def view_documents(callback: CallbackQuery, state: FSMContext, bot: Bot):
    order_id = int(callback.data.split(":")[1])
    
    documents = await get_order_documents(order_id)
    
    if not documents:
        await callback.message.answer(
            f"📎 К заказу #{order_id} не прикреплено документов."
        )
        await callback.answer()
        return
    
    await callback.message.answer(
        f"📎 Документы к заказу #{order_id}:"
    )
    
    for doc in documents:
        try:
            file_path = doc.file_path
            if doc.file_type == "photo":
                await bot.send_photo(
                    callback.from_user.id,
                    FSInputFile(file_path),
                    caption=f"Документ: {doc.file_name}"
                )
            else:
                await bot.send_document(
                    callback.from_user.id,
                    FSInputFile(file_path),
                    caption=f"Документ: {doc.file_name}"
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке документа: {e}")
            await callback.message.answer(
                f"❌ Ошибка при загрузке документа {doc.file_name}"
            )
    
    await callback.answer()
