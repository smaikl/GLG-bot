from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class User:
    user_id: int
    full_name: str
    phone: str
    role: str
    username: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    registration_date: datetime = None


@dataclass
class Order:
    sender_id: int
    cargo_type: str
    weight: float
    pickup_address: str
    delivery_address: str
    pickup_date: str
    order_id: Optional[int] = None
    carrier_id: Optional[int] = None
    dimensions: Optional[str] = None
    comment: Optional[str] = None
    status: str = "new"
    creation_date: datetime = None


@dataclass
class Document:
    order_id: int
    file_path: str
    file_name: str
    file_type: str
    doc_id: Optional[int] = None
    upload_date: datetime = None
