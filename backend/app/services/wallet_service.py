from datetime import datetime

from sqlmodel import Session

from app.models import User, WalletTransaction
from app.repositories import UserRepository, WalletRepository


class WalletError(Exception):
    """Raised for wallet operations the API layer should turn into 4xx responses."""


class WalletService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)
        self.wallet = WalletRepository(session)

    def get_summary(self, user: User) -> dict:
        transactions = self.wallet.list_by_user(user.id)
        return {"balance": user.wallet_balance, "transactions": transactions}

    def topup(self, user_id: int, amount: float, method: str) -> WalletTransaction:
        user = self.users.get(user_id)
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

    def pay(self, user_id: int, amount: float, description: str) -> bool:
        user = self.users.get(user_id)
        if user.wallet_balance < amount:
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
