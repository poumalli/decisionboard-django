"""Tests — dashboard/views.py : rendu des pages revenue/consultants/clients/settings."""

import pytest
from django.contrib.auth.models import Group, User
from django.test import Client as HttpClient


@pytest.fixture
def logged_client(db):
    user = User.objects.create_user(username="testuser", password="testpass")
    group, _ = Group.objects.get_or_create(name="Consultant")
    user.groups.add(group)
    client = HttpClient()
    client.login(username="testuser", password="testpass")
    return client


@pytest.mark.django_db(databases=["default", "dw"])
class TestRevenuePageRendering:

    def test_revenue_page_renders_with_data(self, logged_client, dw_dataset):
        response = logged_client.get("/revenue/")
        assert response.status_code == 200

    def test_revenue_page_with_category_filter(self, logged_client, dw_dataset):
        response = logged_client.get("/revenue/?category=it")
        assert response.status_code == 200
        assert response.context["category_filter"] == "it"


@pytest.mark.django_db(databases=["default", "dw"])
class TestConsultantsPageRendering:

    def test_consultants_page_renders_with_data(self, logged_client, dw_dataset):
        response = logged_client.get("/consultants/")
        assert response.status_code == 200
        assert response.context["consultant_count"] == 1


@pytest.mark.django_db(databases=["default", "dw"])
class TestClientsPageRendering:

    def test_clients_page_renders_with_data(self, logged_client, dw_dataset):
        response = logged_client.get("/clients/")
        assert response.status_code == 200
        assert response.context["total_clients"] == 1


@pytest.mark.django_db(databases=["default", "dw"])
class TestDatePresets:

    @pytest.mark.parametrize("preset", ["month", "quarter", "year"])
    def test_dashboard_accepts_period_preset(self, logged_client, preset):
        response = logged_client.get(f"/?preset={preset}")
        assert response.status_code == 200
        assert response.context["active_preset"] == preset

    def test_dashboard_falls_back_on_invalid_date_range(self, logged_client):
        response = logged_client.get("/?start=not-a-date&end=also-not-a-date")
        assert response.status_code == 200


@pytest.mark.django_db(databases=["default", "dw"])
class TestDashboardHomeWithData:

    def test_home_page_computes_utilization_rate_with_data(
        self, logged_client, dw_dataset
    ):
        response = logged_client.get("/")
        assert response.status_code == 200
        assert response.context["utilization_rate"]["details"]


@pytest.mark.django_db(databases=["default", "dw"])
class TestSettingsViewGet:

    def test_get_settings_page_shows_form(self, logged_client):
        response = logged_client.get("/settings/")
        assert response.status_code == 200
        assert "form" in response.context


@pytest.mark.django_db(databases=["default", "dw"])
class TestSettingsViewPost:

    def test_post_valid_settings_saves_and_redirects(self, logged_client):
        response = logged_client.post(
            "/settings/",
            {
                "monthly_revenue_target": "60000",
                "occupation_rate_target": "80",
                "inactivity_months_threshold": "4",
                "receivables_alert_threshold": "12000",
                "average_basket_target": "6000",
            },
        )
        assert response.status_code == 302

    def test_post_invalid_settings_reshows_form_with_errors(self, logged_client):
        response = logged_client.post(
            "/settings/",
            {
                "monthly_revenue_target": "60000",
                "occupation_rate_target": "150",  # hors de 0-100
                "inactivity_months_threshold": "4",
                "receivables_alert_threshold": "12000",
                "average_basket_target": "6000",
            },
        )
        assert response.status_code == 200
        assert response.context["form"].errors
