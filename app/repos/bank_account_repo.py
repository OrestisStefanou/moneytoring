from typing import Iterable
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.repos.sql_repo import SQLRepo
from app.models.database.bank_account import BankAccount


class BankAccountRepo(SQLRepo):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=BankAccount)
    
    async def add(
        self,
        account_id: str,
        requistion_id: str,
        name: str,
        currency: str,
    ) -> BankAccount:
        bank_account = BankAccount(
            account_id=account_id,
            requisition_id=requistion_id,
            name=name,
            currency=currency
        )
        self._session.add(bank_account)
        await self._session.commit()
        return bank_account

    async def get_accounts_by_requisition_id(
        self,
        requistion_id: str,
    ) -> Iterable[BankAccount]:
        statement = select(BankAccount).where(BankAccount.requisition_id == requistion_id)
        bank_accounts = await self._session.exec(statement)
        return bank_accounts
