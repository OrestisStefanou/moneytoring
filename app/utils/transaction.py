from datetime import datetime


def validate_date_format(date_string: str) -> bool:
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        return False
    
    return True