from typing import Optional
import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repos.sql_repo import SQLRepo
from app.models.database.account_history import AccountHistory

class AccountHistoryRepo(SQLRepo):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=AccountHistory)


    async def add(
        self,
        account_id: str,
        latest_date: str
    ) -> AccountHistory:
        account_history = AccountHistory(
            id=str(uuid.uuid4()),
            account_id=account_id,
            latest_date=latest_date
        )

        self._session.add(account_history)
        await self._session.commit()
        return account_history

    async def get_by_account_id(self, account_id: str) -> Optional[AccountHistory]:
        statement = select(AccountHistory).where(AccountHistory.account_id == account_id)
        result = await self._session.exec(statement)
        return result.first()

    async def update_latest_date_for_account_id(self, account_id: str, latest_date: str) -> AccountHistory:
        account_history = await self.get_by_account_id(account_id)
        account_history.latest_date = latest_date

        self._session.add(account_history)
        await self._session.commit()
        await self._session.refresh(account_history)
        return account_history