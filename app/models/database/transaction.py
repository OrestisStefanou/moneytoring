from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class TransactionStatus(str, Enum):
    booked = "booked"
    pending = "pending"


class Transaction(SQLModel, table=True):
    id: str = Field(primary_key=True)
    account_id: str = Field(foreign_key="bankaccount.account_id")
    amount: str
    currency: str
    information: str
    code: str
    booking_date: str   # Date in format YYYY-MM-DD
    status: TransactionStatus
    category: Optional[str] = None  # TODO: Create an Enum for this, it will be set by the user
    custom_category: Optional[str] = None   # This will be set by the user 
