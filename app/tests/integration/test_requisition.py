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
from app.repos.bank_account_repo import BankAccountRepo
from app.models.database.requisition import Requisition, RequisitionStatus


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


class TestGetBankConnection:
    @pytest.mark.asyncio
    async def test_get_all_linked_status(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        requisiiton_repo = RequisitionRepo(async_session)
        bank_account_repo = BankAccountRepo(async_session)
        for i in range(2):
            requisition = Requisition(
                id=f"requisition_id_{i}",
                user_id="test_user_id",
                institution_id=f"institution_id_{i}",
                institution_name=f"institution_name_{i}",
                link="www.redirect_link.com",
                status=RequisitionStatus.linked,
                accepted_at="2022-07-28",
                expires_at="2022-10-28",
                max_historical_days=90
            )
            async_session.add(requisition)
            await async_session.commit()
        
        for i in range(2):
            await bank_account_repo.add(
                account_id=f"account_id_{i}",
                requistion_id=f"requisition_id_{i}",
                name="Main account",
                currency="Euro"
            )
        # act
        response = test_client.get("/bank_connections")

        assert response.status_code == 200
        assert response.json() == [
            {
                'accepted_at': '2022-07-28',
                'bank_accounts':[{'account_id': 'account_id_0','currency': 'Euro','name': 'Main account'}],
                'expires_at': '2022-10-28','id': 'requisition_id_0',
                'institution_name': 'institution_name_0',
                'link': 'www.redirect_link.com',
                'max_historical_days': 90,
                'status': 'created'
            },
            {
                'accepted_at': '2022-07-28',
                'bank_accounts': [{'account_id': 'account_id_1','currency': 'Euro','name': 'Main account'}],
                'expires_at': '2022-10-28',
                'id': 'requisition_id_1',
                'institution_name': 'institution_name_1',
                'link': 'www.redirect_link.com',
                'max_historical_days': 90,
                'status': 'created'
            }
        ]