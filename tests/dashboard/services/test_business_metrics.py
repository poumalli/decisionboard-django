"""
Tests unitaires — dashboard/services/business_metrics.py

Aucune base de données nécessaire : toutes les fonctions sont pures.
"""

from decimal import Decimal

from dashboard.services.business_metrics import (
    _status_from_pct,
    compute_strategic_metrics,
)


# ─── _status_from_pct ────────────────────────────────────────────────────────


class TestStatusFromPct:
    def test_returns_success_at_or_above_good_threshold(self):
        assert _status_from_pct(90) == "success"
        assert _status_from_pct(100) == "success"
        assert _status_from_pct(150) == "success"

    def test_returns_warning_between_acceptable_and_good(self):
        assert _status_from_pct(70) == "warning"
        assert _status_from_pct(80) == "warning"
        assert _status_from_pct(89) == "warning"

    def test_returns_danger_below_acceptable_threshold(self):
        assert _status_from_pct(0) == "danger"
        assert _status_from_pct(50) == "danger"
        assert _status_from_pct(69) == "danger"

    def test_custom_thresholds_are_respected(self):
        assert _status_from_pct(80, good=80, acceptable=60) == "success"
        assert _status_from_pct(65, good=80, acceptable=60) == "warning"
        assert _status_from_pct(59, good=80, acceptable=60) == "danger"


# ─── compute_strategic_metrics ───────────────────────────────────────────────


class TestComputeStrategicMetrics:
    def test_returns_empty_dict_when_settings_is_none(self):
        result = compute_strategic_metrics({}, None)
        assert result == {}

    def test_returns_empty_dict_when_settings_is_falsy(self):
        result = compute_strategic_metrics({}, False)
        assert result == {}

    def test_revenue_achievement_pct_calculated_correctly(self, mock_settings):
        # 6 mois × 50 000 CHF cible = 300 000 CHF. CA réel = 240 000 → 80%
        data = {
            "total_revenue": Decimal("240000"),
            "monthly_revenue": [{}] * 6,
            "utilization_rate": {"average": 0},
            "average_basket": Decimal("0"),
            "unpaid": {"amount": 0},
        }
        result = compute_strategic_metrics(data, mock_settings)
        assert result["revenue"]["achievement_pct"] == 80.0

    def test_revenue_gap_is_negative_when_below_target(self, mock_settings):
        data = {
            "total_revenue": Decimal("240000"),
            "monthly_revenue": [{}] * 6,
            "utilization_rate": {"average": 0},
            "average_basket": Decimal("0"),
            "unpaid": {"amount": 0},
        }
        result = compute_strategic_metrics(data, mock_settings)
        assert result["revenue"]["gap"] < 0

    def test_revenue_status_is_success_when_above_90_pct(self, mock_settings):
        # 6 mois × 50 000 = 300 000. CA réel = 285 000 → 95%
        data = {
            "total_revenue": Decimal("285000"),
            "monthly_revenue": [{}] * 6,
            "utilization_rate": {"average": 0},
            "average_basket": Decimal("0"),
            "unpaid": {"amount": 0},
        }
        result = compute_strategic_metrics(data, mock_settings)
        assert result["revenue"]["status"] == "success"

    def test_revenue_period_target_scales_with_nb_months(self, mock_settings):
        data = {
            "total_revenue": Decimal("0"),
            "monthly_revenue": [{}] * 3,
            "utilization_rate": {"average": 0},
            "average_basket": Decimal("0"),
            "unpaid": {"amount": 0},
        }
        result = compute_strategic_metrics(data, mock_settings)
        assert result["revenue"]["period_target"] == 150000.0

    def test_occupation_achievement_pct_calculated_correctly(self, mock_settings):
        # Taux réel 60 / cible 75 = 80%
        data = {
            "total_revenue": Decimal("0"),
            "monthly_revenue": [],
            "utilization_rate": {"average": 60.0},
            "average_basket": Decimal("0"),
            "unpaid": {"amount": 0},
        }
        result = compute_strategic_metrics(data, mock_settings)
        assert result["occupation"]["achievement_pct"] == 80.0
        assert result["occupation"]["actual"] == 60.0
        assert result["occupation"]["target"] == 75.0

    def test_occupation_status_is_danger_when_far_below_target(self, mock_settings):
        data = {
            "total_revenue": Decimal("0"),
            "monthly_revenue": [],
            "utilization_rate": {"average": 30.0},
            "average_basket": Decimal("0"),
            "unpaid": {"amount": 0},
        }
        result = compute_strategic_metrics(data, mock_settings)
        assert result["occupation"]["status"] == "danger"

    def test_basket_gap_positive_when_above_target(self, mock_settings):
        # Panier moyen réel = 6000, cible = 5000 → gap = +1000
        data = {
            "total_revenue": Decimal("0"),
            "monthly_revenue": [],
            "utilization_rate": {"average": 0},
            "average_basket": Decimal("6000"),
            "unpaid": {"amount": 0},
        }
        result = compute_strategic_metrics(data, mock_settings)
        assert result["basket"]["gap"] == 1000.0
        assert result["basket"]["status"] == "success"

    def test_receivables_alert_triggered_at_threshold(self, mock_settings):
        # Seuil = 10 000. Montant = exactement 10 000 → alerte
        data = {
            "total_revenue": Decimal("0"),
            "monthly_revenue": [],
            "utilization_rate": {"average": 0},
            "average_basket": Decimal("0"),
            "unpaid": {"amount": 10000},
        }
        result = compute_strategic_metrics(data, mock_settings)
        assert result["receivables"]["is_alert"] is True
        assert result["receivables"]["status"] == "danger"

    def test_receivables_no_alert_below_threshold(self, mock_settings):
        data = {
            "total_revenue": Decimal("0"),
            "monthly_revenue": [],
            "utilization_rate": {"average": 0},
            "average_basket": Decimal("0"),
            "unpaid": {"amount": 9999},
        }
        result = compute_strategic_metrics(data, mock_settings)
        assert result["receivables"]["is_alert"] is False
        assert result["receivables"]["status"] == "success"

    def test_revenue_key_absent_when_monthly_target_is_zero(self, mock_settings):
        mock_settings.monthly_revenue_target = Decimal("0")
        data = {
            "total_revenue": Decimal("50000"),
            "monthly_revenue": [{}] * 3,
            "utilization_rate": {"average": 0},
            "average_basket": Decimal("0"),
            "unpaid": {"amount": 0},
        }
        result = compute_strategic_metrics(data, mock_settings)
        assert "revenue" not in result
