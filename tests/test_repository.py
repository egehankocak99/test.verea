import pytest
from unittest.mock import MagicMock, patch

from app.contacts.repository import fetch_contacts


def make_mock_response(status_code: int, json_data: dict = None):
    """Helper that creates a fake httpx response"""
    mock = MagicMock()
    mock.status_code = status_code
    if json_data is not None:
        mock.json.return_value = json_data
    return mock


def test_fetch_contacts_success():
    """Happy path - HubSpot returns two contacts"""
    fake_response = make_mock_response(200, {
        "results": [
            {
                "id": "1",
                "properties": {
                    "firstname": "Jan",
                    "lastname": "de Vries",
                    "email": "jan@example.com"
                }
            },
            {
                "id": "2",
                "properties": {
                    "firstname": "Sofia",
                    "lastname": "Rossi",
                    "email": "sofia@example.com"
                }
            }
        ]
    })

    with patch("app.contacts.repository.httpx.get", return_value=fake_response):
        contacts = fetch_contacts("fake-token")

    assert len(contacts) == 2
    assert contacts[0].name == "Jan de Vries"
    assert contacts[1].email == "sofia@example.com"


def test_fetch_contacts_empty_results():
    """HubSpot returns 200 but no contacts - should return empty list"""
    fake_response = make_mock_response(200, {"results": []})

    with patch("app.contacts.repository.httpx.get", return_value=fake_response):
        contacts = fetch_contacts("fake-token")

    assert contacts == []


def test_fetch_contacts_401():
    """Expired or missing token - should raise PermissionError"""
    fake_response = make_mock_response(401)

    with patch("app.contacts.repository.httpx.get", return_value=fake_response):
        with pytest.raises(PermissionError):
            fetch_contacts("expired-token")


def test_fetch_contacts_429():
    """Rate limit hit - should raise RuntimeError"""
    fake_response = make_mock_response(429)

    with patch("app.contacts.repository.httpx.get", return_value=fake_response):
        with pytest.raises(RuntimeError):
            fetch_contacts("fake-token")


def test_fetch_contacts_unexpected_status():
    """HubSpot returns something unexpected like 503 - should raise RuntimeError"""
    fake_response = make_mock_response(503)

    with patch("app.contacts.repository.httpx.get", return_value=fake_response):
        with pytest.raises(RuntimeError):
            fetch_contacts("fake-token")


def test_fetch_contacts_bad_json():
    """HubSpot returns unparseable response - should raise ValueError"""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.side_effect = Exception("not valid json")

    with patch("app.contacts.repository.httpx.get", return_value=mock):
        with pytest.raises(ValueError):
            fetch_contacts("fake-token")


def test_fetch_contacts_skips_malformed_contact():
    """One bad contact in results - should skip it and return the good ones"""
    fake_response = make_mock_response(200, {
        "results": [
            {
                "id": "1",
                "properties": {
                    "firstname": "Jan",
                    "lastname": "de Vries",
                    "email": "jan@example.com"
                }
            },
            None
        ]
    })

    with patch("app.contacts.repository.httpx.get", return_value=fake_response):
        contacts = fetch_contacts("fake-token")

    assert len(contacts) == 1
    assert contacts[0].name == "Jan de Vries"
