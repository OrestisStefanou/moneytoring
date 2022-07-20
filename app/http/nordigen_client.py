import logging
import time
from typing import Dict,Any, List, Optional

from app import settings
from app.http.http_client import HttpClient
from app.models.http.nordigen import NordigenToken, Institution
from app.errors.nordigen import NordigenFailure
from app.errors.http import HttpRequestError

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
        
        try:
            response = await self.post(
                endpoint="/token/new/",
                json=json_data
            )
        except HttpRequestError as err:
            logging.error("Http call to get nordigen access token failed with:", str(err))
            return

        token = response.json()
        self._headers = {"Authorization": f'Bearer {token["access"]}'}
        """
        Nordigen returns the number of seconds that the token is valid
        so we add current timestamp to have expiration timestamp in our model
        """
        return NordigenToken(
            access=token["access"],
            access_expires=token["access_expires"] + time.time(),
            refresh=token["refresh"],
            refresh_expires=token["refresh_expires"] + time.time()
        )

    async def _check_token_expiration(self) -> None:
        current_ts = time.time()
        if (self._token is None) or (current_ts > self._token.access_expires):
            self._token = await self._get_access_token()
            return
    
    async def get_country_institutions(self,country_code: str) -> Optional[List[Institution]]:
        await self._check_token_expiration()

        params = {"country": country_code}

        try:
            response = await self.get(
                endpoint='/institutions/',
                headers=self._headers,
                params=params,
            )
        except HttpRequestError as err:
            logging.error("Http call to get country institutions failed with:", str(err))
            raise NordigenFailure("Call to get country institutions failed")

        if response.status_code == 400:
            return None

        institutions = response.json()
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

    async def get_institution_by_id(self, _id: str) -> Optional[Institution]:
        await self._check_token_expiration()

        try:
            response = await self.get(
                endpoint=f'/institutions/{_id}/',
                headers=self._headers,
            )
        except HttpRequestError as err:
            logging.error("Http call to get institution by id failed with:", str(err))
            raise NordigenFailure("Call to get institution by id failed")

        if response.status_code == 404:
            raise None

        institution = response.json()

        return Institution(
            id=institution['id'],
            name=institution['name'],
            bic=institution['bic'],
            transaction_total_days=institution['transaction_total_days'],
            logo=institution['logo']
        )
