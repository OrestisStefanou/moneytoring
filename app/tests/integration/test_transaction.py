import pytest
from pytest_httpx import HTTPXMock

from app.tests.fixtures.nordigen import (
    mock_get_account_transactions,
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
        test_account_id = "26f6f755-0633-4eb4-963c-03534fe03c9e"
        mock_get_account_transactions(httpx_mock, test_account_id)

        # Act
        response = test_client.get(
            f"/account_transactions/{test_account_id}"
        )

        assert response.status_code == 200