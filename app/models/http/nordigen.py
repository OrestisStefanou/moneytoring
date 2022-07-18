from typing import Optional,Dict,Any,List

from pydantic import BaseModel


class NordigenToken(BaseModel):
    access: str
    access_expires: int
    refresh: str
    refresh_expires: int


class Bank(BaseModel):
    id: str
    name: str
    bic: str
    transaction_total_days: int
    logo: str


class Agreement(BaseModel):
    id: str
    created: str
    max_historical_days: int
    access_valid_for_days: int
    access_scope: List[str]
    accepted: Optional[str] = None


class BankLink(BaseModel):
    id: str
    user_id: str
    created_at: str
    redirect: str
    link: str
    institution_id: str
    status: str
    agreement: Optional[Agreement] = None
    meta_reference: Optional[Dict[str,Any]] = None   
    accounts: Optional[List[str]] = None