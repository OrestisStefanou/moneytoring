from datetime import datetime, timedelta
from decimal import Decimal
from typing import AsyncIterable, Iterable, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

import app.services.transactions as transaction_service
import app.errors.transaction as transaction_errors
import app.models.database.transaction as transaction_models
import app.services.bank_account as bank_account_service


async def get_user_transactions(
    session: AsyncSession,
    user_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[transaction_models.TransactionCategory] = None,
    custom_category: Optional[str] = None
) -> AsyncIterable[transaction_models.AccountTransaction]:
    if from_date is None:
        # If from date is not given we set it to 90 days prior from
        # current date as this is max historical days we have access to
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    if to_date is None:
        to_date = datetime.now().strftime("%Y-%m-%d")


    transactions = await transaction_service.get_user_transactions(
        session=session,
        user_id=user_id,
        from_date=from_date,
        to_date=to_date,
        category=category,
        custom_category=custom_category
    )

    return transactions


async def get_account_transactions(
    session: AsyncSession,
    account_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[transaction_models.TransactionCategory] = None,
    custom_category: Optional[str] = None,
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

    transactions = await transaction_service.get_account_transactions(
        session=session,
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
        category=category,
        custom_category=custom_category
    )

    return transactions


async def set_transaction_category(
    session: AsyncSession,
    transaction_id: str,
    category: transaction_models.TransactionCategory,
    set_all: bool = False
) -> transaction_models.AccountTransaction:
    updated_transaction = await transaction_service.set_transaction_category(
        session=session,
        transaction_id=transaction_id,
        category=category,
        set_all=set_all
    )

    if updated_transaction is None:
        raise transaction_errors.TransactionNotFound()
    
    return updated_transaction


async def set_transaction_custom_category(
    session: AsyncSession,
    transaction_id: str,
    category: str,
    set_all: bool = False
) -> transaction_models.AccountTransaction:
    updated_transaction = await transaction_service.set_transaction_custom_category(
        session=session,
        transaction_id=transaction_id,
        custom_category=category,
        set_all=set_all
    )

    if updated_transaction is None:
        raise transaction_errors.TransactionNotFound()
    
    return updated_transaction


async def get_account_total_spent_amount(
    session: AsyncSession,
    account_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[transaction_models.TransactionCategory] = None,
    custom_category: Optional[str] = None,
) -> Decimal:
    bank_account = await bank_account_service.get_bank_account_by_id(session, account_id)
    if bank_account is None:
        raise transaction_errors.AccountNotFound()
    
    if from_date is None:
        # If from date is not given we set it to 90 days prior from
        # current date as this is max historical days we have access to
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    if to_date is None:
        to_date = datetime.now().strftime("%Y-%m-%d")
    
    total_spent = await transaction_service.get_total_spent_amount_of_account(
        session=session,
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
        category=category,
        custom_category=custom_category
    )

    return total_spent


async def get_account_total_credited_amount(
    session: AsyncSession,
    account_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[transaction_models.TransactionCategory] = None,
    custom_category: Optional[str] = None,
) -> Decimal:
    bank_account = await bank_account_service.get_bank_account_by_id(session, account_id)
    if bank_account is None:
        raise transaction_errors.AccountNotFound()
    
    if from_date is None:
        # If from date is not given we set it to 90 days prior from
        # current date as this is max historical days we have access to
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    if to_date is None:
        to_date = datetime.now().strftime("%Y-%m-%d")
    
    total_credited = await transaction_service.get_total_credited_amount_of_account(
        session=session,
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
        category=category,
        custom_category=custom_category
    )

    return total_credited


async def get_user_total_spent_amount(
    session: AsyncSession,
    user_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[transaction_models.TransactionCategory] = None,
    custom_category: Optional[str] = None
) -> AsyncIterable[transaction_models.AccountTransaction]:
    if from_date is None:
        # If from date is not given we set it to 90 days prior from
        # current date as this is max historical days we have access to
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    if to_date is None:
        to_date = datetime.now().strftime("%Y-%m-%d")


    total_spent = await transaction_service.get_total_spent_amount_of_user(
        session=session,
        user_id=user_id,
        from_date=from_date,
        to_date=to_date,
        category=category,
        custom_category=custom_category
    )

    return total_spent


async def get_user_total_credited_amount(
    session: AsyncSession,
    user_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[transaction_models.TransactionCategory] = None,
    custom_category: Optional[str] = None
) -> AsyncIterable[transaction_models.AccountTransaction]:
    if from_date is None:
        # If from date is not given we set it to 90 days prior from
        # current date as this is max historical days we have access to
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    if to_date is None:
        to_date = datetime.now().strftime("%Y-%m-%d")


    total_credited = await transaction_service.get_total_credited_amount_of_user(
        session=session,
        user_id=user_id,
        from_date=from_date,
        to_date=to_date,
        category=category,
        custom_category=custom_category
    )

    return total_credited
