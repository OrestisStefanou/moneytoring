from app.models.database.account_history import AccountHistory

def test_covers_date():
    account_history = AccountHistory(
        id="some_test_id",
        account_id="some_account_id",
        latest_date="2022-08-13"
    )

    assert account_history.covers_date("2022-08-01") is True
    assert account_history.covers_date("2022-09-01") is False