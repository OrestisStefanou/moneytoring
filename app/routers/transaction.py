import logging
from typing import Optional
import uuid

from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException,status
from fastapi import APIRouter, Depends

from app.dependencies import extract_user_id_from_token, get_session
from app.controllers import transaction as transaction_controller


router = APIRouter(tags=["Account Transactions"])

@router.get(
    "/account_transactions/{account_id}",
    response_model=str,
    status_code=200
)
async def get_account_transactions(
    account_id: uuid.UUID,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(extract_user_id_from_token)
):
    try:
        transactions = await transaction_controller.get_account_transactions(
            account_id=account_id,
            from_date=from_date,
            to_date=to_date
        )
    except Exception as err:
        logging.exception("Unexpected error during deleting bank connection:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )
