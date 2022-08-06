from sqlmodel import SQLModel, Field

class AccountHistory(SQLModel, table=True):
    """
    In this model we store until which date we have 
    transactions for this account
    """
    id: str = Field(primary_key=True)
    account_id: str = Field(foreign_key="bankaccount.account_id")
    latest_date: str    # Date in format YYYY-MM-DD