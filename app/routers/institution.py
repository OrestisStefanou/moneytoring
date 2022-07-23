import logging
from typing import List

from fastapi import HTTPException,status
from fastapi import APIRouter, Depends

from app.controllers import institution as institution_controller
from app.entities import institution as institution_entities
from app.dependencies import extract_user_id_from_token
from app.errors import nordigen as nordigen_errors
from app.errors import institution as institution_errors

router = APIRouter(tags=['Institution'])

@router.get("/institutions", response_model=List[institution_entities.Institution], status_code=200)
async def get_country_institutions(country_code: str, _ = Depends(extract_user_id_from_token)):
    try:
        institutions = await institution_controller.get_country_institutions(country_code)
    except institution_errors.InvalidCountryCode:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid country code",
        )
    except nordigen_errors.NordigenFailure:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bank service is not responding, we are working on it",
        )
    except Exception as err:
        logging.exception("Unexpected error during get institutions:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )

    return institutions


@router.get("/institutions/{institution_id}", response_model=institution_entities.Institution, status_code=200)
async def get_institution_by_id(institution_id: str, _ = Depends(extract_user_id_from_token)):
    try:
        institution = await institution_controller.get_institution_by_id(institution_id)
    except institution_errors.InstitutionNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insitution not found",
        )
    except nordigen_errors.NordigenFailure:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bank service is not responding, we are working on it",
        )
    except Exception as err:
        logging.exception("Unexpected error during get institutions:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )

    return institution