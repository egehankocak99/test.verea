from app.contacts.models import Contact
from app.contacts.repository import fetch_contacts
from app.nango.client import get_token_provider


def get_contacts() -> list[Contact]:
    """
    Orchestrates the full contact retrieval flow:
    1. Gets a token from the token provider (Nango or mock)
    2. Passes it to the repository to fetch and normalise contacts
    3. Returns the clean list of Contact objects

    This is the only place that knows about both Nango and the repository.
    The router calls this and never touches either of those directly.
    """
    provider = get_token_provider()
    token = provider.get_token(
        integration="hubspot",
        connection_id="my-hubspot-connection"
    )
    return fetch_contacts(token)