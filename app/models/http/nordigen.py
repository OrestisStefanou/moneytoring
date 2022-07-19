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
