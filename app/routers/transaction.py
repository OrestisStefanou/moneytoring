import logging
from typing import List, Optional
import uuid

from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException,status
from fastapi import APIRouter, Depends

from app.dependencies import extract_user_id_from_token, get_session
from app.controllers import transaction as transaction_controller
from app.errors import transaction as transaction_errros
import app.entities.transaction as transaction_entities
import app.utils.transaction as transaction_utils

router = APIRouter(tags=["Account Transactions"])

@router.get(
    "/account_transactions",
    response_model=List[transaction_entities.Transaction],
    status_code=200
)
async def get_user_transactions(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[transaction_entities.TransactionCategory] = None,
    custom_category: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(extract_user_id_from_token)
):
    # Validation checks for the dates format
    if from_date:
        if transaction_utils.validate_date_format(from_date) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date must be in format YYYY-MM-DD",
            )

    if to_date:
        if transaction_utils.validate_date_format(to_date) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date must be in format YYYY-MM-DD",
            )

    try:
        transactions = await transaction_controller.get_user_transactions(
            session=session,
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            category=category,
            custom_category=custom_category
        )
    except Exception as err:
        logging.exception("Unexpected error during get user transactions:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )

    return [
        transaction_entities.Transaction(**internal_transaction.dict())
        async for internal_transaction in transactions
    ]


@router.get(
    "/account_transactions/{account_id}",
    response_model=List[transaction_entities.Transaction],
    status_code=200
)
async def get_account_transactions(
    account_id: uuid.UUID,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[transaction_entities.TransactionCategory] = None,
    custom_category: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(extract_user_id_from_token)
):
    # Validation checks for the dates format
    if from_date:
        if transaction_utils.validate_date_format(from_date) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date must be in format YYYY-MM-DD",
            )

    if to_date:
        if transaction_utils.validate_date_format(to_date) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date must be in format YYYY-MM-DD",
            )

    try:
        transactions = await transaction_controller.get_account_transactions(
            session=session,
            account_id=str(account_id),
            from_date=from_date,
            to_date=to_date,
            category=category,
            custom_category=custom_category
        )
    except transaction_errros.AccountNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account with given id not found",
        )
    except Exception as err:
        logging.exception("Unexpected error during get account transactions:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )

    return [
        transaction_entities.Transaction(**internal_transaction.dict())
        for internal_transaction in transactions
    ]


@router.put(
    "/account_transactions/{transaction_id}/category",
    response_model=transaction_entities.Transaction,
    status_code=200
)
async def add_transaction_category(
    transaction_id: str,
    category: transaction_entities.TransactionCategory,
    set_all: bool = False,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(extract_user_id_from_token)
):
    try:
        transaction = await transaction_controller.set_transaction_category(
            session=session,
            transaction_id=transaction_id,
            category=category,
            set_all=set_all
        )
    except transaction_errros.TransactionNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction with given id not found",
        )
    except Exception as err:
        logging.exception("Unexpected error during add_transaction_category:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )

    return transaction_entities.Transaction(**transaction.dict())


@router.put(
    "/account_transactions/{transaction_id}/custom_category",
    response_model=transaction_entities.Transaction,
    status_code=200
)
async def add_transaction_custom_category(
    transaction_id: str,
    category: str,
    set_all: bool = False,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(extract_user_id_from_token)
):
    try:
        transaction = await transaction_controller.set_transaction_custom_category(
            session=session,
            transaction_id=transaction_id,
            category=category,
            set_all=set_all
        )
    except transaction_errros.TransactionNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction with given id not found",
        )
    except Exception as err:
        logging.exception("Unexpected error during add_transaction_custom_category:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )

    return transaction_entities.Transaction(**transaction.dict())


@router.get(
    "/transactions/total_spent",
    response_model=transaction_entities.TotalSpentResponse,
    status_code=200
)
async def get_user_total_spent(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[transaction_entities.TransactionCategory] = None,
    custom_category: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(extract_user_id_from_token)
):
    # Validation checks for the dates format
    if from_date:
        if transaction_utils.validate_date_format(from_date) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date must be in format YYYY-MM-DD",
            )

    if to_date:
        if transaction_utils.validate_date_format(to_date) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date must be in format YYYY-MM-DD",
            )

    try:
        total_spent = await transaction_controller.get_user_total_spent_amount(
            session=session,
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            category=category,
            custom_category=custom_category
        )
    except Exception as err:
        logging.exception("Unexpected error during get user transactions:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )

    return transaction_entities.TotalSpentResponse(
        total_spent=total_spent
    )


@router.get(
    "/account_transactions/{account_id}/total_spent",
    response_model=transaction_entities.TotalSpentResponse,
    status_code=200
)
async def get_account_total_spent(
    account_id: uuid.UUID,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[transaction_entities.TransactionCategory] = None,
    custom_category: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(extract_user_id_from_token)
):
    # Validation checks for the dates format
    if from_date:
        if transaction_utils.validate_date_format(from_date) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date must be in format YYYY-MM-DD",
            )

    if to_date:
        if transaction_utils.validate_date_format(to_date) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date must be in format YYYY-MM-DD",
            )

    try:
        total_spent = await transaction_controller.get_account_total_spent_amount(
            session=session,
            account_id=str(account_id),
            from_date=from_date,
            to_date=to_date,
            category=category,
            custom_category=custom_category
        )
    except transaction_errros.AccountNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account with given id not found",
        )
    except Exception as err:
        logging.exception("Unexpected error during get account total spent amount:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )

    return transaction_entities.TotalSpentResponse(
        total_spent=total_spent
    )


@router.get(
    "/transactions/total_credited",
    response_model=transaction_entities.TotalCreditedResponse,
    status_code=200
)
async def get_user_total_credited(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[transaction_entities.TransactionCategory] = None,
    custom_category: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(extract_user_id_from_token)
):
    # Validation checks for the dates format
    if from_date:
        if transaction_utils.validate_date_format(from_date) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date must be in format YYYY-MM-DD",
            )

    if to_date:
        if transaction_utils.validate_date_format(to_date) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date must be in format YYYY-MM-DD",
            )

    try:
        total_credited = await transaction_controller.get_user_total_credited_amount(
            session=session,
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            category=category,
            custom_category=custom_category
        )
    except Exception as err:
        logging.exception("Unexpected error during get user transactions:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )

    return transaction_entities.TotalCreditedResponse(
        total_credited=total_credited
    )


@router.get(
    "/account_transactions/{account_id}/total_credited",
    response_model=transaction_entities.TotalCreditedResponse,
    status_code=200
)
async def get_account_total_credited(
    account_id: uuid.UUID,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    category: Optional[transaction_entities.TransactionCategory] = None,
    custom_category: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(extract_user_id_from_token)
):
    # Validation checks for the dates format
    if from_date:
        if transaction_utils.validate_date_format(from_date) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date must be in format YYYY-MM-DD",
            )

    if to_date:
        if transaction_utils.validate_date_format(to_date) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date must be in format YYYY-MM-DD",
            )

    try:
        total_credited = await transaction_controller.get_account_total_credited_amount(
            session=session,
            account_id=str(account_id),
            from_date=from_date,
            to_date=to_date,
            category=category,
            custom_category=custom_category
        )
    except transaction_errros.AccountNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account with given id not found",
        )
    except Exception as err:
        logging.exception("Unexpected error during get account total spent amount:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )

    return transaction_entities.TotalCreditedResponse(
        total_credited=total_credited
    )
