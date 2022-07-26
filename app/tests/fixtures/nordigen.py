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
            "institution_id": "anavarkos_bank",
            "agreement": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "reference": None,
            "accounts": [],
            "user_language": "klingon",
            "link": "https://ob.nordigen.com/psd2/start/3fa85f64-5717-4562-b3fc-2c963f66afa6/anavarkos_bank",
            "ssn": "string",
            "account_selection": False,
            "redirect_immediate": False
        },
        status_code=200
    )
