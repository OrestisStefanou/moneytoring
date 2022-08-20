from datetime import datetime
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repos.account_history_repo import AccountHistoryRepo
from app.models.database.account_history import AccountHistory
import app.services.transactions as transactions_service

async def create_account_history(session: AsyncSession, account_id: str) ->  AccountHistory:
    account_history_repo = AccountHistoryRepo(session)
    # When we create a new account history the latest date is the current one
    latest_date =  datetime.now().strftime("%Y-%m-%d")
    account_history = await account_history_repo.add(account_id, latest_date)
    return account_history


async def get_account_history(session: AsyncSession, account_id: str) -> Optional[AccountHistory]:
    account_history_repo = AccountHistoryRepo(session)
    account_history = await account_history_repo.get_by_account_id(account_id)
    return account_history


async def update_account_history(session: AsyncSession, account_id: str) -> AccountHistory:
    account_history_repo = AccountHistoryRepo(session)
    latest_date =  datetime.now().strftime("%Y-%m-%d")
    updated_account_history = await account_history_repo.update_latest_date_for_account_id(
        account_id=account_id,
        latest_date=latest_date
    )
    return updated_account_history


async def check_account_history(
    session: AsyncSession,
    account_id: str,
    to_date: str
) -> None:
    # Check account history
    account_history = await get_account_history(
        session=session,
        account_id=account_id
    )

    if account_history is None:
        # This is the first time we try to get transactions for this account
        # so we have to create an account history, fetch the transactions from nordigen
        # and save them internally
        await transactions_service.fetch_and_save_account_transactions_from_nordigen(
            session=session,
            account_id=account_id
        )
        
        await create_account_history(
            session=session,
            account_id=account_id
        )
    else:
        # This not the first time we try to get transactions for this account
        # so we have to check if the internal transactions we have cover the 
        # requested dates
        if account_history.covers_date(to_date) is False:
            await transactions_service.fetch_and_save_account_transactions_from_nordigen(
                session=session,
                account_id=account_id,
                from_date=account_history.latest_date
            )
            await update_account_history(
                session=session,
                account_id=account_id
            )
