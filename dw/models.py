"""
Modèles Data Warehouse — Schéma en étoile.

4 dimensions + 1 table de faits pour l'analyse décisionnelle.
Les données sont alimentées par le pipeline ETL depuis la base OLTP.
"""

from django.db import models


class DimDate(models.Model):
    """Dimension temporelle : jour, mois, trimestre, année."""

    full_date = models.DateField("Date complète", unique=True, db_index=True)
    year = models.IntegerField("Année")
    quarter = models.IntegerField("Trimestre")
    month = models.IntegerField("Mois")
    month_name = models.CharField("Nom du mois", max_length=20)
    day = models.IntegerField("Jour")
    day_of_week = models.IntegerField("Jour de la semaine")
    is_weekend = models.BooleanField("Weekend", default=False)

    class Meta:
        db_table = "dim_date"
        ordering = ["full_date"]
        verbose_name = "Dimension Date"

    def __str__(self):
        return str(self.full_date)


class DimClient(models.Model):
    """Dimension client : informations dénormalisées pour l'analyse."""

    source_id = models.IntegerField("ID source OLTP", unique=True)
    company_name = models.CharField("Raison sociale", max_length=200, db_index=True)
    sector = models.CharField("Secteur", max_length=50, db_index=True)
    city = models.CharField("Ville", max_length=100, blank=True)

    class Meta:
        db_table = "dim_client"
        ordering = ["company_name"]
        verbose_name = "Dimension Client"

    def __str__(self):
        return self.company_name


class DimEmployee(models.Model):
    """Dimension employé : profil du consultant pour l'analyse de performance."""

    source_id = models.IntegerField("ID source OLTP", unique=True)
    full_name = models.CharField("Nom complet", max_length=100, db_index=True)
    role = models.CharField("Rôle", max_length=20, db_index=True)
    hire_date = models.DateField("Date d'embauche")
    seniority_years = models.IntegerField("Ancienneté (années)", default=0)

    class Meta:
        db_table = "dim_employee"
        ordering = ["full_name"]
        verbose_name = "Dimension Employé"

    def __str__(self):
        return self.full_name


class DimService(models.Model):
    """Dimension service : prestation analysée."""

    source_id = models.IntegerField("ID source OLTP", unique=True)
    name = models.CharField("Nom du service", max_length=200)
    category = models.CharField("Catégorie", max_length=50, db_index=True)
    base_price = models.DecimalField("Prix de base HT", max_digits=10, decimal_places=2)
    duration_hours = models.IntegerField("Durée estimée (h)")

    class Meta:
        db_table = "dim_service"
        ordering = ["category", "name"]
        verbose_name = "Dimension Service"

    def __str__(self):
        return self.name


class FactSales(models.Model):
    """
    Table de faits — Ventes / missions facturées.
    Grain : 1 mission = 1 ligne.
    """

    date = models.ForeignKey(DimDate, on_delete=models.CASCADE, verbose_name="Date")
    client = models.ForeignKey(DimClient, on_delete=models.CASCADE, verbose_name="Client")
    employee = models.ForeignKey(DimEmployee, on_delete=models.CASCADE, verbose_name="Consultant")
    service = models.ForeignKey(DimService, on_delete=models.CASCADE, verbose_name="Service")

    source_appointment_id = models.IntegerField("ID mission source", unique=True)

    duration_hours = models.IntegerField("Durée (heures)")
    unit_price = models.DecimalField("Taux horaire (CHF)", max_digits=8, decimal_places=2)
    total_ht = models.DecimalField("Montant HT (CHF)", max_digits=10, decimal_places=2)
    total_ttc = models.DecimalField("Montant TTC (CHF)", max_digits=10, decimal_places=2)
    is_paid = models.BooleanField("Payée", default=False)

    class Meta:
        db_table = "fact_sales"
        ordering = ["-date"]
        verbose_name = "Fait Vente"
        verbose_name_plural = "Faits Ventes"
        indexes = [
            models.Index(fields=["date", "client"], name="idx_fact_date_client"),
            models.Index(fields=["date", "employee"], name="idx_fact_date_employee"),
            models.Index(fields=["date", "service"], name="idx_fact_date_service"),
            models.Index(fields=["is_paid"], name="idx_fact_is_paid"),
        ]

    def __str__(self):
        return f"Vente {self.source_appointment_id} - {self.total_ht} CHF HT"
