"""
Modèles OLTP — Base opérationnelle du cabinet de consulting.

6 tables représentant l'activité quotidienne :
Client, Employee, Service, Appointment, Invoice, Payment.
"""

from django.db import models
from django.utils import timezone


class Client(models.Model):
    """Entreprise cliente du cabinet de consulting."""

    SECTOR_CHOICES = [
        ("finance", "Finance"),
        ("tech", "Technologie"),
        ("sante", "Santé"),
        ("industrie", "Industrie"),
        ("education", "Éducation"),
        ("commerce", "Commerce"),
    ]

    company_name = models.CharField("Raison sociale", max_length=200)
    contact_name = models.CharField("Nom du contact", max_length=100)
    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Téléphone", max_length=20, blank=True)
    address = models.CharField("Adresse", max_length=300, blank=True)
    city = models.CharField("Ville", max_length=100, blank=True)
    sector = models.CharField("Secteur", max_length=50, choices=SECTOR_CHOICES)
    created_at = models.DateField("Date de création", default=timezone.now)

    class Meta:
        db_table = "clients"
        ordering = ["company_name"]
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.company_name


class Employee(models.Model):
    """Consultant ou employé du cabinet."""

    ROLE_CHOICES = [
        ("consultant", "Consultant"),
        ("senior", "Consultant Senior"),
        ("manager", "Manager"),
    ]

    first_name = models.CharField("Prénom", max_length=50)
    last_name = models.CharField("Nom", max_length=50)
    email = models.EmailField("Email", unique=True)
    role = models.CharField("Rôle", max_length=20, choices=ROLE_CHOICES)
    hire_date = models.DateField("Date d'embauche")
    hourly_rate = models.DecimalField("Taux horaire (CHF)", max_digits=8, decimal_places=2)
    is_active = models.BooleanField("Actif", default=True)

    class Meta:
        db_table = "employees"
        ordering = ["last_name", "first_name"]
        verbose_name = "Employé"
        verbose_name_plural = "Employés"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Service(models.Model):
    """Prestation proposée par le cabinet."""

    CATEGORY_CHOICES = [
        ("strategie", "Stratégie"),
        ("it", "IT & Digital"),
        ("rh", "Ressources Humaines"),
        ("finance", "Finance & Audit"),
        ("marketing", "Marketing"),
        ("organisation", "Organisation"),
    ]

    name = models.CharField("Nom du service", max_length=200)
    category = models.CharField("Catégorie", max_length=50, choices=CATEGORY_CHOICES)
    base_price = models.DecimalField("Prix de base HT (CHF)", max_digits=10, decimal_places=2)
    duration_hours = models.IntegerField("Durée estimée (heures)")
    description = models.TextField("Description", blank=True)

    class Meta:
        db_table = "services"
        ordering = ["category", "name"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.name


class Appointment(models.Model):
    """Mission ou rendez-vous : un client réserve un service avec un consultant."""

    STATUS_CHOICES = [
        ("planifie", "Planifié"),
        ("realise", "Réalisé"),
        ("annule", "Annulé"),
    ]

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name="Client"
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, verbose_name="Consultant"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, verbose_name="Service"
    )
    date = models.DateField("Date de la mission")
    duration_hours = models.IntegerField("Durée réelle (heures)")
    status = models.CharField(
        "Statut", max_length=20, choices=STATUS_CHOICES, default="planifie"
    )
    notes = models.TextField("Notes", blank=True)

    class Meta:
        db_table = "appointments"
        ordering = ["-date"]
        verbose_name = "Mission"
        verbose_name_plural = "Missions"

    def __str__(self):
        return f"{self.service} - {self.client} ({self.date})"


class Invoice(models.Model):
    """Facture émise pour une mission réalisée."""

    STATUS_CHOICES = [
        ("emise", "Émise"),
        ("payee", "Payée"),
        ("en_retard", "En retard"),
    ]

    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, verbose_name="Mission"
    )
    invoice_number = models.CharField("N° facture", max_length=50, unique=True)
    amount_ht = models.DecimalField("Montant HT (CHF)", max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField("Taux TVA (%)", max_digits=5, decimal_places=2, default=20.00)
    amount_ttc = models.DecimalField("Montant TTC (CHF)", max_digits=10, decimal_places=2)
    issued_date = models.DateField("Date d'émission")
    due_date = models.DateField("Date d'échéance")
    status = models.CharField(
        "Statut", max_length=20, choices=STATUS_CHOICES, default="emise"
    )

    class Meta:
        db_table = "invoices"
        ordering = ["-issued_date"]
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

    def __str__(self):
        return self.invoice_number


class Payment(models.Model):
    """Paiement reçu pour une facture."""

    METHOD_CHOICES = [
        ("virement", "Virement bancaire"),
        ("carte", "Carte bancaire"),
        ("cheque", "Chèque"),
    ]

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, verbose_name="Facture"
    )
    amount = models.DecimalField("Montant (CHF)", max_digits=10, decimal_places=2)
    payment_date = models.DateField("Date de paiement")
    method = models.CharField(
        "Mode de paiement", max_length=20, choices=METHOD_CHOICES
    )

    class Meta:
        db_table = "payments"
        ordering = ["-payment_date"]
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"

    def __str__(self):
        return f"Paiement {self.amount} CHF - {self.invoice}"
