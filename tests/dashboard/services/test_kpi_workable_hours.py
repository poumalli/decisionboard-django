"""
Tests TDD — #3 factorisation workable_hours, #4 relativedelta
"""

from datetime import date


# ─── #3 : _compute_workable_hours existe et est cohérente ────────────────────


class TestComputeWorkableHours:
    def test_function_exists_and_is_importable(self):
        from dashboard.services.kpi import _compute_workable_hours  # noqa: F401

    def test_returns_at_least_one(self):
        from dashboard.services.kpi import _compute_workable_hours

        # Même sur 1 jour, on retourne au minimum 1
        result = _compute_workable_hours(date(2025, 1, 1), date(2025, 1, 1))
        assert result >= 1

    def test_longer_period_gives_more_hours(self):
        from dashboard.services.kpi import _compute_workable_hours

        short = _compute_workable_hours(date(2025, 1, 1), date(2025, 1, 31))
        long_ = _compute_workable_hours(date(2025, 1, 1), date(2025, 6, 30))
        assert long_ > short

    def test_counts_only_weekdays(self):
        from dashboard.services.kpi import _compute_workable_hours

        # Jan-Mar 2025 : 64 jours ouvrés exacts (hors samedis/dimanches)
        # Jan=23, Fév=20, Mar=21 → 64 × 8h = 512h
        result = _compute_workable_hours(date(2025, 1, 1), date(2025, 3, 31))
        assert result == 64 * 8

    def test_weekend_only_period_returns_minimum(self):
        from dashboard.services.kpi import _compute_workable_hours

        # Samedi + Dimanche : 0 jours ouvrés → minimum garanti de 1h
        saturday = date(2025, 1, 4)
        sunday = date(2025, 1, 5)
        assert _compute_workable_hours(saturday, sunday) >= 1


# ─── #4 : get_date_range et _get_inactive_clients utilisent relativedelta ─────


class TestRelativeDelta:
    def test_get_date_range_12_months_back_is_close_to_365_days(self):
        from dashboard.services.kpi import get_date_range

        start, end = get_date_range(months_back=12)
        delta = (end - start).days
        # Avec relativedelta, exactement 365 ou 366 jours (bissextile)
        assert 364 <= delta <= 366

    def test_get_date_range_1_month_back_is_between_28_and_31_days(self):
        from dashboard.services.kpi import get_date_range

        start, end = get_date_range(months_back=1)
        delta = (end - start).days
        assert 28 <= delta <= 31

    def test_get_date_range_3_months_back_is_between_89_and_92_days(self):
        from dashboard.services.kpi import get_date_range

        start, end = get_date_range(months_back=3)
        delta = (end - start).days
        assert 89 <= delta <= 92
