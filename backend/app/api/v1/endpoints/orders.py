from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.schemas import OrderCreate, OrderRead, OrderStatusUpdate
from app.services import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead)
def create_order(order: OrderCreate, session: Session = Depends(get_session)):
    return OrderService(session).create_order(order)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: UUID, session: Session = Depends(get_session)):
    order = OrderService(session).get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/user/{user_id}", response_model=List[OrderRead])
def get_user_orders(user_id: UUID, session: Session = Depends(get_session)):
    return OrderService(session).list_for_user(user_id)


@router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status(order_id: UUID, update: OrderStatusUpdate, session: Session = Depends(get_session)):
    order = OrderService(session).update_status(order_id, update.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
