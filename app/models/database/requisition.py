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
    created_at: Optional[str] = None     # Date in format YYYY-MM-DD
    expires_at: Optional[str] = None     # Date in format YYYY-MM-DD
    max_historical_days: Optional[int] = None
