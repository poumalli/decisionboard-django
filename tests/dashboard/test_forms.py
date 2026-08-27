"""Tests — dashboard/forms.py : validation BusinessSettingsForm."""

from dashboard.forms import BusinessSettingsForm


VALID_DATA = {
    "monthly_revenue_target": "50000",
    "occupation_rate_target": "75",
    "inactivity_months_threshold": "3",
    "receivables_alert_threshold": "10000",
    "average_basket_target": "5000",
}


class TestBusinessSettingsFormValidation:

    def test_valid_data_passes(self):
        form = BusinessSettingsForm(data=VALID_DATA)
        assert form.is_valid()

    def test_occupation_rate_above_100_is_rejected(self):
        data = {**VALID_DATA, "occupation_rate_target": "150"}
        form = BusinessSettingsForm(data=data)
        assert not form.is_valid()
        assert "occupation_rate_target" in form.errors

    def test_inactivity_threshold_below_1_is_rejected(self):
        data = {**VALID_DATA, "inactivity_months_threshold": "0"}
        form = BusinessSettingsForm(data=data)
        assert not form.is_valid()
        assert "inactivity_months_threshold" in form.errors
