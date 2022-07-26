import logging
from typing import List
import uuid

from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException,status
from fastapi import APIRouter, Depends

from app.controllers import requisition as requisition_controller
from app.entities import requisition as requisition_entities
from app.errors import nordigen as nordigen_errors
from app.errors import institution as institution_errros
from app.errors import requisition as requisition_errors
from app.dependencies import get_session, extract_user_id_from_token

router = APIRouter(tags=['Bank Connection'])

@router.post(
    "/bank_connections",
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


@router.delete(
    "/bank_connections/{bank_connection_id}",
    response_model=None,
    status_code=200
)
async def delete_bank_connection(
    bank_connection_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(extract_user_id_from_token)
):
    try:
        await requisition_controller.delete_bank_connection(session=session, bank_connection_id=str(bank_connection_id))
    except requisition_errors.BankConnectionNotFound:
        raise  HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bank connection with given id doesn't exist",
        )
    except nordigen_errors.NordigenFailure:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bank service is not responding, we are working on it",
        )
    except Exception as err:
        logging.exception("Unexpected error during deleting bank connection:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )


@router.put(
    "/bank_connections/{bank_connection_id}",
    response_model=None,
    status_code=201
)
async def update_expired_bank_connection(
    bank_connection_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(extract_user_id_from_token)
):
    try:
        await requisition_controller.update_expired_bank_connection(
            session=session,
            bank_connection_id=bank_connection_id,
            user_id=user_id
        )
    except requisition_errors.BankConnectionNotFound:
        raise  HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bank connection with given id doesn't exist",
        )
    except nordigen_errors.NordigenFailure:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bank service is not responding, we are working on it",
        )
    except Exception as err:
        logging.exception("Unexpected error during updating expired bank connection:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )
