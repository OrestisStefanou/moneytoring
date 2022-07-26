import pytest

from app.tests.fixtures.nordigen import (
    nordigen_token,
    create_nordigen_requisition,
)

from app.tests.fixtures.app_fixtures import (
    test_client,
    test_db,
    async_session,
    authenticated_user,
    event_loop,
    assert_all_responses_were_requested
)


class TestCreateBankConnection:
    def test_success(
        self,
        test_client,
        test_db,
        async_session,
        authenticated_user,
        nordigen_token,
        create_nordigen_requisition
    ):
        response = test_client.post(
            "/bank_connections",
            json={""}
        )