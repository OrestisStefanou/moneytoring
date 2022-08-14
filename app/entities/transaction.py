from typing import Optional
from pydantic import BaseModel

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