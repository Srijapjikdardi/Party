from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from uuid import UUID

class Restaurant(SQLModel, table=True):
    __tablename__ = "restaurants"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    
    # Relationship to Order
    orders: List["Order"] = Relationship(back_populates="restaurant")

class Order(SQLModel, table=True):
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    restaurant_id: Optional[int] = Field(default=None, foreign_key="restaurants.id")
    
    # Relationship to Restaurant - NOT optional in our actual code
    restaurant: "Restaurant" = Relationship(back_populates="orders")

# Test creating the tables
if __name__ == '__main__':
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully!")
    
    # Test that we can access the relationships
    print("Restaurant.orders property:", Restaurant.orders)
    print("Order.restaurant property:", Order.restaurant)
