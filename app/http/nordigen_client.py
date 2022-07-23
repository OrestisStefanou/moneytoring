import logging
import time
from typing import List, Optional

from app import settings
from app.http.http_client import HttpClient
from app.models.http.nordigen import (
    NordigenToken,
    Institution,
    Requisition,
    Agreement,
    AccountDetails
)
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
            return None

        institution = response.json()

        return Institution(
            id=institution['id'],
            name=institution['name'],
            bic=institution['bic'],
            transaction_total_days=institution['transaction_total_days'],
            logo=institution['logo']
        )

    async def get_agreement_by_id(self, _id: str) -> Optional[Agreement]:
        await self._check_token_expiration()

        try:
            response = await self.get(
                endpoint=f'/agreements/enduser/{_id}/',
                headers=self._headers,
            )
        except HttpRequestError as err:
            logging.error("Http call to get agreement by id failed with:", str(err))
            raise NordigenFailure("Call to get agreement by id failed")

        if response.status_code == 404:
            return None

        agreement = response.json()

        return Agreement(
            id=agreement['id'],
            created=agreement['created'],
            max_historical_days=agreement['max_historical_days'],
            access_valid_for_days=agreement['access_valid_for_days'],
            access_scope=agreement['access_scope'],
            accepted=agreement['accepted']
        )

    async def get_account_details(self, account_id: str) -> Optional[AccountDetails]:
        await self._check_token_expiration()

        try:
            response = await self.get(
                endpoint=f'/accounts/{account_id}/details/',
                headers=self._headers,
            )
        except HttpRequestError as err:
            logging.error("Http call to get account details failed with:", str(err))
            raise NordigenFailure("Call to get account details failed")

        if response.status_code == 404:
            return None

        account_details = response.json()

        return AccountDetails(
            currency=account_details['currency'],
            name=account_details['name'],
            product=account_details['product']
        )

    async def create_requisition(self, institution_id: str, redirect_uri: str) -> Requisition:
        json_data = {
            "redirect": redirect_uri,
            "institution_id": institution_id,
        }
        
        try:
            response = await self.post(
                endpoint="/requisitions/",
                json=json_data,
                headers=self._headers
            )
        except HttpRequestError as err:
            logging.error("Http call to create nordigen requisition failed with:", str(err))
            raise NordigenFailure("Call to create requisition failed")

        requisition = response.json()
        return Requisition(
            id=requisition['id'],
            created=requisition['created'],
            redirect=requisition['redirect'],
            status=requisition['status'],
            institution_id=requisition['institution_id'],
            agreement_id=requisition['agreement'],
            accounts=requisition['accounts'],
            link=requisition['link']
        )

    async def get_requisition_by_id(self, _id: str) -> Optional[Requisition]:
        await self._check_token_expiration()

        try:
            response = await self.get(
                endpoint=f'/requisitions/{_id}/',
                headers=self._headers,
            )
        except HttpRequestError as err:
            logging.error("Http call to get requisition by id failed with:", str(err))
            raise NordigenFailure("Call to get requisition failed")

        if response.status_code == 404:
            return None

        requisition = response.json()

        return Requisition(
            id=requisition['id'],
            created=requisition['created'],
            redirect=requisition['redirect'],
            status=requisition['status']['long'],
            institution_id=requisition['institution_id'],
            agreement_id=requisition['agreement'],
            accounts=requisition['accounts'],
            link=requisition['link']
        )
