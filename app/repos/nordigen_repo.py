from typing import List, Optional
from app.repos.http_repo import HTTPRepo
from app.dependencies import nordigen_client
from app.models.http.nordigen import (
    AccountDetails,
    Agreement,
    Institution,
    Requisition
)


class NordigenRepo(HTTPRepo):
    def __init__(self) -> None:
        super().__init__(client=nordigen_client)
    
    async def get_country_institutions(self, country_code: str) -> Optional[List[Institution]]:
        institutions = await self._client.get_country_institutions(country_code)
        return institutions
    
    async def get_institution_by_id(self, _id: str) -> Optional[Institution]:
        institution = await self._client.get_institution_by_id(_id)
        return institution

    async def create_requisition(self, institution_id: str, redirect_uri: str) -> Requisition:
        requisition = await self._client.create_requisition(institution_id, redirect_uri)
        return requisition
    
    async def get_requisition_by_id(self, _id: str) -> Optional[Requisition]:
        requisition = await self._client.get_requisition_by_id(_id)
        return requisition

    async def get_account_details(self, account_id: str) -> Optional[AccountDetails]:
        account_details = await self._client.get_account_details(account_id)
        return account_details
    
    async def get_agreement_by_id(self, _id: str) -> Optional[Agreement]:
        agreement = await self._client.get_agreement_by_id(_id)
        return agreement