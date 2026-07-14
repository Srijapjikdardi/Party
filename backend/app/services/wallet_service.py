from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlmodel import Session

from app.core.errors import AppError
from app.models import User, WalletTransaction
from app.repositories import UserRepository, WalletRepository


class WalletError(AppError):
    """Raised for wallet operations the API layer should turn into 4xx responses."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(status_code, "wallet_error", message)


class WalletService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)
        self.wallet = WalletRepository(session)

    def get_summary(self, user: User) -> dict:
        transactions = self.wallet.list_by_user(user.id)
        return {"balance": user.wallet_balance, "transactions": transactions}

    def topup(self, user_id: UUID, amount: Decimal, method: str) -> WalletTransaction:
        user = self.users.get(user_id)
        if not user:
            raise WalletError("User not found", status_code=404)
        user.wallet_balance += amount
        self.session.add(user)

        txn = WalletTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type="credit",
            description=f"Wallet top-up via {method}",
            reference_id=f"TXN{int(datetime.utcnow().timestamp())}",
        )
        return self.wallet.add(txn)

    def pay(self, user_id: UUID, amount: Decimal, description: str) -> bool:
        user = self.users.get(user_id)
        if not user or user.wallet_balance < amount:
            return False

        user.wallet_balance -= amount
        self.session.add(user)

        txn = WalletTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type="debit",
            description=description,
            reference_id=f"PAY{int(datetime.utcnow().timestamp())}",
        )
        self.session.add(txn)
        self.session.commit()
        return True
