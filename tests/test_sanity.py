import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.contacts.repository import fetch_contacts
from app.nango.client import MockTokenProvider, get_token_provider


def test_token_provider_returns_mock_token_and_repository_imports() -> None:
    provider = get_token_provider()
    token = provider.get_token("hubspot", "test")

    assert isinstance(provider, MockTokenProvider)
    assert token == "mock-token-for-testing"
    assert callable(fetch_contacts)


if __name__ == "__main__":
    provider = get_token_provider()
    token = provider.get_token("hubspot", "test")
    test_token_provider_returns_mock_token_and_repository_imports()
    print(f"Token: {token}")
    print("Imports working correctly")
    print("No errors, sanity check done")