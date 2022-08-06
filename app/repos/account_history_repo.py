from sqlmodel.ext.asyncio.session import AsyncSession

from app.repos.sql_repo import SQLRepo
from app.models.database.account_history import AccountHistory

class AccountHistoryRepo(SQLRepo):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=AccountHistory)


    async def add(
        self,
        _id: str,
        account_id: str,
        latest_date: str
    ) -> AccountHistory:
        account_history = AccountHistory(
            id=_id,
            account_id=account_id,
            latest_date=latest_date
        )

        self._session.add(account_history)
        await self._session.commit()
        return account_history
