from datetime import datetime
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
                'id': '2022081401927901-1',
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
                'id': '2022081401927905-1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '-15.00',
                'currency': 'EUR',
                'information': 'PAYMENT Alderaan Coffe',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-14',
                'debtor_name': None,
                'category': None,
                'custom_category': None
            },
            {
                'id': '2022081401927907-1',
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
                'id': '2022081401927902-1',
                'account_id': '26f6f755-0633-4eb4-963c-03534fe03c9e',
                'amount': '-15.00',
                'currency': 'EUR',
                'information': 'PAYMENT Alderaan Coffe',
                'code': 'PMNT',
                'created_date': '2022-08-14',
                'booking_date': '2022-08-14',
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

        assert response.status_code == 200
        print("RESPONSE LEN")
        print(len(response.json()))
        print("Transactions:")
        transactions = await transaction_repo.get_all()
        print(transactions)
        # THINK HOW TO AVOID SAVING INTERNALLY DUPLICATE TRANSACTIONS