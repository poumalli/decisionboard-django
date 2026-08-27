"""Tests — core/management/commands/setup_groups.py"""

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command


@pytest.mark.django_db
class TestSetupGroupsCommand:

    def test_creates_both_groups(self):
        # core.apps._create_default_groups (signal post_migrate) les a déjà
        # créés une fois pour la session de tests — on repart d'une table
        # vide pour vérifier la branche "création" elle-même.
        Group.objects.all().delete()
        call_command("setup_groups")
        assert Group.objects.filter(name="Administrateur").exists()
        assert Group.objects.filter(name="Consultant").exists()

    def test_is_idempotent_on_second_run(self):
        call_command("setup_groups")
        call_command("setup_groups")
        assert Group.objects.filter(name="Administrateur").count() == 1
        assert Group.objects.filter(name="Consultant").count() == 1
