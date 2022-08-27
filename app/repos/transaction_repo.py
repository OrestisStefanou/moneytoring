from datetime import datetime
from typing import AsyncIterable, Iterable, List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import sqlalchemy

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
            booking_date_ts=booking_date_obj.timestamp(),
            booking_day=booking_date_obj.day,
            booking_month=booking_date_obj.month,
            booking_year=booking_date_obj.year,
            debtor_name=debtor_name
        )

        try:
            self._session.add(transaction)
            await self._session.commit()
        except sqlalchemy.exc.IntegrityError:
            # We are trying to insert transaction that already
            # exists so we just return in this case
            await self._session.rollback()
            return  
        
        return transaction
    
    async def get_for_account_id(
        self,
        account_id: str,
        date_from: str,
        date_to: str
    ) -> Iterable[AccountTransaction]:
        """
        Get transactions of account_id sorted by booking_date desc
        """
        # Transform date_from and date_to from string to datetime objects
        from_date = datetime.strptime(date_from, "%Y-%m-%d")
        to_date = datetime.strptime(date_to, "%Y-%m-%d")

        statement = select(AccountTransaction).where(
            AccountTransaction.account_id == account_id,
            AccountTransaction.booking_date_ts >= from_date.timestamp(),
            AccountTransaction.booking_date_ts <= to_date.timestamp()
        ).order_by(AccountTransaction.booking_date_ts.desc())

        account_transactions = await self._session.exec(statement)
        return account_transactions

    async def get_for_account_list(
        self,
        accounts_list: List[str],
        date_from: str,
        date_to: str
    ) -> AsyncIterable[AccountTransaction]:
        """
        Get transactions for list of account_ids sorted by booking_date desc
        """
        # Transform date_from and date_to from string to datetime objects
        from_date = datetime.strptime(date_from, "%Y-%m-%d")
        to_date = datetime.strptime(date_to, "%Y-%m-%d")

        statement = f"""SELECT * FROM  accounttransaction 
                    WHERE booking_date_ts <= {to_date.timestamp()}
                    AND booking_date_ts >= {from_date.timestamp()}
                    AND accounttransaction.account_id IN {tuple(accounts_list)}
                    ORDER BY booking_date_ts DESC;"""

        account_transactions = await self._session.exec(statement)
        for transaction in account_transactions:
            yield AccountTransaction(**transaction)

