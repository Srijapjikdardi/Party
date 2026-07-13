from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.schemas import MenuItemRead, RestaurantRead, TableRead
from app.services import MenuService, RestaurantService, TableService

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("", response_model=List[RestaurantRead])
def list_restaurants(
    skip: int = 0,
    limit: int = 100,
    cuisine: Optional[str] = None,
    session: Session = Depends(get_session),
):
    return RestaurantService(session).list_restaurants(skip=skip, limit=limit, cuisine=cuisine)


@router.get("/{restaurant_id}", response_model=RestaurantRead)
def get_restaurant(restaurant_id: UUID, session: Session = Depends(get_session)):
    restaurant = RestaurantService(session).get_restaurant(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.get("/{restaurant_id}/menu", response_model=List[MenuItemRead])
def get_menu(restaurant_id: UUID, session: Session = Depends(get_session)):
    return MenuService(session).list_for_restaurant(restaurant_id)


@router.get("/{restaurant_id}/tables", response_model=List[TableRead])
def get_tables(restaurant_id: UUID, session: Session = Depends(get_session)):
    return TableService(session).list_for_restaurant(restaurant_id)
