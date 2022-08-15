from datetime import datetime, timedelta
from typing import Iterable, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

import app.services.account_history as account_history_service
import app.services.transactions as transaction_service
import app.errors.transaction as transaction_errors
import app.models.database.transaction as transaction_models

async def get_account_transactions(
    session: AsyncSession,
    account_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> Iterable[transaction_models.AccountTransaction]:
    """
    1. Check if we internally have account transactions for these dates
    2. If we have fetch and return them
    3. If we don't
        1. Fetch the transactions from nordigen
        2. Save the transactions internally
        3. Update AccountHistory model
        4. Return the transactions
    """
    if from_date is None:
        # If from date is not given we set to 90 days prior from
        # current date as this is max historical days we have access to
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    if to_date is None:
        to_date = datetime.now().strftime("%Y-%m-%d")

    # Check account history
    account_history = await account_history_service.get_account_history(
        session=session,
        account_id=account_id
    )

    if account_history is None:
        # This is the first time we try to get transactions for this account
        # so we have to create an account history, fetch the transactions from nordigen
        # and save them internally
        nordigen_transactions = await transaction_service.fetch_and_save_account_transactions_from_nordigen(
            session=session,
            account_id=account_id
        )
        if nordigen_transactions is None:
            raise transaction_errors.AccountNotFound
        
        await account_history_service.create_account_history(
            session=session,
            account_id=account_id
        )
    else:
        # This not the first time we try to get transactions for this account
        # so we have to check if the internal transactions we have cover the 
        # requested dates
        if account_history.covers_date(to_date) is False:
            await transaction_service.fetch_and_save_account_transactions_from_nordigen(
                session=session,
                account_id=account_id,
                from_date=account_history.latest_date
            )
            await account_history_service.update_account_history(
                session=session,
                account_id=account_id
            )

    transactions = await transaction_service.get_internal_transactions(
        session=session,
        account_id=account_id,
        from_date=from_date,
        to_date=to_date
    )

    if transactions is None:
        raise transaction_errors.AccountNotFound()

    return transactions
