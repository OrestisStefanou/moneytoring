from app.utils.nordigen import calculate_expiration_date

def test_calculate_expiration_date():
    accepted_datetime = "2022-07-01T10:35:33.580170Z"
    days_duration = 20

    expiration_date_str = calculate_expiration_date(accepted_datetime, days_duration)
    assert expiration_date_str == "2022-07-21"

    days_duration = 90
    expiration_date_str = calculate_expiration_date(accepted_datetime, days_duration)
    assert expiration_date_str == "2022-09-29"
