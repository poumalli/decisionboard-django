"""
Tests — dashboard/views.py
#6 : _load_settings() supprimé, BusinessSettings.load() appelé directement
"""

import pytest
from django.test import Client as HttpClient
from django.contrib.auth.models import Group, User


@pytest.fixture
def logged_client(db):
    """Utilisateur connecté et membre du groupe Consultant (accès dashboard)."""
    user = User.objects.create_user(username="testuser", password="testpass")
    group, _ = Group.objects.get_or_create(name="Consultant")
    user.groups.add(group)
    client = HttpClient()
    client.login(username="testuser", password="testpass")
    return client


class TestViewsDoNotExpose_load_settings:
    def test_load_settings_helper_is_removed_from_views(self):
        """#6 : _load_settings ne doit plus exister dans views.py."""
        import dashboard.views as views

        assert not hasattr(
            views, "_load_settings"
        ), "_load_settings() est encore présent dans views.py — supprimez-le."


class TestDashboardViewAuth:
    def test_unauthenticated_user_is_redirected_to_login(self, db):
        client = HttpClient()
        response = client.get("/")
        assert response.status_code == 302
        assert "/login/" in response["Location"]

    @pytest.mark.django_db(databases=["default", "dw"])
    def test_authenticated_user_gets_200(self, logged_client):
        response = logged_client.get("/")
        assert response.status_code == 200

    def test_revenue_page_requires_auth(self, db):
        client = HttpClient()
        response = client.get("/revenue/")
        assert response.status_code == 302

    def test_consultants_page_requires_auth(self, db):
        client = HttpClient()
        response = client.get("/consultants/")
        assert response.status_code == 302

    def test_clients_page_requires_auth(self, db):
        client = HttpClient()
        response = client.get("/clients/")
        assert response.status_code == 302
