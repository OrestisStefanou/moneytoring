from datetime import datetime
from typing import Iterable, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repos.sql_repo import SQLRepo
from app.models.database.transaction import AccountTransaction

class TransactionRepo(SQLRepo):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=AccountTransaction)

    async def add(
        self,
        _id: str,
        account_id: str,
        amount: str,
        currency: str,
        information: str,
        code: str,
        created_date: str,   # Date in format YYYY-MM-DD
        booking_date: str,   # Date in format YYYY-MM-DD
        debtor_name: Optional[str] = None
    ) -> AccountTransaction:
        booking_date_obj = datetime.strptime(booking_date, "%Y-%m-%d")
        transaction = AccountTransaction(
            id=_id,
            account_id=account_id,
            amount=amount,
            currency=currency,
            information=information,
            code=code,
            created_date=created_date,
            booking_date=booking_date,
            booking_day=booking_date_obj.day,
            booking_month=booking_date_obj.month,
            booking_year=booking_date_obj.year,
            debtor_name=debtor_name
        )

        self._session.add(transaction)
        await self._session.commit()
        return transaction
    
    async def get_for_account_id(
        self,
        account_id: str,
        date_from: str,
        date_to: str
    ) -> Iterable[AccountTransaction]:
        # Transform date_from and date_to from string to datetime objects
        from_date = datetime.strptime(date_from, "%Y-%m-%d")
        to_date = datetime.strptime(date_to, "%Y-%m-%d")

        statement = select(AccountTransaction).where(
            AccountTransaction.account_id == account_id,
            AccountTransaction.booking_day >= from_date.day,
            AccountTransaction.booking_month >= from_date.month,
            AccountTransaction.booking_year >= from_date.year,
            AccountTransaction.booking_day <= to_date.day,
            AccountTransaction.booking_month <= to_date.month,
            AccountTransaction.booking_year <= to_date.year
        )
        account_transactions = await self._session.exec(statement)
        return account_transactions
