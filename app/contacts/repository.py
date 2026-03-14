import httpx

from app.contacts.models import Contact


HUBSPOT_CONTACTS_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
HUBSPOT_PROPERTIES = "firstname,lastname,email"


def normalise_contact(raw: dict) -> Contact:
    """
    Converts a single raw HubSpot contact dict into our clean Contact entity.
    This is the normalisation function - tested heavily in tests.
    """
    properties = raw.get("properties", {})

    firstname = properties.get("firstname") or ""
    lastname = properties.get("lastname") or ""
    name = f"{firstname} {lastname}".strip()

    email = properties.get("email") or ""

    return Contact(
        id=str(raw.get("id", "")),
        name=name,
        email=email,
        source="hubspot"
    )


def fetch_contacts(token: str) -> list[Contact]:
    """
    Calls the HubSpot contacts API and returns a normalised list of Contacts.

    Handles these error cases:
    - 401: token is expired or missing
    - 429: HubSpot rate limit hit
    - Empty response: returns empty list, not an error
    - Unexpected schema: catches KeyError/TypeError gracefully
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    params = {
        "properties": HUBSPOT_PROPERTIES,
        "limit": 100
    }

    try:
        response = httpx.get(
            HUBSPOT_CONTACTS_URL,
            headers=headers,
            params=params
        )
    except httpx.RequestError as e:
        raise ConnectionError(f"Failed to reach HubSpot: {e}")

    # token expired or invalid
    if response.status_code == 401:
        raise PermissionError("HubSpot token is expired or invalid.")

    # rate limit hit
    if response.status_code == 429:
        raise RuntimeError("HubSpot rate limit reached. Try again later.")

    # any other unexpected HTTP error
    if response.status_code != 200:
        raise RuntimeError(f"HubSpot returned unexpected status: {response.status_code}")

    # parse the response body
    try:
        data = response.json()
    except Exception:
        raise ValueError("HubSpot returned a response that could not be parsed as JSON.")

    # get the results list - might be empty, that's fine
    results = data.get("results", [])

    if not results:
        return []

    # normalise each contact - skip any that fail instead of crashing everything
    contacts = []
    for raw in results:
        try:
            contacts.append(normalise_contact(raw))
        except (AttributeError, KeyError, TypeError, ValueError):
            continue

    return contacts