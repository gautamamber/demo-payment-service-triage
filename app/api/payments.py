import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Payment, get_db

router = APIRouter()
logger = logging.getLogger(__name__)


class CreatePayment(BaseModel):
    customer_id: str
    amount: float


class PaymentOut(BaseModel):
    id: str
    customer_id: str
    amount: float
    status: str

    model_config = {"from_attributes": True}


@router.post("/payments", response_model=PaymentOut)
def create_payment(body: CreatePayment, db: Session = Depends(get_db)):
    fraud_resp = httpx.post(
        f"{settings.fraud_mock_url}/check",
        json={"customer_id": body.customer_id, "amount": body.amount},
        timeout=5,
    )
    fraud_resp.raise_for_status()
    approved = fraud_resp.json()["approved"]

    payment = Payment(
        customer_id=body.customer_id,
        amount=body.amount,
        status="completed" if approved else "rejected",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/payments/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: str, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if payment is None:
        logger.warning("Payment not found: %s", payment_id)
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.get("/customers/{customer_id}/payments", response_model=list[PaymentOut])
def list_customer_payments(customer_id: str, db: Session = Depends(get_db)):
    return db.query(Payment).filter(Payment.customer_id == customer_id).all()


@router.post("/payments/{payment_id}/refund", response_model=PaymentOut)
def refund_payment(payment_id: str, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    payment.status = "refunded"
    db.commit()
    db.refresh(payment)
    return payment
