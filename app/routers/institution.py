import logging
from typing import List
from fastapi import HTTPException,status
from fastapi import APIRouter, Depends

from app.controllers import institution as institution_controller
from app.entities import institution as institution_entities
from app.dependencies import extract_user_id_from_token
from app.errors import nordigen as nordigen_erros
from app.errors import institution as institution_errros

router = APIRouter()

@router.get("/institutions", response_model=List[institution_entities.Institution], tags=['Institution'], status_code=200)
async def get_country_institutions(country_code: str, user_id = Depends(extract_user_id_from_token)):
    try:
        institutions = await institution_controller.get_country_institutions(country_code)
    except institution_errros.InvalidCountryCode:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid country code",
        )
    except nordigen_erros.NordigenFailure:
        raise HTTPException(
            status_code=503,
            detail="Bank service is not responding, we are working on it",
        )
    except Exception as err:
        logging.exception("Unexpected error during get institutions:", str(err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, we are working on it",
        )

    return institutions