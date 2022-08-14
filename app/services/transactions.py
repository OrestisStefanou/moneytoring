from typing import Iterable, List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repos.nordigen_repo import NordigenRepo
from app.repos.transaction_repo import TransactionRepo
import app.models.http.nordigen as nordigen_models
import app.models.database.transaction as db_transaction


async def fetch_and_save_account_transactions_from_nordigen(
    session: AsyncSession,
    account_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> List[nordigen_models.Transaction]:
    """
    We fetch the transactions from nordigen and save them in our database
    """
    nordigen_repo = NordigenRepo()
    transactions = await nordigen_repo.get_account_transactions(
        account_id=account_id,
        date_from=from_date,
        date_to=to_date
    )
    for transaction in transactions:
        await create_internal_transaction(
            session=session,
            account_id=account_id,
            amount=transaction.transaction_amount.amount,
            currency=transaction.transaction_amount.currency,
            information=transaction.remittance_information_unstructured,
            code=transaction.bank_transaction_code,
            created_date=transaction.value_date,
            booking_date=transaction.booking_date,
            debtor_name=transaction.debtor_name
        )
    return transactions


async def get_internal_transactions(
    session: AsyncSession,
    account_id: str,
    from_date: str,
    to_date: str
) -> Optional[Iterable[db_transaction.AccountTransaction]]:
    transaction_repo = TransactionRepo(session)
    transactions = await transaction_repo.get_for_account_id(
        account_id=account_id,
        date_from=from_date,
        date_to=to_date
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