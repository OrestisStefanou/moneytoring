from typing import List

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
    access_valid_for_days: int
    access_scope: List[str]
    accepted: str


class AccountDetails(BaseModel):
    currency: str
    name: str
    product: str


class Requisition(BaseModel):
    id: str
    created: str
    redirect: str
    status: str
    institution_id: str
    agreement_id: str
    accounts: List[str]
    link: str


class TransactionAmount(BaseModel):
    amount: str
    currency: str


class Transaction(BaseModel):
    bankTransactionCode: str
    bookingDate: str
    remittanceInformationUnstructured: str
    transactionAmount: TransactionAmount
    transactionId: str
    valueDate: str


class AccountTransactions(BaseModel):
    booked: List[Transaction]
    pending: List[Transaction]
