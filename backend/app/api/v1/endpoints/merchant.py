from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.db.session import get_session
from app.schemas import OrderRead, TableRead
from app.services import OrderService, TableService

router = APIRouter(prefix="/merchant", tags=["merchant"])


class TableStatusUpdate(BaseModel):
    status: str = "available"


@router.get("/orders", response_model=List[OrderRead])
def merchant_orders(restaurant_id: int, limit: int = 50, session: Session = Depends(get_session)):
    return OrderService(session).list_for_restaurant(restaurant_id, limit)


@router.get("/tables", response_model=List[TableRead])
def merchant_tables(restaurant_id: int, session: Session = Depends(get_session)):
    return TableService(session).list_for_restaurant(restaurant_id)


@router.patch("/tables/{table_id}/status", response_model=TableRead)
def update_table_status(table_id: int, body: TableStatusUpdate, session: Session = Depends(get_session)):
    table = TableService(session).update_status(table_id, body.status)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table


@router.get("/analytics")
def merchant_analytics(restaurant_id: int, session: Session = Depends(get_session)):
    return OrderService(session).restaurant_analytics(restaurant_id)
