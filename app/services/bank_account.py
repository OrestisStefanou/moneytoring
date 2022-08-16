from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repos.bank_account_repo import BankAccountRepo
from app.repos.nordigen_repo import NordigenRepo
import app.models.http.nordigen as nordigen_models
import app.models.database.bank_account as db_bank_account


async def get_account_details_from_nordigen(account_id: str) -> nordigen_models.AccountDetails:
    nordigen_repo = NordigenRepo()
    account_details = await nordigen_repo.get_account_details(account_id)
    return account_details


async def create_internal_bank_account(
    session: AsyncSession,
    account_id: str,
    requistion_id: str,
    name: str,
    currency: str,
) -> db_bank_account.BankAccount:
    bank_account_repo = BankAccountRepo(session)
    bank_account = await bank_account_repo.add(
        account_id=account_id,
        requistion_id=requistion_id,
        name=name,
        currency=currency
    )
    return bank_account


async def get_requistion_bank_accounts(session: AsyncSession, requisition_id: str) -> List[db_bank_account.BankAccount]:
    bank_account_repo = BankAccountRepo(session)
    bank_accounts = await bank_account_repo.get_accounts_by_requisition_id(requisition_id)
    return list(bank_accounts)


async def get_bank_account_by_id(session: AsyncSession, account_id: str) -> Optional[db_bank_account.BankAccount]:
    bank_account_repo = BankAccountRepo(session)
    bank_account = await bank_account_repo.get(account_id)
    return bank_account
