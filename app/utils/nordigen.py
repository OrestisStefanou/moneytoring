from datetime import datetime, timedelta

def get_datetime_obj_from_string(date_str: str) -> datetime:
    """
    - Params:
        - date_str: Date in string format. example: 2022-07-23
    - Returns:
        - A datetime object
    """
    return datetime.strptime(date_str, "%Y-%m-%d")


def calculate_expiration_date(accepted_datetime_str: str, days_duration: int) -> str:
    """
    - Params:
        - accepted_date: Date in string format. example: 2022-07-23T10:35:33.580170Z
        - duration: Number of days
    - Returns:
        - A date in string format of YYYY-MM-DD
    """
    accepted_date_string = accepted_datetime_str.split('T')[0]
    accepted_date = datetime.strptime(accepted_date_string, "%Y-%m-%d")
    expiration_date = accepted_date + timedelta(days=days_duration)
    return expiration_date.strftime("%Y-%m-%d")
