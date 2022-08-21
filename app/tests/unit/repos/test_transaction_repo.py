import pytest

from app.tests.fixtures.app_fixtures import (
    test_db,
    async_session,
    event_loop,
)

from app.repos.transaction_repo import TransactionRepo

class TestTransactionRepo:
    @pytest.mark.asyncio
    async def test_duplicate_transaction(
        self,
        test_db,
        async_session,
    ):
        transaction_repo = TransactionRepo(async_session)
        for i in range(3):
            await transaction_repo.add(
                _id=f"transacion_{i}",
                account_id='account_1',
                amount="150.00",
                currency="BTC",
                information="Supermarket",
                code="TOP_SECRET",
                created_date="2022-07-28",
                booking_date="2022-07-28"
            )

        # Try to insert another transaction with an id that already exists
        await transaction_repo.add(
            _id="transacion_0",
            account_id='account_1',
            amount="150.00",
            currency="BTC",
            information="Supermarket",
            code="TOP_SECRET",
            created_date="2022-07-28",
            booking_date="2022-07-28"
        )

        await transaction_repo.add(
            _id="transacion_4",
            account_id='account_1',
            amount="150.00",
            currency="BTC",
            information="Supermarket",
            code="TOP_SECRET",
            created_date="2022-07-28",
            booking_date="2022-07-28"
        )

        transactions = await transaction_repo.get_all()
        assert len(transactions) == 4
