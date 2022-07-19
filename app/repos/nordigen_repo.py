from typing import List, Optional
from app.repos.http_repo import HTTPRepo
from app.dependencies import nordigen_client
from app.models.http.nordigen import Institution

class NordigenRepo(HTTPRepo):
    def __init__(self) -> None:
        super().__init__(client=nordigen_client)
    
    async def get_country_institutions(self, country_code: str) -> Optional[List[Institution]]:
        institutions = await self._client.get_country_institutions(country_code)
        return institutions
    
    async def get_institution_by_id(self, _id) -> Optional[Institution]:
        institution = await self._client.get_institution_by_id(_id)
        return institution