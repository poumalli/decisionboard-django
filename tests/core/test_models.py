"""Tests — core/models.py : représentations __str__."""

from datetime import date

import pytest

from core.models import Appointment, Client, Employee, Invoice, Payment, Service


@pytest.fixture
def sample_appointment(db):
    client_obj = Client.objects.create(
        company_name="Client Str", contact_name="A", email="str@test.ch", sector="tech"
    )
    employee = Employee.objects.create(
        first_name="Ana",
        last_name="Str",
        email="ana.str@test.ch",
        role="senior",
        hire_date=date(2020, 1, 1),
        hourly_rate=150,
    )
    service = Service.objects.create(
        name="Service Str", category="it", base_price=500, duration_hours=5
    )
    return Appointment.objects.create(
        client=client_obj,
        employee=employee,
        service=service,
        date=date(2026, 1, 1),
        duration_hours=5,
        status="realise",
    )


@pytest.mark.django_db
class TestCoreModelStrRepresentations:

    def test_appointment_str_combines_service_client_and_date(
        self, sample_appointment
    ):
        assert str(sample_appointment) == "Service Str - Client Str (2026-01-01)"

    def test_invoice_str_is_invoice_number(self, sample_appointment):
        invoice = Invoice.objects.create(
            appointment=sample_appointment,
            invoice_number="AUD-STR-0001",
            amount_ht=500,
            amount_ttc=600,
            issued_date=date(2026, 1, 5),
            due_date=date(2026, 2, 5),
        )
        assert str(invoice) == "AUD-STR-0001"

    def test_payment_str_includes_amount_and_invoice(self, sample_appointment):
        invoice = Invoice.objects.create(
            appointment=sample_appointment,
            invoice_number="AUD-STR-0002",
            amount_ht=500,
            amount_ttc=600,
            issued_date=date(2026, 1, 5),
            due_date=date(2026, 2, 5),
        )
        payment = Payment.objects.create(
            invoice=invoice, amount=600, payment_date=date(2026, 2, 1), method="carte"
        )
        assert str(payment) == "Paiement 600 CHF - AUD-STR-0002"
