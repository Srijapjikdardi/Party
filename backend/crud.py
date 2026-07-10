from sqlmodel import Session, select
from typing import List
from . import models

def get_restaurants(session: Session, skip: int = 0, limit: int = 100) -> List[models.Restaurant]:
    statement = select(models.Restaurant).offset(skip).limit(limit)
    return session.exec(statement).all()

def get_restaurant(session: Session, restaurant_id: int) -> models.Restaurant | None:
    return session.get(models.Restaurant, restaurant_id)

def get_menu_items_by_restaurant(session: Session, restaurant_id: int) -> List[models.MenuItem]:
    statement = select(models.MenuItem).where(models.MenuItem.restaurant_id == restaurant_id)
    return session.exec(statement).all()

def create_order(session: Session, order: models.OrderCreate) -> models.Order:
    order_dict = order.dict()
    order_items = order_dict.pop("order_items", [])
    db_order = models.Order(**order_dict)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    for item in order_items:
        item["order_id"] = db_order.id
        db_item = models.OrderItem(**item)
        session.add(db_item)
    session.commit()
    session.refresh(db_order)
    return db_order
def get_order(session: Session, order_id: int) -> models.Order | None:
    return session.get(models.Order, order_id)

def create_sample_data(session: Session):
    # Create sample restaurants
    restaurant1 = models.Restaurant(
        name="Spice Garden",
        address="123 Main St, Delhi",
        phone="011-2345-6789",
        cuisine_type="Indian",
        rating=4.5,
        is_active=True
    )
    
    restaurant2 = models.Restaurant(
        name="Pizza Palace",
        address="456 Center Ave, Delhi",
        phone="011-9876-5432",
        cuisine_type="Italian",
        rating=4.2,
        is_active=True
    )
    
    session.add(restaurant1)
    session.add(restaurant2)
    session.commit()
    session.refresh(restaurant1)
    session.refresh(restaurant2)
    
    # Create sample menu items for Spice Garden
    menu_items1 = [
        models.MenuItem(
            name="Butter Chicken",
            description="Creamy tomato-based chicken curry",
            price=299.0,
            category="Main Course",
            is_available=True,
            restaurant_id=restaurant1.id
        ),
        models.MenuItem(
            name="Garlic Naan",
            description="Freshly baked flatbread with garlic",
            price=80.0,
            category="Bread",
            is_available=True,
            restaurant_id=restaurant1.id
        ),
        models.MenuItem(
            name="Vegetable Biryani",
            description="Fragrant rice with mixed vegetables",
            price=249.0,
            category="Main Course",
            is_available=True,
            restaurant_id=restaurant1.id
        )
    ]
    
    # Create sample menu items for Pizza Palace
    menu_items2 = [
        models.MenuItem(
            name="Margherita Pizza",
            description="Classic pizza with tomato, mozzarella, and basil",
            price=349.0,
            category="Pizza",
            is_available=True,
            restaurant_id=restaurant2.id
        ),
        models.MenuItem(
            name="Pepperoni Pizza",
            description="Pizza with pepperoni and extra cheese",
            price=399.0,
            category="Pizza",
            is_available=True,
            restaurant_id=restaurant2.id
        ),
        models.MenuItem(
            name="Caesar Salad",
            description="Fresh romaine lettuce with Caesar dressing",
            price=199.0,
            category="Salad",
            is_available=True,
            restaurant_id=restaurant2.id
        )
    ]
    
    for item in menu_items1 + menu_items2:
        session.add(item)
    
    session.commit()
