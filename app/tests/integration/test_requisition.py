import pytest
from pytest_httpx import HTTPXMock

from app.tests.fixtures.nordigen import (
    nordigen_token,
    mock_create_nordigen_requisition,
    mock_nordigen_get_institution_by_id,
    mock_nordigen_get_institution_by_id_not_found,
    mock_get_requisition_with_linked_status,
    mock_get_account_details,
    mock_get_nordigen_agreement,
    mock_delete_nordigen_requisition,
    mock_delete_nordigen_requisition_not_found
)

from app.tests.fixtures.app_fixtures import (
    test_client,
    test_db,
    async_session,
    authenticated_user,
    event_loop,
    assert_all_responses_were_requested,
)
from app.repos.requisition_repo import RequisitionRepo
from app.repos.bank_account_repo import BankAccountRepo
from app.repos.app_user_repo import AppUserRepo
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
        httpx_mock: HTTPXMock
    ):
        # Prepare
        mock_create_nordigen_requisition(httpx_mock, "ASTROBANK_PIRBCY2N", "1b147a75-1a54-45b7-157d-ca1e2e18d231")
        mock_nordigen_get_institution_by_id(httpx_mock, "ASTROBANK_PIRBCY2N", "Astrobank")

        # Act
        response = test_client.post(
            "/bank_connections",
            json={"institution_id": "ASTROBANK_PIRBCY2N", "redirect_uri": "www.some_website.com"}
        )

        # Assert
        assert response.status_code == 201
        assert response.json() == {
            'accepted_at': None,
            'bank_accounts': None,
            'expires_at': None,
            'id': "1b147a75-1a54-45b7-157d-ca1e2e18d231",
            'institution_name': 'Astrobank',
            'link': 'https://ob.nordigen.com/psd2/start/3fa85f64-5717-4562-b3fc-2c963f66afa6/anavarkos_bank',
            'max_historical_days': None,
            'status': 'pending'
        }

        # Assert that the internal requisition was created
        requisition_repo = RequisitionRepo(async_session)
        requisition = await requisition_repo.get("1b147a75-1a54-45b7-157d-ca1e2e18d231")
        assert requisition is not None
        assert requisition.accepted_at is None
        assert requisition.status == "not_linked"
        assert requisition.expires_at is None
        assert requisition.max_historical_days is None
        assert requisition.institution_name == "Astrobank"
        assert requisition.user_id == "test_user_id"

    @pytest.mark.asyncio
    async def test_institution_not_found(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        nordigen_token,
        httpx_mock: HTTPXMock
    ):
        # Prepare
        mock_nordigen_get_institution_by_id_not_found(httpx_mock, "ANAVARKOS_BANK")
        
        # Act
        response = test_client.post(
            "/bank_connections",
            json={"institution_id": "ANAVARKOS_BANK", "redirect_uri": "www.some_website.com"}
        )
        
        # Assert
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

        # Act
        response = test_client.get("/bank_connections")

        # Assert
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

    @pytest.mark.asyncio
    async def test_get_not_linked_status(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        httpx_mock: HTTPXMock
    ):
        # Prepare
        # Create internal requisition with not_linked status
        requisition_repo = RequisitionRepo(async_session)
        await requisition_repo.add(
            _id="requisition_id",
            user_id="test_user_id",
            institution_id="institution_id",
            institution_name="ANAVARKOS BANK",
            link="www.redirect_link.com"
        )

        # Mock nordigen responses
        mock_get_requisition_with_linked_status(
            httpx_mock=httpx_mock,
            requisition_id="requisition_id",
            institution_id="institution_id",
            accounts=["account1_id", "account2_id"],
            agreement_id="agreement_id"            
        )

        mock_get_nordigen_agreement(
            httpx_mock=httpx_mock,
            agreement_id="agreement_id"
        )

        for i in range(1,3):
            mock_get_account_details(
                httpx_mock=httpx_mock,
                account_id=f"account{i}_id"
            )

        # Act
        response = test_client.get("/bank_connections")

        # Assert
        # Make sure that the internal requisition is updated
        internal_requisition = await requisition_repo.get("requisition_id")
        assert internal_requisition.status == "linked"
        assert internal_requisition.accepted_at == "2022-07-25"
        assert internal_requisition.expires_at == "2022-10-23"
        assert internal_requisition.max_historical_days == 90

        assert response.status_code == 200
        assert response.json() == [
            {
                'accepted_at': '2022-07-25',
                'bank_accounts':[
                    {'account_id': 'account1_id','currency': 'EUR','name': 'Main Account'},
                    {'account_id': 'account2_id','currency': 'EUR','name': 'Main Account'}
                ],
                'expires_at': '2022-10-23',
                'id': 'requisition_id',
                'institution_name': 'ANAVARKOS BANK',
                'link': 'www.redirect_link.com',
                'max_historical_days': 90,
                'status': 'created'
            },
        ]


