from app.http.http_client import HttpClient

class HTTPRepo:
    """
    Repo that gets data from third party providers through http calls
    """
    def __init__(self, client: HttpClient) -> None:
        self._client = client