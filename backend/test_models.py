from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = 'restaurants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    
    # Relationship to Order
    orders = relationship("Order", back_populates="restaurant")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    description = Column(String(100))
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    
    # Relationship to Restaurant
    restaurant = relationship("Restaurant", back_populates="orders")

# Test creating the tables
if __name__ == '__main__':
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///test.db')
    Base.metadata.create_all(engine)
    print("Tables created successfully!")
    
    # Test that we can access the relationships
    print("Restaurant.orders property:", Restaurant.orders)
    print("Order.restaurant property:", Order.restaurant)
