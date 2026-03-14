import pytest

from app.contacts.models import Contact
from app.contacts.repository import normalise_contact


def test_normalise_full_contact():
    """Happy path - all fields present"""
    raw = {
        "id": "101",
        "properties": {
            "firstname": "Jan",
            "lastname": "de Vries",
            "email": "jan@example.com"
        }
    }
    contact = normalise_contact(raw)

    assert contact.id == "101"
    assert contact.name == "Jan de Vries"
    assert contact.email == "jan@example.com"
    assert contact.source == "hubspot"


def test_normalise_missing_lastname():
    """Contact has no lastname - should still work"""
    raw = {
        "id": "102",
        "properties": {
            "firstname": "Jan",
            "lastname": None,
            "email": "jan@example.com"
        }
    }
    contact = normalise_contact(raw)
    assert contact.name == "Jan"


def test_normalise_missing_firstname():
    """Contact has no firstname - should still work"""
    raw = {
        "id": "103",
        "properties": {
            "firstname": None,
            "lastname": "de Vries",
            "email": "jan@example.com"
        }
    }
    contact = normalise_contact(raw)
    assert contact.name == "de Vries"


def test_normalise_missing_email():
    """Contact has no email - should return empty string not crash"""
    raw = {
        "id": "104",
        "properties": {
            "firstname": "Jan",
            "lastname": "de Vries",
            "email": None
        }
    }
    contact = normalise_contact(raw)
    assert contact.email == ""


def test_normalise_empty_properties():
    """Contact has no properties at all - should not crash"""
    raw = {
        "id": "105",
        "properties": {}
    }
    contact = normalise_contact(raw)
    assert contact.id == "105"
    assert contact.name == ""
    assert contact.email == ""
    assert contact.source == "hubspot"


def test_normalise_source_is_always_hubspot():
    """Source field should always be hubspot regardless of input"""
    raw = {
        "id": "106",
        "properties": {
            "firstname": "Test",
            "lastname": "User",
            "email": "test@example.com"
        }
    }
    contact = normalise_contact(raw)
    assert contact.source == "hubspot"