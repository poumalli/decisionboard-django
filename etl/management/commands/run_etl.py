"""
Pipeline ETL — Extraction, Transformation, Chargement.

Transfère les données de la base OLTP vers le Data Warehouse.
Utilise uniquement l'ORM Django (pas de Pandas, pas de SQL brut).

Usage : python manage.py run_etl
"""

import logging
from datetime import date, datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Client, Employee, Service, Appointment, Invoice
from dw.models import DimDate, DimClient, DimEmployee, DimService, FactSales

logger = logging.getLogger(__name__)

# Noms des mois en français
MONTH_NAMES = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre",
}


class Command(BaseCommand):
    help = "Exécute le pipeline ETL : OLTP → Data Warehouse"

    def handle(self, *args, **options):
        self.stdout.write("=" * 50)
        self.stdout.write("Démarrage du pipeline ETL")
        self.stdout.write("=" * 50)

        # Étape 1 : Chargement des dimensions
        self.stdout.write("\n--- Chargement des dimensions ---")
        self.load_dim_date()
        self.load_dim_client()
        self.load_dim_employee()
        self.load_dim_service()

        # Étape 2 : Chargement de la table de faits
        self.stdout.write("\n--- Chargement de la table de faits ---")
        self.load_fact_sales()

        # Enregistrer l'horodatage de la dernière exécution
        self._save_timestamp()

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("ETL terminé avec succès !"))

    def _save_timestamp(self):
        """Sauvegarde la date/heure de fin ETL dans .etl_last_run."""
        filepath = settings.BASE_DIR / ".etl_last_run"
        filepath.write_text(datetime.now().strftime("%d/%m/%Y à %H:%M"))

    # ----- DIMENSIONS -----

    def load_dim_date(self):
        """
        Génère la dimension date pour les 2 dernières années.
        Chaque jour est une ligne avec année, mois, trimestre, etc.
        """
        today = date.today()
        start = today - timedelta(days=730)  # ~2 ans en arrière
        end = today + timedelta(days=90)     # 3 mois dans le futur

        # Récupérer les dates déjà existantes pour éviter les doublons
        existing = set(
            DimDate.objects.using("dw").values_list("full_date", flat=True)
        )

        new_dates = []
        current = start
        while current <= end:
            if current not in existing:
                new_dates.append(DimDate(
                    full_date=current,
                    year=current.year,
                    quarter=(current.month - 1) // 3 + 1,
                    month=current.month,
                    month_name=MONTH_NAMES[current.month],
                    day=current.day,
                    day_of_week=current.weekday() + 1,  # 1=Lundi, 7=Dimanche
                    is_weekend=current.weekday() >= 5,
                ))
            current += timedelta(days=1)

        if new_dates:
            DimDate.objects.using("dw").bulk_create(new_dates)

        self.stdout.write(f"  DimDate : {len(new_dates)} nouvelles dates ajoutées")

    def load_dim_client(self):
        """
        Extraction : lit les clients depuis l'OLTP.
        Transformation : sélectionne les champs utiles à l'analyse.
        Chargement : update_or_create dans le DW.
        """
        clients = Client.objects.all()
        count = 0

        for client in clients:
            DimClient.objects.using("dw").update_or_create(
                source_id=client.id,
                defaults={
                    "company_name": client.company_name,
                    "sector": client.sector,
                    "city": client.city,
                },
            )
            count += 1

        self.stdout.write(f"  DimClient : {count} clients chargés")

    def load_dim_employee(self):
        """
        Extraction : lit les employés depuis l'OLTP.
        Transformation : calcule le nom complet et l'ancienneté.
        Chargement : update_or_create dans le DW.
        """
        employees = Employee.objects.filter(is_active=True)
        count = 0
        today = date.today()

        for emp in employees:
            # Transformation : calcul de l'ancienneté en années
            seniority = (today - emp.hire_date).days // 365

            DimEmployee.objects.using("dw").update_or_create(
                source_id=emp.id,
                defaults={
                    "full_name": f"{emp.first_name} {emp.last_name}",
                    "role": emp.role,
                    "hire_date": emp.hire_date,
                    "seniority_years": seniority,
                },
            )
            count += 1

        self.stdout.write(f"  DimEmployee : {count} employés chargés")

    def load_dim_service(self):
        """
        Extraction : lit les services depuis l'OLTP.
        Chargement : update_or_create dans le DW (pas de transformation).
        """
        services = Service.objects.all()
        count = 0

        for svc in services:
            DimService.objects.using("dw").update_or_create(
                source_id=svc.id,
                defaults={
                    "name": svc.name,
                    "category": svc.category,
                    "base_price": svc.base_price,
                    "duration_hours": svc.duration_hours,
                },
            )
            count += 1

        self.stdout.write(f"  DimService : {count} services chargés")

    # ----- TABLE DE FAITS -----

    def load_fact_sales(self):
        """
        Extraction : lit les missions réalisées + leur facture depuis l'OLTP.
        Transformation : joint les données mission/facture, résout les FK du DW.
        Chargement : crée les faits dans le DW.
        """
        # Pré-charger les mappings OLTP ID -> DW ID pour les dimensions
        date_map = dict(
            DimDate.objects.using("dw").values_list("full_date", "id")
        )
        client_map = dict(
            DimClient.objects.using("dw").values_list("source_id", "id")
        )
        employee_map = dict(
            DimEmployee.objects.using("dw").values_list("source_id", "id")
        )
        service_map = dict(
            DimService.objects.using("dw").values_list("source_id", "id")
        )

        # Extraction : missions réalisées avec leur facture
        appointments = (
            Appointment.objects
            .filter(status="realise")
            .select_related("client", "employee", "service", "invoice")
        )

        # IDs déjà chargés (pour éviter les doublons)
        existing_ids = set(
            FactSales.objects.using("dw").values_list(
                "source_appointment_id", flat=True
            )
        )

        new_facts = []
        skipped = 0

        for apt in appointments:
            # Ignorer si déjà chargé
            if apt.id in existing_ids:
                skipped += 1
                continue

            # Vérifier que la facture existe
            try:
                invoice = apt.invoice
            except Appointment.invoice.RelatedObjectDoesNotExist:
                skipped += 1
                continue

            # Résoudre les clés étrangères du DW
            dim_date_id = date_map.get(apt.date)
            dim_client_id = client_map.get(apt.client_id)
            dim_employee_id = employee_map.get(apt.employee_id)
            dim_service_id = service_map.get(apt.service_id)

            # Si une dimension manque, on saute cette ligne
            if not all([dim_date_id, dim_client_id, dim_employee_id, dim_service_id]):
                skipped += 1
                continue

            new_facts.append(FactSales(
                date_id=dim_date_id,
                client_id=dim_client_id,
                employee_id=dim_employee_id,
                service_id=dim_service_id,
                source_appointment_id=apt.id,
                duration_hours=apt.duration_hours,
                unit_price=apt.employee.hourly_rate,
                total_ht=invoice.amount_ht,
                total_ttc=invoice.amount_ttc,
                is_paid=(invoice.status == "payee"),
            ))

        if new_facts:
            FactSales.objects.using("dw").bulk_create(new_facts)

        self.stdout.write(
            f"  FactSales : {len(new_facts)} faits créés, {skipped} ignorés"
        )
