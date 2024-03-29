from typing import Optional
from decimal import Decimal

from pydantic import BaseModel

from app.models.database.transaction import TransactionCategory


class Transaction(BaseModel):
    id: str
    account_id: str
    amount: str
    currency: str
    information: str
    code: str
    created_date: str
    booking_date: str
    debtor_name: Optional[str] = None
    category: Optional[str] = None
    custom_category: Optional[str] = None


class TotalSpentResponse(BaseModel):
    total_spent: Decimal


class TotalCreditedResponse(BaseModel):
    total_credited: Decimal
