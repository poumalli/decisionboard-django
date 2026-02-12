"""
Formulaires du dashboard — Paramètres stratégiques.
"""

from django import forms

from .models import BusinessSettings


class BusinessSettingsForm(forms.ModelForm):
    """Formulaire de configuration des objectifs stratégiques."""

    class Meta:
        model = BusinessSettings
        fields = [
            "monthly_revenue_target",
            "occupation_rate_target",
            "inactivity_months_threshold",
            "receivables_alert_threshold",
            "average_basket_target",
        ]
        widgets = {
            "monthly_revenue_target": forms.NumberInput(attrs={
                "min": "0",
                "step": "100",
            }),
            "occupation_rate_target": forms.NumberInput(attrs={
                "min": "0",
                "max": "100",
                "step": "1",
            }),
            "inactivity_months_threshold": forms.NumberInput(attrs={
                "min": "1",
                "max": "24",
            }),
            "receivables_alert_threshold": forms.NumberInput(attrs={
                "min": "0",
                "step": "100",
            }),
            "average_basket_target": forms.NumberInput(attrs={
                "min": "0",
                "step": "100",
            }),
        }

    def clean_occupation_rate_target(self):
        value = self.cleaned_data["occupation_rate_target"]
        if not 0 <= value <= 100:
            raise forms.ValidationError("Le taux doit être entre 0 et 100%.")
        return value

    def clean_inactivity_months_threshold(self):
        value = self.cleaned_data["inactivity_months_threshold"]
        if value < 1:
            raise forms.ValidationError("Le seuil doit être d'au moins 1 mois.")
        return value
