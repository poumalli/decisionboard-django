"""Tests — bouton ETL visible dans la sidebar (admin uniquement)."""

import pytest
from django.contrib.auth.models import Group, User
from django.test import Client as HttpClient


@pytest.fixture
def admin_client(db):
    user = User.objects.create_user(username="admin", password="p")
    group, _ = Group.objects.get_or_create(name="Administrateur")
    user.groups.add(group)
    client = HttpClient()
    client.login(username="admin", password="p")
    return client


@pytest.fixture
def consultant_client(db):
    user = User.objects.create_user(username="cons", password="p")
    group, _ = Group.objects.get_or_create(name="Consultant")
    user.groups.add(group)
    client = HttpClient()
    client.login(username="cons", password="p")
    return client


@pytest.mark.django_db(databases=["default", "dw"])
class TestEtlButtonVisibility:

    def test_admin_sees_etl_button_on_dashboard(self, admin_client):
        response = admin_client.get("/")
        assert "Lancer l&#x27;ETL" in response.content.decode() or (
            "Lancer l'ETL" in response.content.decode()
        )

    def test_consultant_does_not_see_etl_button(self, consultant_client):
        response = consultant_client.get("/")
        assert "Lancer l'ETL" not in response.content.decode()
        assert "Lancer l&#x27;ETL" not in response.content.decode()
