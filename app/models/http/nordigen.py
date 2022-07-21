from typing import Optional,Dict,Any,List

from pydantic import BaseModel


class NordigenToken(BaseModel):
    access: str
    access_expires: int
    refresh: str
    refresh_expires: int


class Institution(BaseModel):
    id: str
    name: str
    bic: str
    transaction_total_days: int
    logo: str


class Agreement(BaseModel):
    id: str
    created: str
    max_historical_days: str
    access_valid_for_days: str
    access_scope: List[str]
    accepted: str


class Requisition(BaseModel):
    id: str
    created: str
    redirect: str
    status: str
    institution_id: str
    agreement_id: str
    accounts: List[str]
    link: str