from typing import Any, Iterable, List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

import app.services.account_history as account_history_service
import app.services.transactions as transaction_service
import app.entities.transaction as transaction_entities

async def get_account_transactions(
    session: AsyncSession,
    account_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> Iterable[transaction_entities.Transaction]:    # Replace this with the entity that we will create
    """
    1. Check if we internally have account transactions for these dates
    2. If we have fetch and return them
    3. If we don't
        1. Fetch the transactions from nordigen
        2. Save the transactions internally
        3. Update AccountHistory model
        4. Return the transactions
    """
    # Check account history
    account_history = await account_history_service.get_account_history(
        session=session,
        account_id=account_id
    )

    if account_history is None:
        # This is the first time we try to get transactions for this account
        # so we have to create an account history, fetch the transactions from nordigen
        # and save them internally
        await transaction_service.fetch_and_save_account_transactions_from_nordigen(
            session=session,
            account_id=account_id
        )
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

    # Return the transaction entity here
    for internal_transaction in transactions:
        yield transaction_entities.Transaction(**internal_transaction.dict())