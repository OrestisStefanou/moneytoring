import logging
from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException,status
from fastapi import APIRouter, Depends

from app.controllers import requisition as requisition_controller
from app.entities import requisition as requisition_entities
from app.errors import nordigen as nordigen_errors
from app.errors import institution as institution_errros
from app.dependencies import get_session, extract_user_id_from_token

router = APIRouter(tags=['Bank Connection'])

@router.post(
    "/bank_connection",
    response_model=requisition_entities.BankConnection, 
    status_code=201,
)
async def create_bank_connection(
    body_data: requisition_entities.CreateRequisitionBody,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(extract_user_id_from_token)
):
    try:
        bank_connection = await requisition_controller.create_bank_connection(
            session=session,
            user_id=user_id,
            institution_id=body_data.institution_id,
            redirect_uri=body_data.redirect_uri
        )
    except institution_errros.InstitutionNotFound:
        raise  HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insitution with given id doesn't exist",
        )
    except nordigen_errors.NordigenFailure:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bank service is not responding, we are working on it",
        )
    except Exception as err:
        logging.exception("Unexpected error during creating bank connection:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )
    
    return bank_connection


@router.get(
    "/bank_connections",
    response_model=List[requisition_entities.BankConnection], 
    status_code=200,
)
async def get_bank_connections_of_user(
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(extract_user_id_from_token)
):
    try:
        bank_connections = await requisition_controller.get_user_bank_connections(
            session=session,
            user_id=user_id
        )
    except nordigen_errors.NordigenFailure:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bank service is not responding, we are working on it",
        )
    except Exception as err:
        logging.exception("Unexpected error during creating bank connection:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )
    
    return bank_connections
