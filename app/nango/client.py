import os
from abc import ABC, abstractmethod

import httpx
from dotenv import load_dotenv

load_dotenv()


class TokenProvider(ABC):
    """
    Base interface for token retrieval.
    The rest of the app only knows about this class.
    It never knows if tokens come from Nango, a mock, or anywhere else.
    """

    @abstractmethod
    def get_token(self, integration: str, connection_id: str) -> str:
        raise NotImplementedError("Subclasses must implement get_token()")


class MockTokenProvider(TokenProvider):
    """
    Returns a fake hardcoded token.
    Used in tests and when USE_MOCK_TOKEN=true in .env
    """

    def get_token(self, integration: str, connection_id: str) -> str:
        return "mock-token-for-testing"


class NangoTokenProvider(TokenProvider):
    """
    Calls the real Nango API to get a live token.
    Used in production when USE_MOCK_TOKEN=false in .env
    To wire this up for real:
    - Set NANGO_SECRET_KEY in your .env
    - Set NANGO_BASE_URL in your .env
    - Set USE_MOCK_TOKEN=false in your .env
    """

    def __init__(self) -> None:
        self.secret_key = os.getenv("NANGO_SECRET_KEY")
        self.base_url = os.getenv("NANGO_BASE_URL", "https://api.nango.dev")

    def get_token(self, integration: str, connection_id: str) -> str:
        url = f"{self.base_url}/connection/{connection_id}"
        headers = {"Authorization": f"Bearer {self.secret_key}"}

        response = httpx.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        return data["credentials"]["access_token"]


def get_token_provider() -> TokenProvider:
    """
    This is the factory function.
    The rest of the app calls this to get whichever provider is configured.
    It reads USE_MOCK_TOKEN from .env and returns the right one.
    """

    use_mock = os.getenv("USE_MOCK_TOKEN", "true").lower() == "true"

    if use_mock:
        return MockTokenProvider()
    return NangoTokenProvider()