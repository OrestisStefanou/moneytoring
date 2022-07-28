import pytest
from pytest_httpx import HTTPXMock

from app.tests.fixtures.nordigen import (
    nordigen_token,
    mock_nordigen_get_country_institutions,
    nordigen_country_institutions_400,
    nordigen_get_institution_by_id,
    nordigen_get_institution_by_id_not_found
)
from app.tests.fixtures.app_fixtures import (
    test_client,
    authenticated_user,
    event_loop,
    assert_all_responses_were_requested
)


class TestGetCountryInstitutions:
    def test_success(
        self,
        test_client,
        httpx_mock: HTTPXMock,
        authenticated_user,
        nordigen_token,
        nordigen_country_institutions,
    ):
        # Prepare
        mock_nordigen_get_country_institutions(httpx_mock)
        response = test_client.get("/institutions?country_code=CY")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": "ASTROBANK_PIRBCY2N",
                "name": "AstroBank",
                "bic": "PIRBCY2N",
                "transaction_total_days": 730,
                "logo": "astrobank_logo"
            },
            {
                "id": "BANKOFCYPRUS_BCYPCY2NXXX",
                "name": "Bank of Cyprus",
                "bic": "BCYPCY2NXXX",
                "transaction_total_days": 730,
                "logo": "https://cdn.nordigen.com/ais/BANKOFCYPRUS_BCYPCY2NXXX.png"
            },
        ]

    def test_invalid_country_code(
        self,
        test_client,
        authenticated_user,
        nordigen_token,
        nordigen_country_institutions_400
    ):
        response = test_client.get("/institutions?country_code=CY")
        assert response.status_code == 400
        assert response.json() == {'detail': 'Invalid country code'}

    def test_unauthorized(
        self,
        test_client,
    ):
        response = test_client.get("/institutions?country_code=CY")
        assert response.status_code == 401


class TestGetInstitutionById:
    def test_success(
        self,
        test_client,
        authenticated_user,
        nordigen_token,
        nordigen_get_institution_by_id,
    ):
        response = test_client.get("/institutions/ASTROBANK_PIRBCY2N")
        assert response.status_code == 200
        assert response.json() == {
            "id": "ASTROBANK_PIRBCY2N",
            "name": "AstroBank",
            "bic": "PIRBCY2N",
            "transaction_total_days": 730,
            "logo": "astrobank_logo"
        }

    def test_not_found(
        self,
        test_client,
        authenticated_user,
        nordigen_token,
        nordigen_get_institution_by_id_not_found
    ):
        response = test_client.get("/institutions/ASTROBANK_PIRBCY2N")
        assert response.status_code == 404
        assert response.json() == {'detail': 'Insitution not found'}

    def test_unauthorized(
        self,
        test_client,
    ):
        response = test_client.get("/institutions/ASTROBANK_PIRBCY2N")
        assert response.status_code == 401
