"""
Tests unitaires et d'intégration — dashboard/services/kpi.py
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from dashboard.services.kpi import (
    _compute_variation,
    _get_previous_period,
    get_date_range,
)


# ─── _compute_variation ──────────────────────────────────────────────────────


class TestComputeVariation:
    def test_returns_correct_percentage(self):
        assert _compute_variation(110, 100) == 10.0

    def test_returns_negative_when_current_lower(self):
        assert _compute_variation(80, 100) == -20.0

    def test_returns_100_when_previous_is_zero_and_current_positive(self):
        assert _compute_variation(500, 0) == 100.0

    def test_returns_0_when_both_are_zero(self):
        assert _compute_variation(0, 0) == 0.0

    def test_rounds_to_one_decimal(self):
        assert _compute_variation(1, 3) == -66.7

    def test_handles_decimal_types(self):
        assert _compute_variation(Decimal("150"), Decimal("100")) == 50.0

    def test_handles_none_as_zero(self):
        assert _compute_variation(None, 100) == -100.0
        assert _compute_variation(100, None) == 100.0


# ─── _get_previous_period ────────────────────────────────────────────────────


class TestGetPreviousPeriod:
    def test_previous_period_has_same_duration(self):
        start = date(2025, 4, 1)
        end = date(2025, 6, 30)
        prev_start, prev_end = _get_previous_period(start, end)
        duration = (end - start).days
        prev_duration = (prev_end - prev_start).days
        assert prev_duration == duration

    def test_previous_period_ends_day_before_start(self):
        start = date(2025, 4, 1)
        end = date(2025, 6, 30)
        prev_start, prev_end = _get_previous_period(start, end)
        assert prev_end == start - timedelta(days=1)

    def test_previous_period_does_not_overlap(self):
        start = date(2025, 4, 1)
        end = date(2025, 6, 30)
        prev_start, prev_end = _get_previous_period(start, end)
        assert prev_end < start


# ─── get_date_range ──────────────────────────────────────────────────────────


class TestGetDateRange:
    def test_returns_tuple_of_two_dates(self):
        result = get_date_range()
        assert len(result) == 2

    def test_end_date_is_today(self):
        _, end = get_date_range()
        assert end == date.today()

    def test_start_date_is_before_end_date(self):
        start, end = get_date_range()
        assert start < end

    def test_custom_months_back(self):
        start, end = get_date_range(months_back=1)
        assert (end - start).days <= 31


# ─── Bug #2 : get_revenue_summary respecte le filtre catégorie ───────────────


class TestGetRevenueSummaryMonthlyFilter:
    """
    Vérifie que monthly_revenue applique le filtre de catégorie.
    RED : ce test échoue AVANT le fix du bug #2.
    """

    @pytest.mark.django_db(databases=["default", "dw"])
    def test_monthly_revenue_respects_category_filter(self):
        """
        Avec deux ventes dans des catégories différentes sur le même mois,
        filtrer par une catégorie ne doit retourner que le CA de cette catégorie.
        """
        from datetime import date as dt
        from dw.models import DimDate, DimClient, DimEmployee, DimService, FactSales
        from dashboard.services.kpi import get_revenue_summary

        target_month = dt(2025, 3, 15)
        start = dt(2025, 1, 1)
        end = dt(2025, 12, 31)

        # Dimension Date
        dim_date, _ = DimDate.objects.using("dw").get_or_create(
            full_date=target_month,
            defaults={
                "year": 2025,
                "quarter": 1,
                "month": 3,
                "month_name": "Mars",
                "day": 15,
                "day_of_week": 6,
                "is_weekend": True,
            },
        )

        # Dimension Client
        client, _ = DimClient.objects.using("dw").get_or_create(
            source_id=9901,
            defaults={"company_name": "Test Corp", "sector": "tech", "city": "Paris"},
        )

        # Dimension Employé
        employee, _ = DimEmployee.objects.using("dw").get_or_create(
            source_id=9901,
            defaults={
                "full_name": "Test User",
                "role": "consultant",
                "hire_date": dt(2020, 1, 1),
                "seniority_years": 5,
            },
        )

        # Deux services — catégories différentes
        svc_it, _ = DimService.objects.using("dw").get_or_create(
            source_id=9901,
            defaults={
                "name": "Migration cloud",
                "category": "it",
                "base_price": Decimal("8000"),
                "duration_hours": 60,
            },
        )
        svc_strat, _ = DimService.objects.using("dw").get_or_create(
            source_id=9902,
            defaults={
                "name": "Audit stratégique",
                "category": "strategie",
                "base_price": Decimal("5000"),
                "duration_hours": 40,
            },
        )

        # Vente IT : 10 000 CHF
        FactSales.objects.using("dw").create(
            date=dim_date,
            client=client,
            employee=employee,
            service=svc_it,
            source_appointment_id=99901,
            duration_hours=10,
            unit_price=Decimal("150"),
            total_ht=Decimal("10000"),
            total_ttc=Decimal("12000"),
            is_paid=True,
        )

        # Vente Stratégie : 5 000 CHF
        FactSales.objects.using("dw").create(
            date=dim_date,
            client=client,
            employee=employee,
            service=svc_strat,
            source_appointment_id=99902,
            duration_hours=8,
            unit_price=Decimal("150"),
            total_ht=Decimal("5000"),
            total_ttc=Decimal("6000"),
            is_paid=True,
        )

        result = get_revenue_summary(start, end, category="it")

        # Le CA total filtré doit être 10 000 (uniquement IT)
        assert float(result["total_revenue"]) == 10000.0

        # monthly_revenue doit aussi ne contenir que le CA IT
        total_monthly = sum(float(r["revenue"]) for r in result["monthly_revenue"])
        assert (
            total_monthly == 10000.0
        ), f"monthly_revenue inclut du CA hors catégorie 'it' : {result['monthly_revenue']}"
