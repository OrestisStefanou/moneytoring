from datetime import datetime
from sqlmodel import SQLModel, Field

class AccountHistory(SQLModel, table=True):
    """
    In this model we store until which date we have 
    transactions for this account
    """
    id: str = Field(primary_key=True)
    account_id: str = Field(foreign_key="bankaccount.account_id")
    latest_date: str    # Date in format YYYY-MM-DD

    def covers_date(self, requested_date: str) -> bool:
        """
        - Params:
            - requested_date: Date string in format YYYY-MM-DD
        - Returns:
            - True if latest_date of the model is after requested_date
            - False otherwise
        """
        latest_date = datetime.strptime(self.latest_date, "%Y-%m-%d")
        requested_date_obj = datetime.strptime(requested_date, "%Y-%m-%d") 
        return latest_date > requested_date_obj