class TestDeleteBankConnection:
    @pytest.mark.asyncio
    async def test_delete_success(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        httpx_mock: HTTPXMock
    ):
        # Prepare
        # Create internal requisition
        requisition_repo = RequisitionRepo(async_session)
        await requisition_repo.add(
            _id="9b147a75-6a54-45b7-857d-ca4e2e88d234",
            user_id="test_user_id",
            institution_id="institution_id",
            institution_name="ANAVARKOS BANK",
            link="www.redirect_link.com"
        )

        # Mock nordigen responses
        mock_delete_nordigen_requisition(httpx_mock,"9b147a75-6a54-45b7-857d-ca4e2e88d234")

        # Act
        response = test_client.delete("/bank_connections/9b147a75-6a54-45b7-857d-ca4e2e88d234")

        # Assert
        # Make sure that the internal requisition is deleted
        internal_requisition = await requisition_repo.get("9b147a75-6a54-45b7-857d-ca4e2e88d234")
        assert internal_requisition is None
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_nordigen_failure(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        httpx_mock: HTTPXMock
    ):
        # Prepare
        # Create internal requisition
        requisition_repo = RequisitionRepo(async_session)
        await requisition_repo.add(
            _id="9b147a75-6a54-45b7-857d-ca4e2e88d234",
            user_id="test_user_id",
            institution_id="institution_id",
            institution_name="ANAVARKOS BANK",
            link="www.redirect_link.com"
        )

        # Mock nordigen responses
        mock_delete_nordigen_requisition_not_found(httpx_mock,"9b147a75-6a54-45b7-857d-ca4e2e88d234")

        # Act
        response = test_client.delete("/bank_connections/9b147a75-6a54-45b7-857d-ca4e2e88d234")

        # Assert
        # Make sure that the internal requisition is deleted
        internal_requisition = await requisition_repo.get("9b147a75-6a54-45b7-857d-ca4e2e88d234")
        assert internal_requisition is None
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_not_found(
        self,
        test_client,
        test_db,
        authenticated_user,
        httpx_mock: HTTPXMock
    ):
        # Prepare
        mock_delete_nordigen_requisition_not_found(httpx_mock,"9b147a75-6a54-45b7-857d-ca4e2e88d234")

        # Act
        response = test_client.delete("/bank_connections/9b147a75-6a54-45b7-857d-ca4e2e88d234")
        
        # Assert
        assert response.status_code == 400
        assert response.json()['detail'] == "Bank connection with given id doesn't exist"


class TestUpdateBankConnection:
    @pytest.mark.asyncio
    async def test_update_success(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        httpx_mock: HTTPXMock
    ):
        # Prepare
        # Create internal expired requisition
        requisition_repo = RequisitionRepo(async_session)
        await requisition_repo.add(
            _id="9b147a75-6a54-45b7-857d-ca4e2e88d234",
            user_id="test_user_id",
            institution_id="ASTROBANK_PIRBCY2N",
            institution_name="Astrobank",
            link="www.redirect_link.com",
            status="expired"
        )

        # Mock nordigen responses
        mock_delete_nordigen_requisition(httpx_mock,"9b147a75-6a54-45b7-857d-ca4e2e88d234")
        mock_create_nordigen_requisition(httpx_mock, "ASTROBANK_PIRBCY2N", "1b147a75-1a54-45b7-157d-ca1e2e18d231")
        mock_nordigen_get_institution_by_id(httpx_mock, "ASTROBANK_PIRBCY2N", "Astrobank")

        # Act
        response = test_client.put("/bank_connections/9b147a75-6a54-45b7-857d-ca4e2e88d234")

        # Assert
        # Make sure that the expired internal requisition is deleted
        expired_requisition = await requisition_repo.get("9b147a75-6a54-45b7-857d-ca4e2e88d234")
        assert expired_requisition is None
        
        # Assert that a new requisition was created
        new_requisition = await requisition_repo.get("1b147a75-1a54-45b7-157d-ca1e2e18d231")
        assert new_requisition is not None
        assert new_requisition.accepted_at is None
        assert new_requisition.status == "not_linked"
        assert new_requisition.expires_at is None
        assert new_requisition.max_historical_days is None
        assert new_requisition.institution_name == "Astrobank"
        assert new_requisition.user_id == "test_user_id"

        assert response.status_code == 201
        assert response.json() == {
            'accepted_at': None,
            'bank_accounts': None,
            'expires_at': None,
            'id': "1b147a75-1a54-45b7-157d-ca1e2e18d231",
            'institution_name': 'Astrobank',
            'link': 'https://ob.nordigen.com/psd2/start/3fa85f64-5717-4562-b3fc-2c963f66afa6/anavarkos_bank',
            'max_historical_days': None,
            'status': 'pending'
        }

    @pytest.mark.asyncio
    async def test_update_not_found(
        self,
        test_client,
        test_db,
        authenticated_user,
        httpx_mock: HTTPXMock
    ):
        # Prepare
        mock_delete_nordigen_requisition_not_found(httpx_mock,"9b147a75-6a54-45b7-857d-ca4e2e88d234")

        # Act
        response = test_client.put("/bank_connections/9b147a75-6a54-45b7-857d-ca4e2e88d234")
        
        # Assert
        assert response.status_code == 400
        assert response.json() == {
            'detail': "Bank connection with given id doesn't exist",
        }
