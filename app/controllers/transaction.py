from datetime import datetime, timedelta
from typing import Iterable, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

import app.services.account_history as account_history_service
import app.services.transactions as transaction_service
import app.services.bank_account as bank_account_service
import app.errors.transaction as transaction_errors
import app.models.database.transaction as transaction_models


async def get_account_transactions(
    session: AsyncSession,
    account_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> Iterable[transaction_models.AccountTransaction]:
    bank_account = await bank_account_service.get_bank_account_by_id(session, account_id)
    if bank_account is None:
        raise transaction_errors.AccountNotFound()
    
    if from_date is None:
        # If from date is not given we set it to 90 days prior from
        # current date as this is max historical days we have access to
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    if to_date is None:
        to_date = datetime.now().strftime("%Y-%m-%d")

    await account_history_service.check_account_history(
        session=session,
        account_id=account_id,
        to_date=to_date
    )

    transactions = await transaction_service.get_internal_transactions(
        session=session,
        account_id=account_id,
        from_date=from_date,
        to_date=to_date
    )

    return transactions
