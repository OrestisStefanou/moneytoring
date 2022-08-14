from typing import Iterable, List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repos.nordigen_repo import NordigenRepo
from app.repos.transaction_repo import TransactionRepo
import app.models.http.nordigen as nordigen_models
import app.models.database.transaction as db_transaction


async def get_account_transactions_from_nordigen(
    account_id: str,
    date_from: str,
    date_to: str
) -> List[nordigen_models.Transaction]:
    nordigen_repo = NordigenRepo()
    transactions = await nordigen_repo.get_account_transactions(
        account_id=account_id,
        date_from=date_from,
        date_to=date_to
    )
    return transactions


async def get_internal_transactions(
    session: AsyncSession,
    account_id: str,
    date_from: str,
    date_to: str
) -> Optional[Iterable[db_transaction.AccountTransaction]]:
    transaction_repo = TransactionRepo(session)
    transactions = await transaction_repo.get_for_account_id(
        account_id=account_id,
        date_from=date_from,
        date_to=date_to
    )
    return transactions


async def create_internal_transaction(
    session: AsyncSession,
    account_id: str,
    amount: str,
    currency: str,
    information: str,
    code: str,
    created_date: str,   # Date in format YYYY-MM-DD
    booking_date: str,   # Date in format YYYY-MM-DD
    debtor_name: Optional[str] = None
) -> db_transaction.AccountTransaction:
    transaction_repo = TransactionRepo(session)
    transaction = await transaction_repo.add(
        account_id=account_id,
        amount=amount,
        currency=currency,
        information=information,
        code=code,
        created_date=created_date,
        booking_date=booking_date,
        debtor_name=debtor_name
    )
    return transaction