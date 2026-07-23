from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from uuid import UUID
from sqlalchemy import Column, Integer, String, ForeignKey

class Restaurant(SQLModel, table=True):
    __tablename__ = "restaurants"
    
    id: int = Field(default=None, primary_key=True)
    name: str
    
    # Relationship to Order
    orders: List["Order"] = Relationship(back_populates="restaurant")

class Order(SQLModel, table=True):
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    
    # Relationship to Restaurant
    restaurant: Optional["Restaurant"] = Relationship(back_populates="orders")

# Test creating the tables
if __name__ == '__main__':
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///test.db')
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully!")
    
    # Test that we can access the relationships
    print("Restaurant.orders property:", Restaurant.orders)
    print("Order.restaurant property:", Order.restaurant)
