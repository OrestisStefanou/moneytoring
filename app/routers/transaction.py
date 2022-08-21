import logging
from typing import List, Optional
import uuid

from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException,status
from fastapi import APIRouter, Depends

from app.dependencies import extract_user_id_from_token, get_session
from app.controllers import transaction as transaction_controller
from app.errors.transaction import AccountNotFound
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
            to_date=to_date
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
            to_date=to_date
        )
    except AccountNotFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
