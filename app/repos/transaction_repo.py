from datetime import datetime
from typing import AsyncIterable, Iterable, List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import sqlalchemy

from app.repos.sql_repo import SQLRepo
from app.models.database.transaction import AccountTransaction,TransactionCategory

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
        date_to: str,
        category: Optional[TransactionCategory] = None,
        custom_category: Optional[str] = None
    ) -> Iterable[AccountTransaction]:
        """
        Get transactions of account_id sorted by booking_date desc
        """
        # Transform date_from and date_to from string to datetime objects
        from_date = datetime.strptime(date_from, "%Y-%m-%d")
        to_date = datetime.strptime(date_to, "%Y-%m-%d")

        where_conditions = [
            AccountTransaction.account_id == account_id,
            AccountTransaction.booking_date_ts >= from_date.timestamp(),
            AccountTransaction.booking_date_ts <= to_date.timestamp()
        ]

        if category is not None:
            where_conditions.append(
                AccountTransaction.category == category
            )

        if custom_category is not None:
            where_conditions.append(
                AccountTransaction.custom_category == custom_category
            )

        statement = select(AccountTransaction).where(*where_conditions).order_by(AccountTransaction.booking_date_ts.desc())

        account_transactions = await self._session.exec(statement)
        return account_transactions

    async def get_for_account_list(
        self,
        accounts_list: List[str],
        date_from: str,
        date_to: str,
        category: Optional[TransactionCategory] = None,
        custom_category: Optional[str] = None
    ) -> AsyncIterable[AccountTransaction]:
        """
        Get transactions for list of account_ids sorted by booking_date desc
        """
        # Transform date_from and date_to from string to datetime objects
        from_date = datetime.strptime(date_from, "%Y-%m-%d")
        to_date = datetime.strptime(date_to, "%Y-%m-%d")

        where_conditions = f"""WHERE booking_date_ts <= {to_date.timestamp()}
                    AND booking_date_ts >= {from_date.timestamp()}
                    AND account_id IN {tuple(accounts_list)} """
        
        if category:
            where_conditions += f"AND category = '{category}' "

        if custom_category:
            where_conditions += f"AND custom_category = '{custom_category}' "

        order_by_condition = "ORDER BY booking_date_ts DESC"

        statement = f"SELECT * FROM  accounttransaction {where_conditions} {order_by_condition};"

        account_transactions = await self._session.exec(statement)
        for transaction in account_transactions:
            yield AccountTransaction(**transaction)

    async def set_category(
        self,
        transaction_id: str,
        category: TransactionCategory,
    ) -> Optional[AccountTransaction]:
        """
        Sets category to AccountTransaction with id=transaction_id
        Returns None if transaction with given id does not exist
        """
        transaction = await self.get(transaction_id)
        if transaction is None:
            return None

        transaction.category = category

        self._session.add(transaction)
        await self._session.commit()
        await self._session.refresh(transaction)
        return transaction

    async def set_custom_category(
        self,
        transaction_id: str,
        custom_category: str,
    ) -> Optional[AccountTransaction]:
        """
        Sets category to AccountTransaction with id=transaction_id
        Returns None if transaction with given id does not exist
        """
        transaction = await self.get(transaction_id)
        if transaction is None:
            return None

        transaction.custom_category = custom_category

        self._session.add(transaction)
        await self._session.commit()
        await self._session.refresh(transaction)
        return transaction
