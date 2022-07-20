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