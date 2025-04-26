from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import os

from src.config import config, logger
from src.database.crud import get_order_documents, get_order, get_user
from src.utils.helpers import save_document
from src.database.models import Document
from src.database.crud import add_document
from src.keyboards.main_kb import get_main_keyboard


router = Router()


async def upload_document_to_order(message: Message, order_id: int, bot: Bot):
    if not os.path.exists(config.files_dir):
        os.makedirs(config.files_dir, exist_ok=True)
    
    if message.photo:
        file_id = message.photo[-1].file_id
        file_name = f"photo_{message.message_id}"
        file_type = "photo"
    elif message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        file_type = "document"
    else:
        await message.answer("❌ Неподдерживаемый тип файла.")
        return None
    
    try:
        file_path = await save_document(bot, file_id, order_id, file_name)
        
        document = Document(
            order_id=order_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type
        )
        
        doc_id = await add_document(document)
        
        return doc_id
    except Exception as e:
        logger.error(f"Ошибка при сохранении документа: {e}")
        await message.answer("❌ Произошла ошибка при загрузке документа. Попробуйте позже.")
        return None


async def send_order_documents(chat_id: int, order_id: int, bot: Bot):
    documents = await get_order_documents(order_id)
    
    if not documents:
        await bot.send_message(
            chat_id,
            f"📎 К заказу #{order_id} не прикреплено документов."
        )
        return
    
    await bot.send_message(
        chat_id,
        f"📎 Документы к заказу #{order_id}:"
    )
    
    for doc in documents:
        try:
            file_path = doc.file_path
            if doc.file_type == "photo":
                await bot.send_photo(
                    chat_id,
                    FSInputFile(file_path),
                    caption=f"Документ: {doc.file_name}"
                )
            else:
                await bot.send_document(
                    chat_id,
                    FSInputFile(file_path),
                    caption=f"Документ: {doc.file_name}"
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке документа: {e}")
            await bot.send_message(
                chat_id,
                f"❌ Ошибка при загрузке документа {doc.file_name}"
            )
