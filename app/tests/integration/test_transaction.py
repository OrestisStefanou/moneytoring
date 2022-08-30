from datetime import datetime
from unicodedata import category

import pytest
from pytest_httpx import HTTPXMock

from ...repos.bank_account_repo import BankAccountRepo
from app.tests.fixtures.nordigen import (
    mock_get_account_transactions,
    mock_get_account_transactions_wtih_dates,
    nordigen_token
)
from app.tests.fixtures.app_fixtures import (
    test_client,
    test_db,
    async_session,
    authenticated_user,
    event_loop,
    assert_all_responses_were_requested,
)
from app.repos.account_history_repo import AccountHistoryRepo
from app.repos.transaction_repo import TransactionRepo
from app.repos.requisition_repo import RequisitionRepo
import app.services.transactions as transactions_services


class TestGetAccountTransactions:
    @pytest.mark.asyncio
    async def test_no_account_history(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        nordigen_token,
        httpx_mock: HTTPXMock
    ):
        # Prepare
        # Create test bank account
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        mock_get_account_transactions(httpx_mock, test_account_id)

        # Act
        response = test_client.get(
            f"/account_transactions/{test_account_id}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': f"{test_account_id}-2",
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '-15.00',
                'currency': 'EUR',
                'information': 'PAYMENT Alderaan Coffe',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-15',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': f"{test_account_id}-1",
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '45.00',
                'currency': 'EUR',
                'information': 'For the support of Restoration of the Republic foundation',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-14',
                'debtor_name': 'MON MOTHMA',
                'category': None, 
                'custom_category': None
            },
            {
                'id': f"{test_account_id}-3",
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '45.00',
                'currency': 'EUR',
                'information': 'For the support of Restoration of the Republic foundation',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-13',
                'debtor_name': 'MON MOTHMA',
                'category': None,
                'custom_category': None
            },
            {
                'id': f"{test_account_id}-4",
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '-15.00',
                'currency': 'EUR',
                'information': 'PAYMENT Alderaan Coffe',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-12',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            }
        ]

        # Check that we have transactions internally
        transaction_repo = TransactionRepo(async_session)
        transactions = await transaction_repo.get_all()
        assert len(transactions) == 4

        # Check that we have account history
        account_history_repo = AccountHistoryRepo(async_session)
        account_history = await account_history_repo.get_by_account_id(test_account_id)
        assert account_history.latest_date == datetime.now().strftime("%Y-%m-%d")

    @pytest.mark.asyncio
    async def test_account_history_outdated(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        nordigen_token,
        httpx_mock: HTTPXMock
    ):
        # Prepare
        # Create test bank account
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        # Create test account history
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id,
            latest_date="2022-07-30"
        )
        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(2):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id,
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date="2022-07-28"
            )
        # Mock nordigen response
        mock_get_account_transactions_wtih_dates(
            httpx_mock=httpx_mock,
            account_id=test_account_id,
            date_from="2022-07-30",
        )

        # Act
        response = test_client.get(
            f"/account_transactions/{test_account_id}?to_date=2022-08-15"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': f'{test_account_id}-1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '45.00',
                'currency': 'EUR',
                'information': 'For the support of Restoration of the Republic foundation',
                'code': 'PMNT',
                'created_date': '2022-07-30',
                'booking_date': '2022-07-30',
                'debtor_name': 'MON MOTHMA',
                'category': None,
                'custom_category': None
            },
            {
                'id': f'{test_account_id}-2',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '-15.00',
                'currency': 'EUR',
                'information': 'PAYMENT Alderaan Coffe',
                'code': 'PMNT',
                'created_date': '2022-07-30',
                'booking_date': '2022-07-30',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': 'transacion_0',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-28',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': 'transacion_1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-28',
                'debtor_name': None,
                'category': None, 
                'custom_category': None
            }
        ]

        transactions = await transaction_repo.get_all()
        assert len(transactions) == 4

        # Assert that account history is updated
        account_history = await account_history_repo.get_by_account_id(test_account_id)
        assert account_history.latest_date == datetime.now().strftime("%Y-%m-%d")

    @pytest.mark.asyncio
    async def test_account_history_covers_request(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        # Create test bank account
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        # Create test account history
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id,
            latest_date="2022-07-30"
        )
        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(3):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id,
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date="2022-07-28"
            )

        # Act
        response = test_client.get(
            f"/account_transactions/{test_account_id}?to_date=2022-07-28"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': 'transacion_0',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-28',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': 'transacion_1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-28',
                'debtor_name': None,
                'category': None, 
                'custom_category': None
            },
            {
                'id': 'transacion_2',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-28',
                'debtor_name': None,
                'category': None, 
                'custom_category': None
            }
        ]


    @pytest.mark.asyncio
    async def test_category_filter(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        # Create test account history
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id,
            latest_date=datetime.now().strftime("%Y-%m-%d")
        )
        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(1,11):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id,
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date=f"2022-07-{i}"
            )

        await transactions_services.set_transaction_category(
            session=async_session,
            transaction_id="transacion_1",
            category="food"
        )

        await transactions_services.set_transaction_category(
            session=async_session,
            transaction_id="transacion_3",
            category="food"
        )

        # Act
        response = test_client.get(
            f"/account_transactions/{test_account_id}?category=food&to_date=2022-08-01"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': 'transacion_3',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-3',
                'debtor_name': None,
                'category': "food",
                'custom_category': None
            },
            {
                'id': 'transacion_1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-1',
                'debtor_name': None,
                'category': "food", 
                'custom_category': None
            }
        ]


    @pytest.mark.asyncio
    async def test_custom_category_filter(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        # Create test account history
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id,
            latest_date=datetime.now().strftime("%Y-%m-%d")
        )
        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(1,11):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id,
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date=f"2022-07-{i}"
            )

        await transactions_services.set_transaction_custom_category(
            session=async_session,
            transaction_id="transacion_1",
            custom_category="Classified"
        )

        await transactions_services.set_transaction_custom_category(
            session=async_session,
            transaction_id="transacion_3",
            custom_category="Classified"
        )

        # Act
        response = test_client.get(
            f"/account_transactions/{test_account_id}?custom_category=Classified&to_date=2022-08-01"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': 'transacion_3',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-3',
                'debtor_name': None,
                'category': None,
                'custom_category': 'Classified'
            },
            {
                'id': 'transacion_1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-1',
                'debtor_name': None,
                'category': None, 
                'custom_category': 'Classified'
            }
        ]


    @pytest.mark.asyncio
    async def test_categories_filter(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        # Create test account history
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id,
            latest_date=datetime.now().strftime("%Y-%m-%d")
        )
        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(1,11):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id,
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date=f"2022-07-{i}"
            )

        await transactions_services.set_transaction_custom_category(
            session=async_session,
            transaction_id="transacion_1",
            custom_category="Classified"
        )

        await transactions_services.set_transaction_custom_category(
            session=async_session,
            transaction_id="transacion_3",
            custom_category="Classified"
        )

        await transactions_services.set_transaction_category(
            session=async_session,
            transaction_id="transacion_3",
            category="food"
        )

        # Act
        response = test_client.get(
            f"/account_transactions/{test_account_id}?custom_category=Classified&category=food&to_date=2022-08-01"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': 'transacion_3',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-3',
                'debtor_name': None,
                'category': 'food',
                'custom_category': 'Classified'
            }
        ]


    @pytest.mark.asyncio
    async def test_date_range_filter(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        # Create test account history
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id,
            latest_date=datetime.now().strftime("%Y-%m-%d")
        )
        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(1,11):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id,
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date=f"2022-07-{i}"
            )

        # Act
        response = test_client.get(
            f"/account_transactions/{test_account_id}?from_date=2022-07-03&to_date=2022-07-05"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': 'transacion_5',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-5',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': 'transacion_4',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-4',
                'debtor_name': None,
                'category': None, 
                'custom_category': None
            },
            {
                'id': 'transacion_3',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-3',
                'debtor_name': None,
                'category': None, 
                'custom_category': None
            }
        ]


    @pytest.mark.asyncio
    async def test_account_not_found(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        nordigen_token,
        httpx_mock: HTTPXMock
    ):
        # Prepare
        # Act
        response = test_client.get(
            f"/account_transactions/26f6f755-0633-4eb4-963c-03534fe03c9e"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()['detail'] == "Account with given id not found"

class TestGetUserTransactions:
    @pytest.mark.asyncio
    async def test_no_account_history(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        nordigen_token,
        httpx_mock: HTTPXMock
    ):
        # Prepare
        # Crete test requisition
        requisition_repo = RequisitionRepo(async_session)
        await requisition_repo.add(
            _id="test_requisition_id",
            user_id="test_user_id",
            institution_id="Anavargos_bank_id",
            institution_name="Anavagros_bank",
            link="some_link.com",
        )
        # Create test bank account
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id_1 = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id_1,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        mock_get_account_transactions(httpx_mock, test_account_id_1)
        
        test_account_id_2 = "f9a31318-a48c-4fc9-a038-5defb4db0509"
        await bank_account_repo.add(
            account_id=test_account_id_2,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        mock_get_account_transactions(httpx_mock, test_account_id_2)

        # Act
        response = test_client.get(
            f"/account_transactions"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': '26f6f755-0633-4eb4-963c-03534fe03c9e-2',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '-15.00',
                'currency': 'EUR',
                'information': 'PAYMENT Alderaan Coffe',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-15',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': 'f9a31318-a48c-4fc9-a038-5defb4db0509-2',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '-15.00',
                'currency': 'EUR',
                'information': 'PAYMENT Alderaan Coffe',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-15',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': '26f6f755-0633-4eb4-963c-03534fe03c9e-1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '45.00',
                'currency': 'EUR',
                'information': 'For the support of Restoration of the Republic foundation',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-14',
                'debtor_name': 'MON MOTHMA',
                'category': None,
                'custom_category': None
            },
            {
                'id': 'f9a31318-a48c-4fc9-a038-5defb4db0509-1',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '45.00',
                'currency': 'EUR',
                'information': 'For the support of Restoration of the Republic foundation',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-14',
                'debtor_name': 'MON MOTHMA',
                'category': None,
                'custom_category': None
            },
            {
                'id': '26f6f755-0633-4eb4-963c-03534fe03c9e-3',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '45.00',
                'currency': 'EUR',
                'information': 'For the support of Restoration of the Republic foundation',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-13',
                'debtor_name': 'MON MOTHMA',
                'category': None,
                'custom_category': None
            },
            {
                'id': 'f9a31318-a48c-4fc9-a038-5defb4db0509-3',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '45.00',
                'currency': 'EUR',
                'information': 'For the support of Restoration of the Republic foundation',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-13',
                'debtor_name': 'MON MOTHMA',
                'category': None, 
                'custom_category': None
            },
            {
                'id': '26f6f755-0633-4eb4-963c-03534fe03c9e-4',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '-15.00',
                'currency': 'EUR',
                'information': 'PAYMENT Alderaan Coffe',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-12',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': 'f9a31318-a48c-4fc9-a038-5defb4db0509-4',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '-15.00',
                'currency': 'EUR',
                'information': 'PAYMENT Alderaan Coffe',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-12',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            }
        ]

        # Check that we have transactions internally
        transaction_repo = TransactionRepo(async_session)
        transactions = await transaction_repo.get_all()
        assert len(transactions) == 8

        # Check that we have account history
        account_history_repo = AccountHistoryRepo(async_session)
        account_history = await account_history_repo.get_by_account_id(test_account_id_1)
        assert account_history.latest_date == datetime.now().strftime("%Y-%m-%d")
        account_history = await account_history_repo.get_by_account_id(test_account_id_2)
        assert account_history.latest_date == datetime.now().strftime("%Y-%m-%d")

    @pytest.mark.asyncio
    async def test_account_history_outdated(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        nordigen_token,
        httpx_mock: HTTPXMock
    ):
        # Prepare
        # Crete test requisition
        requisition_repo = RequisitionRepo(async_session)
        await requisition_repo.add(
            _id="test_requisition_id",
            user_id="test_user_id",
            institution_id="Anavargos_bank_id",
            institution_name="Anavagros_bank",
            link="some_link.com",
        )
        # Create test bank accounts
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )

        test_account_id_2 = "f9a31318-a48c-4fc9-a038-5defb4db0509"
        await bank_account_repo.add(
            account_id=test_account_id_2,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )

        # Create test account history
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id,
            latest_date="2022-07-30"
        )
        await account_history_repo.add(
            account_id=test_account_id_2,
            latest_date="2022-07-30"
        )
        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        await transaction_repo.add(
            _id=f"transacion_0",
            account_id=test_account_id,
            amount="150.00",
            currency="BTC",
            information="Supermarket",
            code="TOP_SECRET",
            created_date="2022-07-28",
            booking_date="2022-07-28"
        )
        await transaction_repo.add(
            _id=f"transacion_1",
            account_id=test_account_id_2,
            amount="50.00",
            currency="BTC",
            information="Molly with the purple rain",
            code="MOLLY",
            created_date="2022-07-27",
            booking_date="2022-07-27"
        )

        # Mock nordigen responses
        mock_get_account_transactions_wtih_dates(
            httpx_mock=httpx_mock,
            account_id=test_account_id,
            date_from="2022-07-30",
        )

        mock_get_account_transactions_wtih_dates(
            httpx_mock=httpx_mock,
            account_id=test_account_id_2,
            date_from="2022-07-30",
        )

        # Act
        response = test_client.get(
            f"/account_transactions?to_date=2022-08-15"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': '26f6f755-0633-4eb4-963c-03534fe03c9e-1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '45.00',
                'currency': 'EUR',
                'information': 'For the support of Restoration of the Republic foundation',
                'code': 'PMNT',
                'created_date': '2022-07-30',
                'booking_date': '2022-07-30',
                'debtor_name': 'MON MOTHMA',
                'category': None,
                'custom_category': None
            },
            {
                'id': '26f6f755-0633-4eb4-963c-03534fe03c9e-2',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '-15.00',
                'currency': 'EUR',
                'information': 'PAYMENT Alderaan Coffe',
                'code': 'PMNT',
                'created_date': '2022-07-30',
                'booking_date': '2022-07-30',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': 'f9a31318-a48c-4fc9-a038-5defb4db0509-1',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '45.00',
                'currency': 'EUR',
                'information': 'For the support of Restoration of the Republic foundation',
                'code': 'PMNT',
                'created_date': '2022-07-30',
                'booking_date': '2022-07-30',
                'debtor_name': 'MON MOTHMA',
                'category': None,
                'custom_category': None
            },
            {
                'id': 'f9a31318-a48c-4fc9-a038-5defb4db0509-2',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '-15.00',
                'currency': 'EUR',
                'information': 'PAYMENT Alderaan Coffe',
                'code': 'PMNT',
                'created_date': '2022-07-30',
                'booking_date': '2022-07-30',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': 'transacion_0',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-28',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': 'transacion_1',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '50.00',
                'currency': 'BTC',
                'information': 'Molly with the purple rain',
                'code': 'MOLLY',
                'created_date': '2022-07-27',
                'booking_date': '2022-07-27',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            }
        ]

        transactions = await transaction_repo.get_all()
        assert len(transactions) == 6

        # Assert that account history is updated
        account_history = await account_history_repo.get_by_account_id(test_account_id)
        assert account_history.latest_date == datetime.now().strftime("%Y-%m-%d")

        account_history = await account_history_repo.get_by_account_id(test_account_id_2)
        assert account_history.latest_date == datetime.now().strftime("%Y-%m-%d")

    @pytest.mark.asyncio
    async def test_account_history_covers_request(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        # Crete test requisition
        requisition_repo = RequisitionRepo(async_session)
        await requisition_repo.add(
            _id="test_requisition_id",
            user_id="test_user_id",
            institution_id="Anavargos_bank_id",
            institution_name="Anavagros_bank",
            link="some_link.com",
        )

        # Create test bank account
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        test_account_id_2 = "f9a31318-a48c-4fc9-a038-5defb4db0509"
        await bank_account_repo.add(
            account_id=test_account_id_2,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )

        # Create test account history
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id,
            latest_date="2022-07-30"
        )
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id_2,
            latest_date="2022-07-30"
        )

        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(2):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id,
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date="2022-07-28"
            )
        for i in range(2,4):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id_2,
                amount="50.00",
                currency="BTC",
                information="Ecstasy is fantasy",
                code="MDMA",
                created_date="2022-07-27",
                booking_date="2022-07-27"
            )

        # Act
        response = test_client.get(
            f"/account_transactions?to_date=2022-07-28"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': 'transacion_0',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-28',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': 'transacion_1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-28',
                'debtor_name': None,
                'category': None, 
                'custom_category': None
            },
            {
                'id': 'transacion_2',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '50.00',
                'currency': 'BTC',
                'information': 'Ecstasy is fantasy',
                'code': 'MDMA',
                'created_date': '2022-07-27',
                'booking_date': '2022-07-27',
                'debtor_name': None,
                'category': None, 
                'custom_category': None
            },
            {
                'id': 'transacion_3',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '50.00',
                'currency': 'BTC',
                'information': 'Ecstasy is fantasy',
                'code': 'MDMA',
                'created_date': '2022-07-27',
                'booking_date': '2022-07-27',
                'debtor_name': None,
                'category': None, 
                'custom_category': None
            }
        ]


    @pytest.mark.asyncio
    async def test_category_filter(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        # Crete test requisition
        requisition_repo = RequisitionRepo(async_session)
        await requisition_repo.add(
            _id="test_requisition_id",
            user_id="test_user_id",
            institution_id="Anavargos_bank_id",
            institution_name="Anavagros_bank",
            link="some_link.com",
        )

        # Create test bank account
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        test_account_id_2 = "f9a31318-a48c-4fc9-a038-5defb4db0509"
        await bank_account_repo.add(
            account_id=test_account_id_2,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )

        # Create test account history
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id,
            latest_date=datetime.now().strftime("%Y-%m-%d")
        )
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id_2,
            latest_date=datetime.now().strftime("%Y-%m-%d")
        )

        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(2):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id,
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date="2022-07-28"
            )
        for i in range(2,4):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id_2,
                amount="50.00",
                currency="BTC",
                information="Ecstasy is fantasy",
                code="MDMA",
                created_date="2022-07-27",
                booking_date="2022-07-27"
            )

        await transactions_services.set_transaction_category(
            session=async_session,
            transaction_id="transacion_1",
            category="healthcare"
        )

        await transactions_services.set_transaction_category(
            session=async_session,
            transaction_id="transacion_3",
            category="healthcare"
        )

        # Act
        response = test_client.get(
            f"/account_transactions?to_date=2022-07-28&category=healthcare"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': 'transacion_1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-28',
                'debtor_name': None,
                'category': 'healthcare', 
                'custom_category': None
            },
            {
                'id': 'transacion_3',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '50.00',
                'currency': 'BTC',
                'information': 'Ecstasy is fantasy',
                'code': 'MDMA',
                'created_date': '2022-07-27',
                'booking_date': '2022-07-27',
                'debtor_name': None,
                'category': 'healthcare', 
                'custom_category': None
            }
        ]


    @pytest.mark.asyncio
    async def test_custom_category_filter(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        # Crete test requisition
        requisition_repo = RequisitionRepo(async_session)
        await requisition_repo.add(
            _id="test_requisition_id",
            user_id="test_user_id",
            institution_id="Anavargos_bank_id",
            institution_name="Anavagros_bank",
            link="some_link.com",
        )

        # Create test bank account
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        test_account_id_2 = "f9a31318-a48c-4fc9-a038-5defb4db0509"
        await bank_account_repo.add(
            account_id=test_account_id_2,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )

        # Create test account history
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id,
            latest_date=datetime.now().strftime("%Y-%m-%d")
        )
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id_2,
            latest_date=datetime.now().strftime("%Y-%m-%d")
        )

        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(2):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id,
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date="2022-07-28"
            )
        for i in range(2,4):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id_2,
                amount="50.00",
                currency="BTC",
                information="Ecstasy is fantasy",
                code="MDMA",
                created_date="2022-07-27",
                booking_date="2022-07-27"
            )

        await transactions_services.set_transaction_custom_category(
            session=async_session,
            transaction_id="transacion_1",
            custom_category="charity"
        )

        await transactions_services.set_transaction_custom_category(
            session=async_session,
            transaction_id="transacion_3",
            custom_category="charity"
        )

        # Act
        response = test_client.get(
            f"/account_transactions?to_date=2022-07-28&custom_category=charity"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': 'transacion_1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-28',
                'debtor_name': None,
                'category': None, 
                'custom_category': 'charity'
            },
            {
                'id': 'transacion_3',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '50.00',
                'currency': 'BTC',
                'information': 'Ecstasy is fantasy',
                'code': 'MDMA',
                'created_date': '2022-07-27',
                'booking_date': '2022-07-27',
                'debtor_name': None,
                'category': None, 
                'custom_category': 'charity'
            }
        ]

    @pytest.mark.asyncio
    async def test_category_filtering(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        # Crete test requisition
        requisition_repo = RequisitionRepo(async_session)
        await requisition_repo.add(
            _id="test_requisition_id",
            user_id="test_user_id",
            institution_id="Anavargos_bank_id",
            institution_name="Anavagros_bank",
            link="some_link.com",
        )

        # Create test bank account
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        test_account_id_2 = "f9a31318-a48c-4fc9-a038-5defb4db0509"
        await bank_account_repo.add(
            account_id=test_account_id_2,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )

        # Create test account history
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id,
            latest_date=datetime.now().strftime("%Y-%m-%d")
        )
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id_2,
            latest_date=datetime.now().strftime("%Y-%m-%d")
        )

        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(2):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id,
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date="2022-07-28"
            )
        for i in range(2,4):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id_2,
                amount="50.00",
                currency="BTC",
                information="Ecstasy is fantasy",
                code="MDMA",
                created_date="2022-07-27",
                booking_date="2022-07-27"
            )

        await transactions_services.set_transaction_category(
            session=async_session,
            transaction_id="transacion_1",
            category="healthcare"
        )

        await transactions_services.set_transaction_custom_category(
            session=async_session,
            transaction_id="transacion_1",
            custom_category="charity"
        )

        await transactions_services.set_transaction_custom_category(
            session=async_session,
            transaction_id="transacion_3",
            custom_category="charity"
        )

        # Act
        response = test_client.get(
            f"/account_transactions?to_date=2022-07-28&custom_category=charity&category=healthcare"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': 'transacion_1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-28',
                'debtor_name': None,
                'category': 'healthcare', 
                'custom_category': 'charity'
            }
        ]

    @pytest.mark.asyncio
    async def test_date_range_filtering(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        # Crete test requisition
        requisition_repo = RequisitionRepo(async_session)
        await requisition_repo.add(
            _id="test_requisition_id",
            user_id="test_user_id",
            institution_id="Anavargos_bank_id",
            institution_name="Anavagros_bank",
            link="some_link.com",
        )

        # Create test bank account
        bank_account_repo = BankAccountRepo(async_session)
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        await bank_account_repo.add(
            account_id=test_account_id,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )
        test_account_id_2 = "f9a31318-a48c-4fc9-a038-5defb4db0509"
        await bank_account_repo.add(
            account_id=test_account_id_2,
            requistion_id="test_requisition_id",
            name="LaundryAccount",
            currency="BTC"
        )

        # Create test account history
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id,
            latest_date=datetime.now().strftime("%Y-%m-%d")
        )
        account_history_repo = AccountHistoryRepo(async_session)
        await account_history_repo.add(
            account_id=test_account_id_2,
            latest_date=datetime.now().strftime("%Y-%m-%d")
        )

        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(1,3):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id,
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date=f"2022-07-{i}"
            )
        for i in range(3,10):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id=test_account_id_2,
                amount="50.00",
                currency="BTC",
                information="Ecstasy is fantasy",
                code="MDMA",
                created_date="2022-07-27",
                booking_date=f"2022-07-{i}"
            )

        await transactions_services.set_transaction_category(
            session=async_session,
            transaction_id="transacion_1",
            category="healthcare"
        )

        await transactions_services.set_transaction_custom_category(
            session=async_session,
            transaction_id="transacion_1",
            custom_category="charity"
        )

        await transactions_services.set_transaction_custom_category(
            session=async_session,
            transaction_id="transacion_3",
            custom_category="charity"
        )

        # Act
        response = test_client.get(
            f"/account_transactions?to_date=2022-07-04&from_date=2022-07-02"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': 'transacion_4',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '50.00',
                'currency': 'BTC',
                'information': 'Ecstasy is fantasy',
                'code': 'MDMA',
                'created_date': '2022-07-27',
                'booking_date': '2022-07-4',
                'debtor_name': None,
                'category': None, 
                'custom_category': None
            },
            {
                'id': 'transacion_3',
                'account_id': 'f9a31318-a48c-4fc9-a038-5defb4db0509',
                'amount': '50.00',
                'currency': 'BTC',
                'information': 'Ecstasy is fantasy',
                'code': 'MDMA',
                'created_date': '2022-07-27',
                'booking_date': '2022-07-4',
                'debtor_name': None,
                'category': None, 
                'custom_category': None
            },
            {
                'id': 'transacion_2',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '150.00',
                'currency': 'BTC',
                'information': 'Supermarket',
                'code': 'TOP_SECRET',
                'created_date': '2022-07-28',
                'booking_date': '2022-07-28',
                'debtor_name': None,
                'category': None, 
                'custom_category': None
            },
        ]


