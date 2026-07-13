from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas import WalletTopup, WalletTransactionRead
from app.services import WalletError, WalletService

router = APIRouter(prefix="/wallet", tags=["wallet"])


class WalletPaymentRequest(BaseModel):
    amount: Decimal
    description: str = "Payment"


@router.get("")
def get_wallet(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    summary = WalletService(session).get_summary(current_user)
    return {
        "balance": summary["balance"],
        "transactions": [WalletTransactionRead.model_validate(t) for t in summary["transactions"]],
    }


@router.post("/topup", response_model=WalletTransactionRead)
def wallet_topup(
    topup: WalletTopup,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if topup.amount <= 0 or topup.amount > 50000:
        raise HTTPException(status_code=400, detail="Invalid amount")
    try:
        return WalletService(session).topup(current_user.id, topup.amount, topup.payment_method)
    except WalletError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/pay")
def wallet_pay(
    body: WalletPaymentRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    success = WalletService(session).pay(current_user.id, body.amount, body.description)
    if not success:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")
    return {"success": True, "message": "Payment successful"}
