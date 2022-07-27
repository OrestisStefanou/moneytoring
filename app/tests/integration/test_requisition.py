import pytest

from app.tests.fixtures.nordigen import (
    nordigen_token,
    create_nordigen_requisition,
    nordigen_get_institution_by_id,
    nordigen_get_institution_by_id_not_found
)

from app.tests.fixtures.app_fixtures import (
    test_client,
    test_db,
    async_session,
    authenticated_user,
    event_loop,
    assert_all_responses_were_requested
)
from app.repos.requisition_repo import RequisitionRepo


class TestCreateBankConnection:
    @pytest.mark.asyncio
    async def test_success(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        nordigen_token,
        create_nordigen_requisition,
        nordigen_get_institution_by_id
    ):
        response = test_client.post(
            "/bank_connections",
            json={"institution_id": "ASTROBANK_PIRBCY2N", "redirect_uri": "www.some_website.com"}
        )

        assert response.status_code == 201
        assert response.json() == {
            'accepted_at': None,
            'bank_accounts': None,
            'expires_at': None,
            'id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'institution_name': 'AstroBank',
            'link': 'https://ob.nordigen.com/psd2/start/3fa85f64-5717-4562-b3fc-2c963f66afa6/anavarkos_bank',
            'max_historical_days': None,
            'status': 'pending'
        }

        # Assert that the internal requisition was created
        requisition_repo = RequisitionRepo(async_session)
        requisition = await requisition_repo.get("3fa85f64-5717-4562-b3fc-2c963f66afa6")
        assert requisition is not None
        assert requisition.accepted_at is None
        assert requisition.status == "not_linked"
        assert requisition.expires_at is None
        assert requisition.max_historical_days is None
        assert requisition.institution_name == "AstroBank"
        assert requisition.user_id == "test_user_id"

    @pytest.mark.asyncio
    async def test_institution_not_found(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        nordigen_token,
        nordigen_get_institution_by_id_not_found
    ):
        response = test_client.post(
            "/bank_connections",
            json={"institution_id": "ASTROBANK_PIRBCY2N", "redirect_uri": "www.some_website.com"}
        )

        assert response.status_code == 400
        assert response.json()['detail'] == "Insitution with given id doesn't exist"

        # Assert that the internal requisition was created
        requisition_repo = RequisitionRepo(async_session)
        requisitions = await requisition_repo.get_all()
        assert requisitions == []
