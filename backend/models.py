from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import secrets

# ─────────────────────────────────────────────
# USER
# ─────────────────────────────────────────────
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    phone: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="diner")  # diner | merchant | waiter | admin
    avatar_url: Optional[str] = None
    wallet_balance: float = Field(default=500.0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    orders: List["Order"] = Relationship(back_populates="user")
    wallet_transactions: List["WalletTransaction"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")
    session_participants: List["SessionParticipant"] = Relationship(back_populates="user")

class UserCreate(SQLModel):
    name: str
    email: str
    phone: str
    password: str
    role: str = "diner"

class UserRead(SQLModel):
    id: int
    name: str
    email: str
    phone: str
    role: str
    avatar_url: Optional[str]
    wallet_balance: float
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(SQLModel):
    email: str
    password: str

# ─────────────────────────────────────────────
# RESTAURANT
# ─────────────────────────────────────────────
class Restaurant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: str
    phone: str
    cuisine_type: str
    rating: float = Field(default=0.0, ge=0, le=5)
    price_range: str = Field(default="₹300-800")
    description: str = Field(default="")
    image_url: Optional[str] = None
    is_active: bool = Field(default=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    menu_items: List["MenuItem"] = Relationship(back_populates="restaurant")
    orders: List["Order"] = Relationship(back_populates="restaurant")
    tables: List["Table"] = Relationship(back_populates="restaurant")
    dining_sessions: List["DiningSession"] = Relationship(back_populates="restaurant")

class RestaurantBase(SQLModel):
    name: str
    address: str
    phone: str
    cuisine_type: str
    rating: float = Field(default=0.0, ge=0, le=5)
    price_range: str = "₹300-800"
    description: str = ""
    image_url: Optional[str] = None
    is_active: bool = True

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantRead(RestaurantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ─────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────
class Table(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_id: int = Field(foreign_key="restaurant.id")
    number: str
    capacity: int = Field(default=4)
    status: str = Field(default="available")  # available | occupied | reserved | billing

    restaurant: Optional["Restaurant"] = Relationship(back_populates="tables")
    dining_sessions: List["DiningSession"] = Relationship(back_populates="table")

class TableRead(SQLModel):
    id: int
    restaurant_id: int
    number: str
    capacity: int
    status: str

    class Config:
        orm_mode = True

# ─────────────────────────────────────────────
# MENU ITEM
# ─────────────────────────────────────────────
class MenuItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    is_available: bool = Field(default=True)
    is_vegetarian: bool = Field(default=False)
    restaurant_id: int = Field(foreign_key="restaurant.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    restaurant: Optional["Restaurant"] = Relationship(back_populates="menu_items")
    order_items: List["OrderItem"] = Relationship(back_populates="menu_item")

class MenuItemBase(SQLModel):
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    is_available: bool = True
    is_vegetarian: bool = False

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemRead(MenuItemBase):
    id: int
    restaurant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ─────────────────────────────────────────────
# DINING SESSION
# ─────────────────────────────────────────────
class DiningSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_id: int = Field(foreign_key="restaurant.id")
    table_id: Optional[int] = Field(default=None, foreign_key="table.id")
    host_user_id: int = Field(foreign_key="user.id")
    session_code: str = Field(default_factory=lambda: secrets.token_hex(3).upper())
    status: str = Field(default="active")  # active | billing | closed
    total_amount: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None

    restaurant: Optional["Restaurant"] = Relationship(back_populates="dining_sessions")
    table: Optional["Table"] = Relationship(back_populates="dining_sessions")
    participants: List["SessionParticipant"] = Relationship(back_populates="session")

class DiningSessionCreate(SQLModel):
    restaurant_id: int
    table_id: Optional[int] = None
    host_user_id: int

class DiningSessionRead(SQLModel):
    id: int
    restaurant_id: int
    table_id: Optional[int]
    host_user_id: int
    session_code: str
    status: str
    total_amount: float
    created_at: datetime

    class Config:
        orm_mode = True

# ─────────────────────────────────────────────
# SESSION PARTICIPANT
# ─────────────────────────────────────────────
class SessionParticipant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="diningsession.id")
    user_id: int = Field(foreign_key="user.id")
    share_amount: float = Field(default=0.0)
    is_paid: bool = Field(default=False)
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    session: Optional["DiningSession"] = Relationship(back_populates="participants")
    user: Optional["User"] = Relationship(back_populates="session_participants")

class SessionParticipantRead(SQLModel):
    id: int
    session_id: int
    user_id: int
    share_amount: float
    is_paid: bool
    joined_at: datetime

    class Config:
        orm_mode = True

# ─────────────────────────────────────────────
# ORDER
# ─────────────────────────────────────────────
class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    customer_name: str
    customer_phone: str
    total_amount: float
    status: str = Field(default="pending")  # pending | confirmed | preparing | ready | delivered | cancelled
    special_instructions: Optional[str] = None
    restaurant_id: int = Field(foreign_key="restaurant.id")
    session_id: Optional[int] = Field(default=None, foreign_key="diningsession.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    restaurant: Optional["Restaurant"] = Relationship(back_populates="orders")
    user: Optional["User"] = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")

class OrderBase(SQLModel):
    customer_name: str
    customer_phone: str
    total_amount: float
    status: str = "pending"
    special_instructions: Optional[str] = None
    restaurant_id: int

class OrderCreate(OrderBase):
    order_items: List["OrderItemCreate"] = []
    user_id: Optional[int] = None
    session_id: Optional[int] = None

class OrderRead(OrderBase):
    id: int
    user_id: Optional[int]
    session_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class OrderStatusUpdate(SQLModel):
    status: str

# ─────────────────────────────────────────────
# ORDER ITEM
# ─────────────────────────────────────────────
class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int
    unit_price: float
    special_request: Optional[str] = None
    order_id: int = Field(foreign_key="order.id")
    menu_item_id: int = Field(foreign_key="menuitem.id")

    order: Optional["Order"] = Relationship(back_populates="order_items")
    menu_item: Optional["MenuItem"] = Relationship(back_populates="order_items")

class OrderItemBase(SQLModel):
    quantity: int
    unit_price: float
    special_request: Optional[str] = None
    menu_item_id: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemRead(OrderItemBase):
    id: int
    order_id: int

    class Config:
        orm_mode = True

# ─────────────────────────────────────────────
# WALLET
# ─────────────────────────────────────────────
class WalletTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    amount: float
    transaction_type: str  # credit | debit
    description: str
    reference_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="wallet_transactions")

class WalletTransactionRead(SQLModel):
    id: int
    user_id: int
    amount: float
    transaction_type: str
    description: str
    reference_id: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class WalletTopup(SQLModel):
    amount: float
    payment_method: str = "upi"

# ─────────────────────────────────────────────
# NOTIFICATION
# ─────────────────────────────────────────────
class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    body: str
    icon: str = Field(default="notifications")
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="notifications")

class NotificationRead(SQLModel):
    id: int
    user_id: int
    title: str
    body: str
    icon: str
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True

# ─────────────────────────────────────────────
# AUTH TOKEN STORE (in-memory, production would use JWT)
# ─────────────────────────────────────────────
# Stored in auth.py