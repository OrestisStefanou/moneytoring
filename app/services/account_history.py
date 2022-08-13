from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repos.account_history_repo import AccountHistoryRepo
from app.models.database.account_history import AccountHistory


async def create_account_history(session: AsyncSession, account_id: str) ->  AccountHistory:
    account_history_repo = AccountHistoryRepo(session)
    # When we create a new account history the latest date is the current one
    latest_date =  datetime.now().strftime("%Y-%m-%d")


async def get_account_history(session: AsyncSession, account_id: str) -> AccountHistory:
    pass


async def update_account_history(session: AsyncSession, account_id: str, latest_date: str) -> AccountHistory:
    pass 