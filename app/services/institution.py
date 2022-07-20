from typing import List, Optional
from app.models.http.nordigen import Institution

from app.repos.nordigen_repo import NordigenRepo


async def get_country_institutions(country_code: str) -> Optional[List[Institution]]:
    nordigen_repo = NordigenRepo()
    institutions = await nordigen_repo.get_country_institutions(country_code)
    return institutions


async def get_institution_by_id(_id: str) -> Optional[Institution]:
    nordigen_repo = NordigenRepo()
    institution = await nordigen_repo.get_institution_by_id(_id)
    return institution