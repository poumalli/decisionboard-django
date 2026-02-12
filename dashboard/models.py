"""
Modèles du dashboard — Paramètres stratégiques.

Singleton : une seule configuration active, avec des valeurs par défaut
sensées pour un cabinet de consulting suisse.
"""

from django.db import models


class BusinessSettings(models.Model):
    """
    Configuration stratégique unique du cabinet.
    Définit les objectifs et seuils utilisés par les indicateurs du dashboard.
    """

    monthly_revenue_target = models.DecimalField(
        "Objectif CA mensuel (CHF)",
        max_digits=12,
        decimal_places=2,
        default=50000,
        help_text="Chiffre d'affaires HT mensuel visé.",
    )
    occupation_rate_target = models.FloatField(
        "Objectif taux d'occupation (%)",
        default=75.0,
        help_text="Taux d'occupation cible des consultants.",
    )
    inactivity_months_threshold = models.IntegerField(
        "Seuil d'inactivité client (mois)",
        default=3,
        help_text="Nombre de mois sans mission pour considérer un client inactif.",
    )
    receivables_alert_threshold = models.DecimalField(
        "Seuil d'alerte créances (CHF)",
        max_digits=12,
        decimal_places=2,
        default=10000,
        help_text="Montant HT à partir duquel les créances déclenchent une alerte.",
    )
    average_basket_target = models.DecimalField(
        "Objectif panier moyen (CHF)",
        max_digits=10,
        decimal_places=2,
        default=5000,
        help_text="Panier moyen HT par mission visé.",
    )
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        verbose_name = "Paramètre stratégique"
        verbose_name_plural = "Paramètres stratégiques"

    def __str__(self):
        return f"Paramètres stratégiques (MAJ {self.updated_at:%d/%m/%Y})"

    @classmethod
    def load(cls):
        """
        Retourne la configuration active (singleton).
        Crée une configuration par défaut si aucune n'existe.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        """Force le singleton : pk toujours = 1."""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Empêche la suppression de la configuration."""
        pass
