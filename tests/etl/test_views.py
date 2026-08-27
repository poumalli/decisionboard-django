"""Tests — etl/views.py : run_etl_view."""

import pytest
from django.contrib.auth.models import Group, User
from django.test import Client as HttpClient


@pytest.fixture
def admin_client(db):
    user = User.objects.create_user(username="admin", password="testpass")
    group, _ = Group.objects.get_or_create(name="Administrateur")
    user.groups.add(group)
    client = HttpClient()
    client.login(username="admin", password="testpass")
    return client


@pytest.mark.django_db(databases=["default", "dw"])
class TestRunEtlViewRedirect:
    def test_redirects_to_safe_relative_next(self, admin_client):
        response = admin_client.post("/etl/run/", {"next": "/clients/"})
        assert response["Location"] == "/clients/"

    def test_ignores_external_next_and_redirects_home(self, admin_client):
        response = admin_client.post(
            "/etl/run/", {"next": "https://evil.example.com/phishing"}
        )
        assert response["Location"] == "/"

    def test_ignores_protocol_relative_next_and_redirects_home(self, admin_client):
        response = admin_client.post("/etl/run/", {"next": "//evil.example.com"})
        assert response["Location"] == "/"

    def test_get_request_redirects_without_running_etl(self, admin_client):
        response = admin_client.get("/etl/run/")
        assert response["Location"] == "/"

    def test_command_failure_shows_error_message_and_still_redirects(
        self, admin_client, monkeypatch
    ):
        def _boom(*args, **kwargs):
            raise RuntimeError("panne simulée")

        monkeypatch.setattr("etl.views.call_command", _boom)
        response = admin_client.post("/etl/run/", {"next": "/"}, follow=True)
        assert response.status_code == 200
        messages = list(response.context["messages"])
        assert any("panne simulée" in str(m) for m in messages)
