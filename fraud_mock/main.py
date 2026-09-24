import os
import time
from random import random

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="fraud-mock")

LATENCY_MS = float(os.environ.get("FRAUD_MOCK_LATENCY_MS", "50"))
FAILURE_RATE = float(os.environ.get("FRAUD_MOCK_FAILURE_RATE", "0"))


class CheckRequest(BaseModel):
    customer_id: str
    amount: float


class CheckResponse(BaseModel):
    approved: bool


@app.post("/check", response_model=CheckResponse)
def check(body: CheckRequest):
    time.sleep(LATENCY_MS / 1000)
    if random() < FAILURE_RATE:
        approved = False
    else:
        approved = body.amount < 10_000
    return CheckResponse(approved=approved)


@app.get("/health")
def health():
    return {"status": "ok"}
