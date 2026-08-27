"""Tests — dashboard/views.py : export_csv avec choix du jeu de données."""

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
class TestExportCsvDatasetChoice:

    def test_default_dataset_is_consultants(self, logged_client):
        response = logged_client.get("/export/")
        content = response.content.decode()
        assert content.splitlines()[0] == "Consultant;Rôle;CA HT (CHF);Missions;Heures"

    def test_dataset_consultants_explicit(self, logged_client):
        response = logged_client.get("/export/?dataset=consultants")
        content = response.content.decode()
        assert content.splitlines()[0] == "Consultant;Rôle;CA HT (CHF);Missions;Heures"

    def test_dataset_revenue_returns_monthly_header(self, logged_client):
        response = logged_client.get("/export/?dataset=revenue")
        content = response.content.decode()
        assert content.splitlines()[0] == "Mois;CA HT (CHF)"

    def test_dataset_clients_returns_ranking_header(self, logged_client):
        response = logged_client.get("/export/?dataset=clients")
        content = response.content.decode()
        assert (
            content.splitlines()[0]
            == "Client;Secteur;Ville;CA HT (CHF);Missions;% du CA"
        )

    def test_unknown_dataset_falls_back_to_consultants(self, logged_client):
        response = logged_client.get("/export/?dataset=bogus")
        content = response.content.decode()
        assert content.splitlines()[0] == "Consultant;Rôle;CA HT (CHF);Missions;Heures"

    def test_filename_reflects_chosen_dataset(self, logged_client):
        response = logged_client.get("/export/?dataset=revenue")
        assert "decisionboard_revenue_" in response["Content-Disposition"]


@pytest.mark.django_db(databases=["default", "dw"])
class TestExportCsvWithData:

    def test_consultants_export_includes_data_row(self, logged_client, dw_dataset):
        response = logged_client.get("/export/?dataset=consultants")
        lines = response.content.decode().splitlines()
        assert len(lines) == 2
        assert "Consultant DW Test" in lines[1]

    def test_revenue_export_includes_data_row(self, logged_client, dw_dataset):
        response = logged_client.get("/export/?dataset=revenue")
        lines = response.content.decode().splitlines()
        assert len(lines) == 2
        assert "01/2026" in lines[1]

    def test_clients_export_includes_data_row(self, logged_client, dw_dataset):
        response = logged_client.get("/export/?dataset=clients")
        lines = response.content.decode().splitlines()
        assert len(lines) == 2
        assert "Client DW Test" in lines[1]
