from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlmodel import SQLModel, Session, create_engine, select
from typing import List
import os
from pathlib import Path
from . import models, crud

# Create database engine
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)

# Create tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency to get DB session
def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="PartyPe API")

# Create tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Create sample data if none exists
    with Session(engine) as session:
        if not session.exec(select(models.Restaurant)).first():
            crud.create_sample_data(session)

# Mount static files for frontend
BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend"), name="static")

# Serve frontend index.html
@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = BASE_DIR / "frontend" / "index.html"
    with open(index_path, "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# Restaurant endpoints
@app.get("/api/restaurants", response_model=list[models.RestaurantRead])
def read_restaurants(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    restaurants = crud.get_restaurants(session, skip=skip, limit=limit)
    return restaurants

@app.get("/api/restaurants/{restaurant_id}", response_model=models.RestaurantRead)
def read_restaurant(restaurant_id: int, session: Session = Depends(get_session)):
    restaurant = crud.get_restaurant(session, restaurant_id=restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@app.get("/api/restaurants/{restaurant_id}/menu", response_model=list[models.MenuItemRead])
def read_menu(restaurant_id: int, session: Session = Depends(get_session)):
    menu_items = crud.get_menu_items_by_restaurant(session, restaurant_id=restaurant_id)
    return menu_items

# Order endpoints
@app.post("/api/orders", response_model=models.OrderRead)
def create_order(order: models.OrderCreate, session: Session = Depends(get_session)):
    return crud.create_order(session=session, order=order)

@app.get("/api/orders/{order_id}", response_model=models.OrderRead)
def read_order(order_id: int, session: Session = Depends(get_session)):
    order = crud.get_order(session, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}