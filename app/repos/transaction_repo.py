from pyparsing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

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
        booking_day: int,
        booking_month: int,
        booking_year: int,
        debtor_name: Optional[str] = None
    ) -> AccountTransaction:
        transaction = AccountTransaction(
            id=_id,
            account_id=account_id,
            amount=amount,
            currency=currency,
            information=information,
            code=code,
            created_date=created_date,
            booking_date=booking_date,
            booking_day=booking_day,
            booking_month=booking_month,
            booking_year=booking_year,
            debtor_name=debtor_name
        )

        self._session.add(transaction)
        await self._session.commit()
        return transaction