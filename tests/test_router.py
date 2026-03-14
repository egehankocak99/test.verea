import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.contacts.models import Contact
from app.main import app


client = TestClient(app)


def test_get_contacts_success():
    """GET /contacts returns 200 with correct shape"""
    fake_contacts = [
        Contact(id="1", name="Jan de Vries", email="jan@example.com", source="hubspot"),
        Contact(id="2", name="Sofia Rossi", email="sofia@example.com", source="hubspot")
    ]

    with patch("app.contacts.router.get_contacts", return_value=fake_contacts):
        response = client.get("/contacts")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Jan de Vries"
    assert data[0]["source"] == "hubspot"


def test_get_contacts_empty():
    """GET /contacts returns 200 with empty list when no contacts"""
    with patch("app.contacts.router.get_contacts", return_value=[]):
        response = client.get("/contacts")

    assert response.status_code == 200
    assert response.json() == []


def test_get_contacts_401():
    """GET /contacts returns 401 when token is expired"""
    with patch(
        "app.contacts.router.get_contacts",
        side_effect=PermissionError("HubSpot token is expired or invalid.")
    ):
        response = client.get("/contacts")

    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_get_contacts_502():
    """GET /contacts returns 502 when rate limit is hit"""
    with patch(
        "app.contacts.router.get_contacts",
        side_effect=RuntimeError("HubSpot rate limit reached.")
    ):
        response = client.get("/contacts")

    assert response.status_code == 502


def test_get_contacts_503():
    """GET /contacts returns 503 when HubSpot is unreachable"""
    with patch(
        "app.contacts.router.get_contacts",
        side_effect=ConnectionError("Failed to reach HubSpot.")
    ):
        response = client.get("/contacts")

    assert response.status_code == 503


def test_get_contacts_500():
    """GET /contacts returns 500 for unexpected errors"""
    with patch(
        "app.contacts.router.get_contacts",
        side_effect=Exception("something totally unexpected")
    ):
        response = client.get("/contacts")

    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected error occurred."


def test_response_shape():
    """Every contact in response has exactly id, name, email, source"""
    fake_contacts = [
        Contact(id="1", name="Jan de Vries", email="jan@example.com", source="hubspot")
    ]

    with patch("app.contacts.router.get_contacts", return_value=fake_contacts):
        response = client.get("/contacts")

    contact = response.json()[0]
    assert set(contact.keys()) == {"id", "name", "email", "source"}