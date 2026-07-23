from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas import BillRead, BillSplitRead, BillSplitUpdate, PaymentCreate, BillGenerate
from app.services import BillService, DiningSessionService

router = APIRouter(prefix="/bills", tags=["bills"])


@router.post("/session/{session_id}", response_model=BillRead)
def generate_bill(
    session_id: UUID,
    payload: BillGenerate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Generate a bill for a session. Only host can generate bill."""
    # Verify user is host of session
    session_service = DiningSessionService(session)
    ds = session_service.get_session(session_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Session not found")
    if ds.host_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only host can generate bill",
        )
    bill_service = BillService(session)
    bill = bill_service.generate_bill_for_session(
        session_id,
        split_type=payload.split_type,
        custom_amounts=payload.custom_amounts,
    )
    return bill


@router.get("/{bill_id}", response_model=BillRead)
def get_bill(
    bill_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    bill_service = BillService(session)
    bill = bill_service.get_bill(bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    # Optionally check if user is participant of the session
    session_service = DiningSessionService(session)
    ds = session_service.get_session(bill.session_id)
    participant = session_service.get_participant(ds.id, current_user.id)
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant")
    return bill


@router.get("/{bill_id}/splits", response_model=List[BillSplitRead])
def get_bill_splits(
    bill_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    bill_service = BillService(session)
    # Verify bill exists and participant
    bill = bill_service.get_bill(bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    session_service = DiningSessionService(session)
    ds = session_service.get_session(bill.session_id)
    participant = session_service.get_participant(ds.id, current_user.id)
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant")
    splits = bill_service.get_bill_splits(bill_id)
    return splits


@router.post("/{bill_id}/participants/{participant_id}/payments", response_model=BillSplitRead)
def record_payment_for_participant(
    bill_id: UUID,
    participant_id: int,
    payment: PaymentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Record a payment for a participant against a bill."""
    bill_service = BillService(session)
    # Verify bill exists
    bill = bill_service.get_bill(bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    # Verify participant belongs to the bill's session
    session_service = DiningSessionService(session)
    ds = session_service.get_session(bill.session_id)
    participant = session_service.get_participant(ds.id, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found in session")
    # Verify current user is the participant (they can only pay their own share)
    if participant.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only pay for yourself",
        )
    # Record payment
    updated_split = bill_service.record_payment(
        bill_id, participant_id, payment.amount
    )
    return updated_split


@router.patch("/splits/{split_id}", response_model=BillSplitRead)
def record_payment(
    split_id: int,
    update: BillSplitUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Record a payment against a split. User can only pay their own split."""
    # Get the split record
    from app.models import BillSplitRecord
    split = session.get(BillSplitRecord, split_id)
    if not split:
        raise HTTPException(status_code=404, detail="Split not found")
    # Verify participant belongs to current user
    from app.models import SessionParticipant
    participant = session.get(SessionParticipant, split.participant_id)
    if not participant or participant.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your split",
        )
    bill_service = BillService(session)
    # Note: update.amount_paid is the amount to pay now; we need to add to existing amount_paid
    # Our service.record_payment expects amount to add, not total paid.
    # We'll adjust: we assume update.amount_paid is the amount to pay now.
    updated_split = bill_service.record_payment(
        split.bill_id, split.participant_id, update.amount_paid
    )
    return updated_split