from typing import List, Optional, Dict, Any, Union
import aiosqlite
from datetime import datetime
from sqlalchemy import update
from src.database.models import Order
from sqlalchemy import select

from src.database.db import get_db_connection
from src.database.models import User, Order, Document
from src.config import logger
from src.config import config



async def add_user(user: User) -> int:
    conn = await get_db_connection()
    try:
        cursor = await conn.execute(
            """
            INSERT INTO users (user_id, username, full_name, phone, email, company, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user.user_id, user.username, user.full_name, user.phone, user.email, user.company, user.role)
        )
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


async def get_user(user_id: int) -> Optional[User]:
    conn = await get_db_connection()
    try:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM users WHERE user_id = ?", 
            (user_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
            
        return User(
            user_id=row['user_id'],
            username=row['username'],
            full_name=row['full_name'],
            phone=row['phone'],
            email=row['email'],
            company=row['company'],
            role=row['role'],
            registration_date=row['registration_date']
        )
    finally:
        await conn.close()


async def update_user(user: User) -> bool:
    conn = await get_db_connection()
    try:
        await conn.execute(
            """
            UPDATE users
            SET username = ?, full_name = ?, phone = ?, email = ?, company = ?, role = ?
            WHERE user_id = ?
            """,
            (user.username, user.full_name, user.phone, user.email, user.company, user.role, user.user_id)
        )
        await conn.commit()
        return True
    finally:
        await conn.close()


async def add_order(order: Order) -> int:
    conn = await get_db_connection()
    try:
        cursor = await conn.execute(
            """
            INSERT INTO orders (sender_id, cargo_type, weight, dimensions, pickup_address, 
                              delivery_address, pickup_date, comment, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (order.sender_id, order.cargo_type, order.weight, order.dimensions, order.pickup_address,
             order.delivery_address, order.pickup_date, order.comment, order.status)
        )
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


async def get_order(order_id: int) -> Optional[Order]:
    conn = await get_db_connection()
    try:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM orders WHERE order_id = ?", 
            (order_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
            
        return Order(
            order_id=row['order_id'],
            sender_id=row['sender_id'],
            carrier_id=row['carrier_id'],
            cargo_type=row['cargo_type'],
            weight=row['weight'],
            dimensions=row['dimensions'],
            pickup_address=row['pickup_address'],
            delivery_address=row['delivery_address'],
            pickup_date=row['pickup_date'],
            comment=row['comment'],
            status=row['status'],
            creation_date=row['creation_date']
        )
    finally:
        await conn.close()


async def update_order(order: Order) -> bool:
    conn = await get_db_connection()
    try:
        await conn.execute(
            """
            UPDATE orders
            SET carrier_id = ?, cargo_type = ?, weight = ?, dimensions = ?, 
                pickup_address = ?, delivery_address = ?, pickup_date = ?, 
                comment = ?, status = ?
            WHERE order_id = ?
            """,
            (order.carrier_id, order.cargo_type, order.weight, order.dimensions,
             order.pickup_address, order.delivery_address, order.pickup_date,
             order.comment, order.status, order.order_id)
        )
        await conn.commit()
        return True
    finally:
        await conn.close()


async def get_available_orders() -> List[Order]:
    conn = await get_db_connection()
    try:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM orders WHERE status = 'new' ORDER BY creation_date DESC"
        )
        rows = await cursor.fetchall()
        
        return [
            Order(
                order_id=row['order_id'],
                sender_id=row['sender_id'],
                carrier_id=row['carrier_id'],
                cargo_type=row['cargo_type'],
                weight=row['weight'],
                dimensions=row['dimensions'],
                pickup_address=row['pickup_address'],
                delivery_address=row['delivery_address'],
                pickup_date=row['pickup_date'],
                comment=row['comment'],
                status=row['status'],
                creation_date=row['creation_date']
            ) for row in rows
        ]
    finally:
        await conn.close()


async def get_user_orders(user_id: int, role: str) -> List[Order]:
    conn = await get_db_connection()
    try:
        conn.row_factory = aiosqlite.Row
        
        if role == "sender":
            cursor = await conn.execute(
                "SELECT * FROM orders WHERE sender_id = ? ORDER BY creation_date DESC", 
                (user_id,)
            )
        else:
            cursor = await conn.execute(
                "SELECT * FROM orders WHERE carrier_id = ? ORDER BY creation_date DESC", 
                (user_id,)
            )
            
        rows = await cursor.fetchall()
        
        return [
            Order(
                order_id=row['order_id'],
                sender_id=row['sender_id'],
                carrier_id=row['carrier_id'],
                cargo_type=row['cargo_type'],
                weight=row['weight'],
                dimensions=row['dimensions'],
                pickup_address=row['pickup_address'],
                delivery_address=row['delivery_address'],
                pickup_date=row['pickup_date'],
                comment=row['comment'],
                status=row['status'],
                creation_date=row['creation_date']
            ) for row in rows
        ]
    finally:
        await conn.close()


async def add_document(document: Document) -> int:
    conn = await get_db_connection()
    try:
        cursor = await conn.execute(
            """
            INSERT INTO documents (order_id, file_path, file_name, file_type)
            VALUES (?, ?, ?, ?)
            """,
            (document.order_id, document.file_path, document.file_name, document.file_type)
        )
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


async def get_order_documents(order_id: int) -> List[Document]:
    conn = await get_db_connection()
    try:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM documents WHERE order_id = ?", 
            (order_id,)
        )
        rows = await cursor.fetchall()
        
        return [
            Document(
                doc_id=row['doc_id'],
                order_id=row['order_id'],
                file_path=row['file_path'],
                file_name=row['file_name'],
                file_type=row['file_type'],
                upload_date=row['upload_date']
            ) for row in rows
        ]
    finally:
        await conn.close()
        
async def update_user_field(user_id: int, field: str, value: str):
    db_path = "database/bot_database.sqlite"  # Путь к твоей базе
    query = f"UPDATE Users SET {field} = ? WHERE user_id = ?"

    async with aiosqlite.connect(db_path) as db:
        await db.execute(query, (value, user_id))
        await db.commit()
        


async def update_order_status(order_id: int, new_status: str):
    async with aiosqlite.connect("database/bot_database.sqlite") as db:
        await db.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (new_status, order_id)
        )
        await db.commit()



async def get_order_by_id(order_id: int):
    db_path = "database/bot_database.sqlite"
    query = "SELECT * FROM Orders WHERE id = ?"

    async with aiosqlite.connect(db_path) as db:
        async with db.execute(query, (order_id,)) as cursor:
            row = await cursor.fetchone()
            return row  # можно будет потом замапить в модель