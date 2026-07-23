from sqlmodel import select

from app.models import Bill
from app.repositories.base import BaseRepository


class BillRepository(BaseRepository[Bill]):
    model = Bill

    def list_by_session(self, session_id):
        return self.session.exec(
            select(Bill).where(Bill.session_id == session_id)
        ).all()
