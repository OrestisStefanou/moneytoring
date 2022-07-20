from typing import List
from app.models.http.nordigen import Institution
from app.services import institution as institution_serice
from app.errors.institution import InvalidCountryCode, InstitutionNotFound


async def get_country_institutions(country_code: str) -> List[Institution]:
    institutions = await institution_serice.get_country_institutions(country_code)

    if institutions is None:
        raise InvalidCountryCode()
    
    return institutions


async def get_institution_by_id(_id: str) -> Institution:
    institution = await institution_serice.get_institution_by_id(_id)

    if institution is None:
        raise InstitutionNotFound()
    
    return institution
