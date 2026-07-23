from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Session, select, func

from app.models import Bill, BillSplitRecord, DiningSession, Order, Payment, SessionParticipant, User
from app.repositories import BillRepository, BillSplitRecordRepository, DiningSessionRepository, OrderRepository, SessionParticipantRepository


class BillService:
    def __init__(self, session: Session):
        self.session = session
        self.bills = BillRepository(session)
        self.bill_splits = BillSplitRecordRepository(session)
        self.sessions = DiningSessionRepository(session)
        self.orders = OrderRepository(session)
        self.participants = SessionParticipantRepository(session)

    def generate_bill_for_session(
        self,
        session_id: UUID,
        split_type: str = "equal",
        custom_amounts: Optional[Dict[int, Decimal]] = None,
    ) -> Bill:
        """Generate a bill from a dining session's orders with split options.
        split_type: "equal", "individual", or "host_paid".
        For "individual", custom_amounts must be provided mapping participant_id -> amount_owed.
        For "host_paid", host pays total amount, others owe 0.
        """
        # Fetch session
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        if session.status != "active":
            raise ValueError("Session must be active to generate bill")

        # Calculate total from orders
        orders = self.orders.list_by_session(session_id)
        total = sum((order.total_amount for order in orders), Decimal("0.00"))

        # Create bill
        bill = Bill(
            session_id=session_id,
            subtotal=total,
            tax=Decimal("0.00"),
            service_charge=Decimal("0.00"),
            discount=Decimal("0.00"),
            total_amount=total,
            status="pending",  # pending split
            split_type=split_type,
        )
        bill = self.bills.add(bill)

        # Get participants
        participants = self.participants.list_by_session(session_id)
        if not participants:
            raise ValueError("No participants in session")

        # Determine host participant
        host_participant = None
        for p in participants:
            if p.user_id == session.host_user_id:
                host_participant = p
                break

        # Compute amount owed per participant based on split_type
        amounts: Dict[int, Decimal] = {}
        if split_type == "equal":
            share = total / len(participants)
            for participant in participants:
                amounts[participant.id] = share
        elif split_type == "individual":
            if not custom_amounts:
                raise ValueError("custom_amounts required for individual split")
            # Validate that all participants have an amount and sum equals total
            sum_amount = decimal.Decimal("0.00")
            for participant in participants:
                amt = custom_amounts.get(participant.id)
                if amt is None:
                    raise ValueError(f"Missing amount for participant {participant.id}")
                amounts[participant.id] = amt
                sum_amount += amt
            if sum_amount != total:
                raise ValueError("Sum of custom amounts must equal total")
        elif split_type == "host_paid":
            if not host_participant:
                raise ValueError("Host participant not found")
            for participant in participants:
                if participant.id == host_participant.id:
                    amounts[participant.id] = total
                else:
                    amounts[participant.id] = decimal.Decimal("0.00")
        else:
            raise ValueError(f"Invalid split_type: {split_type}")

        # Update participant share_amount and create split records
        for participant in participants:
            amount_owed = amounts[participant.id]
            participant.share_amount = amount_owed
            self.session.add(participant)
            split = BillSplitRecord(
                bill_id=bill.id,
                participant_id=participant.id,
                amount_owed=amount_owed,
                amount_paid=decimal.Decimal("0.00"),
                status="pending",
            )
            self.session.add(split)

        self.session.commit()
        self.session.refresh(bill)
        return bill

    def get_bill(self, bill_id: UUID) -> Optional[Bill]:
        return self.bills.get(bill_id)

    def get_bill_splits(self, bill_id: UUID) -> List[BillSplitRecord]:
        return self.bill_splits.list_by_bill(bill_id)

    def record_payment(self, bill_id: UUID, participant_id: int, amount: Decimal) -> BillSplitRecord:
        """Record a payment against a participant's share."""
        stmt = select(BillSplitRecord).where(
            BillSplitRecord.bill_id == bill_id,
            BillSplitRecord.participant_id == participant_id
        )
        split = self.session.exec(stmt).first()
        if not split:
            raise ValueError("Split record not found for participant")
        if split.amount_paid + amount > split.amount_owed:
            raise ValueError("Payment exceeds amount owed")
        split.amount_paid += amount
        if split.amount_paid >= split.amount_owed:
            split.status = "paid"
        self.session.add(split)
        # Create payment record
        participant = self.session.get(SessionParticipant, participant_id)
        payment = Payment(
            user_id=participant.user_id,
            bill_split_record_id=split.id,
            purpose="bill_split",
            amount=amount,
            status="success",
            method="cash",
            currency="INR",
            gateway="internal",
            gateway_order_id=str(uuid4()),
        )
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(split)
        self.session.refresh(payment)
        # Update participant is_paid if fully paid
        if split.status == "paid":
            participant = self.participants.get(participant_id)
            if participant:
                participant.is_paid = True
                self.session.add(participant)
                self.session.commit()
        return split

    def get_bill_status(self, bill_id: UUID) -> dict:
        """Return summary of bill payment status."""
        bill = self.bills.get(bill_id)
        if not bill:
            raise ValueError("Bill not found")
        splits = self.bill_splits.list_by_bill(bill_id)
        total_owed = sum((s.amount_owed for s in splits), Decimal("0.00"))
        total_paid = sum((s.amount_paid for s in splits), Decimal("0.00"))
        paid_count = sum(1 for s in splits if s.status == "paid")
        return {
            "bill_id": bill.id,
            "total_amount": bill.total_amount,
            "total_owed": total_owed,
            "total_paid": total_paid,
            "paid_count": paid_count,
            "total_participants": len(splits),
            "is_fully_paid": total_paid >= total_owed,
        }