"""
Base HTTP client for ORCA external API integrations
Provides common functionality for retry logic, timeouts, and error handling
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import aiohttp
from asyncio import TimeoutError as AsyncioTimeoutError

logger = logging.getLogger(__name__)

class CredentialsUnavailableError(Exception):
    """Exception raised when required API credentials are not provided."""
    pass

class BaseAPIClient:
    """
    Base class for external API clients with retry logic and error handling
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0
    ):
        """
        Initialize base API client

        Args:
            base_url: Base URL for the API
            api_key: API key for authentication (if required)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
            backoff_factor: Multiplicative factor for retry delay
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
        self.logger = logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__name__)

    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for API requests

        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            'User-Agent': 'ORCA-Backend/0.1.0',
            'Accept': 'application/json'
        }

        if self.api_key:
            # Default to Bearer token, can be overridden by subclasses
            headers['Authorization'] = f'Bearer {self.api_key}'

        return headers

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be joined with base_url)
            params: Query parameters
            data: Request body data
            headers: Additional headers

        Returns:
            JSON response as dictionary

        Raises:
            aiohttp.ClientError: For HTTP errors
            AsyncioTimeoutError: For timeout errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)

        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                self.logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")

                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.request(
                        method=method,
                        url=url,
                        params=params,
                        json=data if data else None,
                        headers=request_headers
                    ) as response:
                        # Log response status
                        self.logger.debug(f"Response status: {response.status}")

                        # Handle HTTP errors
                        if response.status >= 400:
                            error_text = await response.text()
                            self.logger.warning(
                                f"HTTP {response.status} error from {url}: {error_text}"
                            )

                            # Don't retry on client errors (4xx) except 429
                            if 400 <= response.status < 500 and response.status != 429:
                                self.logger.warning(f"Fatal client error {response.status} for {url}. Not retrying.")
                                raise Exception(f"Fatal Client Error {response.status}")

                            # For 429 (rate limit) and 5xx errors, we'll retry
                            if attempt == self.max_retries:
                                response.raise_for_status()

                        # Parse JSON response
                        try:
                            result = await response.json()
                            self.logger.debug(f"Successfully retrieved data from {url}")
                            return result
                        except aiohttp.ContentTypeError:
                            # If response is not JSON, return text
                            text_result = await response.text()
                            return {"text": text_result, "status": response.status}

            except AsyncioTimeoutError:
                last_exception = AsyncioTimeoutError(f"Timeout requesting {url}")
                self.logger.warning(f"Timeout on attempt {attempt + 1} for {url}")

            except aiohttp.ClientResponseError as e:
                # If it's a 4xx error (except 429), don't retry, just raise immediately
                if 400 <= e.status < 500 and e.status != 429:
                    self.logger.warning(f"Fatal client error {e.status} for {url}. Not retrying.")
                    raise e
                last_exception = e
                self.logger.warning(f"Client error on attempt {attempt + 1} for {url}: {str(e)}")

            except aiohttp.ClientError as e:
                last_exception = e
                self.logger.warning(f"Client error on attempt {attempt + 1} for {url}: {str(e)}")

            except Exception as e:
                # If we explicitly raised a Fatal Client Error, don't retry
                if str(e).startswith("Fatal Client Error"):
                    raise e
                last_exception = e
                self.logger.error(f"Unexpected error on attempt {attempt + 1} for {url}: {str(e)}")

            # If we have retries left, wait before next attempt
            if attempt < self.max_retries:
                delay = self.retry_delay * (self.backoff_factor ** attempt)
                self.logger.debug(f"Waiting {delay} seconds before retry...")
                await asyncio.sleep(delay)

        # If we exhausted all retries, raise the last exception
        self.logger.error(f"Failed to retrieve data from {url} after {self.max_retries + 1} attempts")
        raise last_exception

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make GET request

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers

        Returns:
            JSON response as dictionary
        """
        return await self._make_request('GET', endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make POST request

        Args:
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            headers: Additional headers

        Returns:
            JSON response as dictionary
        """
        return await self._make_request('POST', endpoint, params=params, data=data, headers=headers)

    async def health_check(self) -> bool:
        """
        Check if the API service is healthy

        Returns:
            True if service is responsive, False otherwise
        """
        try:
            # Try to make a simple request to check connectivity
            await self.get('/', params={})
            return True
        except Exception as e:
            self.logger.warning(f"Health check failed: {str(e)}")
            return False