class TestSetTransactionCategory:
    @pytest.mark.asyncio
    async def test_success(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(5):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id="test_account_id",
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date="2022-07-28"
            )

        # Act
        response = test_client.put(
            f"/account_transactions/transacion_0/category?category=food"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            'id': 'transacion_0',
            'account_id': 'test_account_id',
            'amount': '150.00',
            'currency': 'BTC',
            'information': 'Supermarket',
            'code': 'TOP_SECRET',
            'created_date': '2022-07-28',
            'booking_date': '2022-07-28',
            'debtor_name': None,
            'category': 'food',
            'custom_category': None
        }

        # Assert internal transaction is updated
        transaction = await transaction_repo.get("transacion_0")
        assert transaction.category == "food"

    @pytest.mark.asyncio
    async def test_not_found(
        self,
        test_client,
        test_db,
        authenticated_user,
    ):
        # Act
        response = test_client.put(
            f"/account_transactions/transacion_0/category?category=food"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()['detail'] == "Transaction with given id not found"


class TestSetTransactionCustomCategory:
    @pytest.mark.asyncio
    async def test_success(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
    ):
        # Prepare
        # Create mock transactions
        transaction_repo = TransactionRepo(async_session)
        for i in range(5):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id="test_account_id",
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date="2022-07-28"
            )

        # Act
        response = test_client.put(
            f"/account_transactions/transacion_0/custom_category?category=Drugs"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            'id': 'transacion_0',
            'account_id': 'test_account_id',
            'amount': '150.00',
            'currency': 'BTC',
            'information': 'Supermarket',
            'code': 'TOP_SECRET',
            'created_date': '2022-07-28',
            'booking_date': '2022-07-28',
            'debtor_name': None,
            'category': None,
            'custom_category': 'Drugs'
        }

        # Assert internal transaction is updated
        transaction = await transaction_repo.get("transacion_0")
        assert transaction.custom_category == "Drugs"

    @pytest.mark.asyncio
    async def test_not_found(
        self,
        test_client,
        test_db,
        authenticated_user,
    ):
        # Act
        response = test_client.put(
            f"/account_transactions/transacion_0/custom_category?category=Drugs"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()['detail'] == "Transaction with given id not found"