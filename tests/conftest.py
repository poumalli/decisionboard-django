"""Fixtures partagées entre tous les tests."""

import pytest
from datetime import date
from decimal import Decimal


@pytest.fixture
def fixed_start():
    return date(2025, 1, 1)


@pytest.fixture
def fixed_end():
    return date(2025, 6, 30)


@pytest.fixture
def mock_settings():
    """Objet BusinessSettings factice — pas de DB nécessaire."""

    class FakeSettings:
        monthly_revenue_target = Decimal("50000")
        occupation_rate_target = 75.0
        inactivity_months_threshold = 3
        receivables_alert_threshold = Decimal("10000")
        average_basket_target = Decimal("5000")

    return FakeSettings()


@pytest.fixture
def dw_dataset(db):
    """Un jeu de données DW minimal (1 fait complet) pour les tests d'intégration."""
    from dw.models import DimClient, DimDate, DimEmployee, DimService, FactSales

    dim_date = DimDate.objects.using("dw").create(
        full_date=date(2026, 1, 15),
        year=2026,
        quarter=1,
        month=1,
        month_name="Janvier",
        day=15,
        day_of_week=3,
        is_weekend=False,
    )
    dim_client = DimClient.objects.using("dw").create(
        source_id=1, company_name="Client DW Test", sector="tech", city="Fribourg"
    )
    dim_employee = DimEmployee.objects.using("dw").create(
        source_id=1,
        full_name="Consultant DW Test",
        role="senior",
        hire_date=date(2020, 1, 1),
        seniority_years=5,
    )
    dim_service = DimService.objects.using("dw").create(
        source_id=1,
        name="Service DW Test",
        category="it",
        base_price=Decimal("1000.00"),
        duration_hours=10,
    )
    return FactSales.objects.using("dw").create(
        date=dim_date,
        client=dim_client,
        employee=dim_employee,
        service=dim_service,
        source_appointment_id=1,
        duration_hours=10,
        unit_price=Decimal("100.00"),
        total_ht=Decimal("1000.00"),
        total_ttc=Decimal("1200.00"),
        is_paid=True,
    )
