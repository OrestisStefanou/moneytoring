
class InvalidCountryCode(Exception):
    pass


class InstitutionNotFound(Exception):
    pass


class NordigenFailure(Exception):
    """
    This is a general exception that we raise in case an 
    http call to Nordigen fails to complete
    """
    pass