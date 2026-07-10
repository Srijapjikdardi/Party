from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

# Restaurant model
class Restaurant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: str
    phone: str
    cuisine_type: str
    rating: float = Field(default=0.0, ge=0, le=5)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    menu_items: List["MenuItem"] = Relationship(back_populates="restaurant")
    orders: List["Order"] = Relationship(back_populates="restaurant")

# MenuItem model
class MenuItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    price: float
    category: str
    is_available: bool = Field(default=True)
    restaurant_id: int = Field(foreign_key="restaurant.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    restaurant: Optional["Restaurant"] = Relationship(back_populates="menu_items")
    order_items: List["OrderItem"] = Relationship(back_populates="menu_item")

# Order model
class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str
    customer_phone: str
    total_amount: float
    status: str = Field(default="pending")  # pending, confirmed, preparing, ready, delivered, cancelled
    special_instructions: Optional[str] = None
    restaurant_id: int = Field(foreign_key="restaurant.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    restaurant: Optional["Restaurant"] = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")

# OrderItem model
class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int
    unit_price: float
    special_request: Optional[str] = None
    order_id: int = Field(foreign_key="order.id")
    menu_item_id: int = Field(foreign_key="menuitem.id")

    # Relationships
    order: Optional["Order"] = Relationship(back_populates="order_items")
    menu_item: Optional["MenuItem"] = Relationship(back_populates="order_items")

# Pydantic models for API
class RestaurantBase(SQLModel):
    name: str
    address: str
    phone: str
    cuisine_type: str
    rating: float = Field(default=0.0, ge=0, le=5)
    is_active: bool = True

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantRead(RestaurantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class MenuItemBase(SQLModel):
    name: str
    description: str
    price: float
    category: str
    is_available: bool = True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemRead(MenuItemBase):
    id: int
    restaurant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class OrderBase(SQLModel):
    customer_name: str
    customer_phone: str
    total_amount: float
    status: str = "pending"
    special_instructions: Optional[str] = None
    restaurant_id: int

class OrderCreate(OrderBase):
    order_items: List["OrderItemCreate"] = []

class OrderRead(OrderBase):
    id: int
    restaurant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class OrderItemBase(SQLModel):
    quantity: int
    unit_price: float
    special_request: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemRead(OrderItemBase):
    id: int
    order_id: int
    menu_item_id: int

    class Config:
        orm_mode = True