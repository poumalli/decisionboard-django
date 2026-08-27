"""Tests — core/context_processors.py"""

import pytest
from django.contrib.auth.models import AnonymousUser, Group, User
from django.test import Client as HttpClient
from django.test import RequestFactory

from core.context_processors import etl_status, user_role


@pytest.mark.django_db(databases=["default", "dw"])
class TestUserRoleContextProcessor:

    def test_admin_group_member_sees_user_is_admin_true(self):
        user = User.objects.create_user(username="a", password="p")
        group, _ = Group.objects.get_or_create(name="Administrateur")
        user.groups.add(group)
        client = HttpClient()
        client.login(username="a", password="p")
        response = client.get("/")
        assert response.context["user_is_admin"] is True

    def test_consultant_group_member_sees_user_is_admin_false(self):
        user = User.objects.create_user(username="c", password="p")
        group, _ = Group.objects.get_or_create(name="Consultant")
        user.groups.add(group)
        client = HttpClient()
        client.login(username="c", password="p")
        response = client.get("/")
        assert response.context["user_is_admin"] is False

    def test_anonymous_user_sees_user_is_admin_false(self):
        request = RequestFactory().get("/")
        request.user = AnonymousUser()
        assert user_role(request) == {"user_is_admin": False}


class TestEtlStatusContextProcessor:

    def test_returns_none_when_etl_never_ran(self, monkeypatch, tmp_path):
        monkeypatch.setattr(
            "core.context_processors.settings.BASE_DIR", tmp_path
        )
        request = RequestFactory().get("/")
        assert etl_status(request) == {"etl_last_run": None}
