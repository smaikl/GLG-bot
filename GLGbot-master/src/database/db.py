import os
import sqlite3
import aiosqlite
from src.config import config, logger


DB_PATH = os.path.join(config.db.db_path, config.db.db_name)


async def init_db():
    os.makedirs(config.db.db_path, exist_ok=True)
    
    conn = await aiosqlite.connect(DB_PATH)
    try:
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            company TEXT,
            role TEXT NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            carrier_id INTEGER,
            cargo_type TEXT NOT NULL,
            weight REAL NOT NULL,
            dimensions TEXT,
            pickup_address TEXT NOT NULL,
            delivery_address TEXT NOT NULL,
            pickup_date TEXT NOT NULL,
            comment TEXT,
            status TEXT NOT NULL DEFAULT 'new',
            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (user_id),
            FOREIGN KEY (carrier_id) REFERENCES users (user_id)
        )
        ''')
        
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders (order_id)
        )
        ''')
        
        await conn.commit()
    finally:
        await conn.close()
    
    logger.info("База данных инициализирована")


async def get_db_connection():
    return await aiosqlite.connect(DB_PATH)
