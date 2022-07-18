import time
from typing import Dict,Any

from app import settings
from app.http.http_client import HttpClient
from app.models.http.nordigen import NordigenToken


class NordigenClient(HttpClient):
    def __init__(self) -> None:
        super().__init__(url=settings.nordigen_base_url)
        self._token: NordigenToken = None
        self._headers = None

    async def _get_access_token(self) -> NordigenToken:
        json_data = {
            "secret_id": settings.nordigen_id,
            "secret_key": settings.nordigen_id,
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
    
    # async def get_available_banks(self,country_code: str) -> Dict[str,Any]:
    #     await self._check_token_expiration()
    #     url = f"{NORDIGEN_BASE_URL}/institutions/"
    #     headers = {"Authorization": f"Bearer {self.token.access}"}
    #     params = {"country": country_code}

    #     json_response = await make_request(
    #         method="GET",
    #         url=url,
    #         headers=headers,
    #         params=params,
    #     )
    #     return json_response

    # async def get_bank_by_id(self,bank_id) -> Dict[str,Any]:
    #     await self._check_token_expiration()
    #     url = f"{NORDIGEN_BASE_URL}/institutions/{bank_id}/"
    #     headers = {"Authorization": f"Bearer {self.token.access}"}

    #     json_response = await make_request(
    #         method="GET",
    #         url=url,
    #         headers=headers,
    #     )
    #     return json_response
    
    # async def get_agreement_by_id(self,agreement_id: str) -> Dict[str,Any]:
    #     pass
    
    # async def create_bank_link(self, bank_id: str, redirect: str):
    #     await self._check_token_expiration()
    #     url = f"{NORDIGEN_BASE_URL}/requisitions/"
    #     headers = {"Authorization": f"Bearer {self.token.access}"}

    #     json_response = await make_request(
    #         method="POST",
    #         url=url,
    #         headers=headers,
    #         json={
    #             "redirect": redirect,
    #             "institution_id": bank_id
    #         }
    #     )
    #     return json_response
    
    # async def get_bank_link_by_id(self):
    #     pass