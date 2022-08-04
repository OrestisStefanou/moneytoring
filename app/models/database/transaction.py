from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class TransactionCategory(str, Enum):
    housing = 'housing'
    transportation = 'transportation'
    food = 'food'
    utilities = 'utilities'
    clothing = 'clothing'
    healthcare = 'healthcare'
    insurance = 'insurance'
    household_items = 'household_items'
    personal = 'personal'
    debt = 'debt'
    retirement = 'retirement'
    education = 'education'
    savings = 'savings'
    gifts = 'gifts'
    entertainment = 'entertainment'


class AccountTransaction(SQLModel, table=True):
    id: str = Field(primary_key=True)
    account_id: str = Field(foreign_key="bankaccount.account_id")
    amount: str
    currency: str
    information: str
    debtor_name: Optional[str] = None
    code: str
    created_date: str   # Date in format YYYY-MM-DD
    booking_date: str   # Date in format YYYY-MM-DD
    booking_day: int
    booking_month: int
    booking_year: int
    category: Optional[TransactionCategory] = None  # This will be set by the user
    custom_category: Optional[str] = None   # This will be set by the user 
