import time
from typing import Dict,Any, List

from app import settings
from app.http.http_client import HttpClient
from app.models.http.nordigen import NordigenToken, Institution


class NordigenClient(HttpClient):
    def __init__(self) -> None:
        super().__init__(url=settings.nordigen_base_url)
        self._token: NordigenToken = None
        self._headers = None

    async def _get_access_token(self) -> NordigenToken:
        json_data = {
            "secret_id": settings.nordigen_id,
            "secret_key": settings.nordigen_key,
        }

        json_response = await self.post(
            endpoint="/token/new/",
            json=json_data
        )
        self._headers = {"Authorization": f'Bearer {json_response["access"]}'}
        """
        Nordigen returns the number of seconds that the token is valid
        so we add current timestamp to have expiration timestamp in our model
        """
        return NordigenToken(
            access=json_response["access"],
            access_expires=json_response["access_expires"] + time.time(),
            refresh=json_response["refresh"],
            refresh_expires=json_response["refresh_expires"] + time.time()
        )

    async def _check_token_expiration(self) -> None:
        current_ts = time.time()
        if (self._token is None) or (current_ts > self._token.access_expires):
            self._token = await self._get_access_token()
            return
    
    async def get_country_institutions(self,country_code: str) -> List[Institution]:
        await self._check_token_expiration()

        params = {"country": country_code}

        institutions = await self.get(
            endpoint='/institutions/',
            headers=self._headers,
            params=params,
        )
        
        return [
            Institution(
                id=institution['id'],
                name=institution['name'],
                bic=institution['bic'],
                transaction_total_days=institution['transaction_total_days'],
                logo=institution['logo']
            )
            for institution in institutions
        ]

    async def get_institution_by_id(self, _id: str) -> Institution:
        await self._check_token_expiration()

        institution = await self.get(
            endpoint=f'/institutions/{_id}/',
            headers=self._headers,
        )

        return Institution(
            id=institution['id'],
            name=institution['name'],
            bic=institution['bic'],
            transaction_total_days=institution['transaction_total_days'],
            logo=institution['logo']
        )
