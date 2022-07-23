from typing import List, Optional
import uuid
from enum import Enum

from pydantic import BaseModel, Field


class CreateRequisitionBody(BaseModel):
    institution_id: str
    redirect_uri: str


class BankAccount(BaseModel):
    account_id: str
    name: str
    currency: str


class BankConnectionStatus(str, Enum):
    pending = "pending"
    created = "created"
    expired = "expired"


class BankConnection(BaseModel):
    id: str
    institution_name: str
    link: str
    status: BankConnectionStatus = BankConnectionStatus.pending
    created_at: Optional[str] = Field(default=None, description='Date in format YYYY-MM-DD')
    expires_at: Optional[str] = Field(default=None, description='Date in format YYYY-MM-DD')
    max_historical_days: Optional[int] = None
    bank_accounts: Optional[List[BankAccount]] = None
