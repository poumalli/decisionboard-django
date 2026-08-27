"""Tests — core/permissions.py : décorateurs admin_required / consultant_required."""

import pytest
from django.contrib.auth.models import User
from django.test import Client as HttpClient


@pytest.mark.django_db(databases=["default", "dw"])
class TestConsultantRequired:

    def test_superuser_without_group_can_access_dashboard(self):
        User.objects.create_superuser(username="root", email="", password="p")
        client = HttpClient()
        client.login(username="root", password="p")
        response = client.get("/")
        assert response.status_code == 200

    def test_user_without_any_group_is_forbidden(self):
        User.objects.create_user(username="nogroup", password="p")
        client = HttpClient()
        client.login(username="nogroup", password="p")
        response = client.get("/")
        assert response.status_code == 403
