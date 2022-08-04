from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class RequisitionStatus(str, Enum):
    linked = "linked"
    not_linked = "not_linked"
    expired = "expired"


class Requisition(SQLModel, table=True):
    id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="appuser.user_id")
    institution_id: str
    institution_name: str
    link: str
    status: RequisitionStatus = RequisitionStatus.not_linked
    accepted_at: Optional[str] = None     # Datetime in format YYYY-MM-DDTHH:MM:SS
    expires_at: Optional[str] = None     # Date in format YYYY-MM-DD
    max_historical_days: Optional[int] = None

    @property
    def is_expired(self) -> bool:
        expiration_dt = datetime.strptime(self.expires_at, "%Y-%m-%d")

        if expiration_dt > datetime.now():
            return False
        
        return True