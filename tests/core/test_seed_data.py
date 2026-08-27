"""Tests — core/management/commands/seed_data.py"""

import pytest
from django.core.management import call_command

from core.models import Appointment, Client, Employee, Invoice, Payment, Service


@pytest.mark.django_db
class TestSeedDataCommand:

    def test_creates_expected_reference_data(self):
        call_command("seed_data")
        assert Client.objects.count() == 16
        assert Employee.objects.count() == 8
        assert Service.objects.count() == 10
        assert Appointment.objects.count() > 0
        assert Invoice.objects.count() > 0
        assert Payment.objects.count() > 0

    def test_wipes_previous_data_before_reseeding(self):
        Client.objects.create(
            company_name="Junk",
            contact_name="x",
            email="junk@test.ch",
            sector="tech",
        )
        call_command("seed_data")
        assert not Client.objects.filter(company_name="Junk").exists()
        assert Client.objects.count() == 16

    def test_repeated_runs_stay_consistent(self):
        """Relancer plusieurs fois explore d'autres tirages aléatoires
        (le seed n'est fixé qu'une fois, au chargement du module) tout en
        vérifiant que les invariants structurels restent vrais à chaque fois."""
        for _ in range(5):
            call_command("seed_data")
            assert Client.objects.count() == 16
            assert Employee.objects.count() == 8
            assert Service.objects.count() == 10
            assert Appointment.objects.count() > 0
