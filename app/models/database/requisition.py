from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class RequisitionStatus(str, Enum):
    linked = "linked"
    not_linked = "not_linked"


class Requisition(SQLModel, table=True):
    id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="appuser.user_id")
    institution_name: str
    link: str
    status: RequisitionStatus = RequisitionStatus.not_linked
    created_at: Optional[str] = None     # Date in format DD-MM-YYYY
    expires_at: Optional[str] = None     # Date in format DD-MM-YYYY
    currency: Optional[str] = None
    max_historical_days: Optional[str] = None
