from typing import Dict,Any,Optional
import logging

import httpx

from app.errors.http import HttpRequestError

class HttpClient:
    """
    Http client to help with integrations with 3rd party providers
    """
    def __init__(self, url: str) -> None:
        self._url = url

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str,Any]] = None,
        params: Optional[Dict[str,Any]] = None,
        headers: Optional[Dict[str,Any]] = None,
        timeout: int = 5
    ) -> Dict[str,Any]:
        async with httpx.AsyncClient() as client:
            request = client.build_request(
                method=method,
                url=f'{self._url}{endpoint}',
                json=json,
                params=params,
                headers=headers,
                timeout=timeout
            )
            try:
                response = await client.send(request)
                response.raise_for_status()
            except httpx.RequestError as exc:
                logging.error(f"Http call to {exc.request.url!r} failed with: {str(exc)}")
                raise HttpRequestError()
            except httpx.HTTPStatusError as exc:
                logging.error(f"Http call to {exc.request.url!r} failed with: {str(exc)} and status code: {exc.response.status_code}")
            
            return response.json()
    
    async def post(
        self,
        endpoint: str,
        json: Optional[Dict[str,Any]] = None,
        params: Optional[Dict[str,Any]] = None,
        headers: Optional[Dict[str,Any]] = None,
        timeout: int = 5
    ) -> Dict[str,Any]:
        json_response = await self._make_request(
            method="POST",
            endpoint=endpoint,
            json=json,
            params=params,
            headers=headers,
            timeout=timeout
        )
        return json_response 

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str,Any]] = None,
        headers: Optional[Dict[str,Any]] = None,
        timeout: int = 5
    ) -> Dict[str,Any]:
        json_response = await self._make_request(
            method="GET",
            endpoint=endpoint,
            params=params,
            headers=headers,
            timeout=timeout
        )
        return json_response
    
    # TODO Add methods for other http methods