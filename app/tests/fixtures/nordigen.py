import pytest

from pytest_httpx import HTTPXMock


@pytest.fixture(scope="function")
def nordigen_token(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://ob.nordigen.com/api/v2/token/new/",
        method="POST",
        json={
            "access": "test_access",
            "access_expires": 100,
            "refresh": "test_refresh",
            "refresh_expires": 100
        }
    )


@pytest.fixture(scope="function")
def nordigen_country_institutions(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://ob.nordigen.com/api/v2/institutions/?country=CY",
        method="GET",
        json=[
            {
                "id": "ASTROBANK_PIRBCY2N",
                "name": "AstroBank",
                "bic": "PIRBCY2N",
                "transaction_total_days": "730",
                "countries": [
                "CY"
                ],
                "logo": "astrobank_logo"
            },
            {
                "id": "BANKOFCYPRUS_BCYPCY2NXXX",
                "name": "Bank of Cyprus",
                "bic": "BCYPCY2NXXX",
                "transaction_total_days": "730",
                "countries": [
                "CY"
                ],
                "logo": "https://cdn.nordigen.com/ais/BANKOFCYPRUS_BCYPCY2NXXX.png"
            },
        ],
        status_code=200,
    )


@pytest.fixture(scope="function")
def nordigen_country_institutions_400(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://ob.nordigen.com/api/v2/institutions/?country=CY",
        method="GET",
        json={},
        status_code=400,
    )


@pytest.fixture(scope="function")
def nordigen_get_institution_by_id(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://ob.nordigen.com/api/v2/institutions/ASTROBANK_PIRBCY2N/",
        method="GET",
        json={
            "id": "ASTROBANK_PIRBCY2N",
            "name": "AstroBank",
            "bic": "PIRBCY2N",
            "transaction_total_days": "730",
            "countries": [
            "CY"
            ],
            "logo": "astrobank_logo"
        },
        status_code=200,
    )


@pytest.fixture(scope="function")
def nordigen_get_institution_by_id_not_found(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://ob.nordigen.com/api/v2/institutions/ASTROBANK_PIRBCY2N/",
        method="GET",
        json={},
        status_code=404,
    )


@pytest.fixture(scope="function")
def create_nordigen_requisition(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://ob.nordigen.com/api/v2/requisitions/",
        method="POST",
        json={
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "created": "2022-07-26T09:44:24.664Z",
            "redirect": "www.some_website.com",
            "status": "CR",
            "institution_id": "ASTROBANK_PIRBCY2N",
            "agreement": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "reference": None,
            "accounts": [],
            "user_language": "klingon",
            "link": "https://ob.nordigen.com/psd2/start/3fa85f64-5717-4562-b3fc-2c963f66afa6/anavarkos_bank",
            "ssn": "string",
            "account_selection": False,
            "redirect_immediate": False
        },
        status_code=201
    )


@pytest.fixture(scope="function")
def get_requisition_with_linked_status(httpx_mock: HTTPXMock, requisition_id: str):
    httpx_mock.add_response(
        url=f"https://ob.nordigen.com/api/v2/requisitions/{requisition_id}/",
        method="GET",
        json={
            "id": requisition_id,
            "created": "2022-07-25T19:15:20.624770Z",
            "redirect": "https://www.some_website.com",
            "status": "LN",
            "institution_id": "SANDBOXFINANCE_SFIN0000",
            "agreement": "3eef47d9-99e8-4a05-88a1-39f95ed84fad",
            "reference": "d2dee8cf-e9c3-4e72-afd6-ae5f801a3ab5",
            "accounts": [
                "7e944232-bda9-40bc-b784-660c7ab5fe78",
                "99a0bfe2-0bef-46df-bff2-e9ae0c6c5838"
            ],
            "link": "https://ob.nordigen.com/psd2/start/d2dee8cf-e9c3-4e72-afd6-ae5f801a3ab5/SANDBOXFINANCE_SFIN0000",
            "ssn": None,
            "account_selection": None,
            "redirect_immediate": None
            },
        status_code=200
    )


def get_account_details(httpx_mock: HTTPXMock, account_id: str):
    httpx_mock.add_response(
        url=f"https://ob.nordigen.com/api/v2/accounts/{account_id}/details/",
        method="GET",
        json={
            "account": {
                "resourceId": "01F3NS4YV94RA29YCH8R0F6BMF",
                "iban": "GL3343697694912188",
                "currency": "EUR",
                "ownerName": "John Doe",
                "name": "Main Account",
                "product": "Checkings",
                "cashAccountType": "CACC"
            }
        },
        status_code=200
    )
