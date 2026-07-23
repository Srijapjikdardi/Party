from sqlmodel import select

from app.models import BillSplitRecord
from app.repositories.base import BaseRepository


class BillSplitRecordRepository(BaseRepository[BillSplitRecord]):
    model = BillSplitRecord

    def list_by_bill(self, bill_id):
        return self.session.exec(
            select(BillSplitRecord).where(BillSplitRecord.bill_id == bill_id)
        ).all()

    def get_by_bill_and_participant(self, bill_id, participant_id):
        return self.session.exec(
            select(BillSplitRecord).where(
                BillSplitRecord.bill_id == bill_id,
                BillSplitRecord.participant_id == participant_id
            )
        ).first()
