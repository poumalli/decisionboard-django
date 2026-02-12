"""
Commande Django pour générer des données de démonstration réalistes.

Crée : 5 clients, 4 consultants, 6 services, ~50 missions sur 12 mois,
avec les factures et paiements correspondants.

Usage : python manage.py seed_data
"""

import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import Client, Employee, Service, Appointment, Invoice, Payment


class Command(BaseCommand):
    help = "Génère des données de démonstration pour le cabinet de consulting"

    def handle(self, *args, **options):
        self.stdout.write("Nettoyage des données existantes...")
        Payment.objects.all().delete()
        Invoice.objects.all().delete()
        Appointment.objects.all().delete()
        Service.objects.all().delete()
        Employee.objects.all().delete()
        Client.objects.all().delete()

        self.stdout.write("Création des clients...")
        clients = self._create_clients()

        self.stdout.write("Création des employés...")
        employees = self._create_employees()

        self.stdout.write("Création des services...")
        services = self._create_services()

        self.stdout.write("Création des missions...")
        appointments = self._create_appointments(clients, employees, services)

        self.stdout.write("Création des factures et paiements...")
        self._create_invoices_and_payments(appointments)

        self.stdout.write(self.style.SUCCESS("Données de démo créées avec succès !"))
        self.stdout.write(f"  - {Client.objects.count()} clients")
        self.stdout.write(f"  - {Employee.objects.count()} employés")
        self.stdout.write(f"  - {Service.objects.count()} services")
        self.stdout.write(f"  - {Appointment.objects.count()} missions")
        self.stdout.write(f"  - {Invoice.objects.count()} factures")
        self.stdout.write(f"  - {Payment.objects.count()} paiements")

    def _create_clients(self):
        """Crée 5 entreprises clientes dans différents secteurs."""
        data = [
            {
                "company_name": "TechNova SA",
                "contact_name": "Marie Dupont",
                "email": "m.dupont@technova.ch",
                "phone": "+41 21 345 67 89",
                "address": "Rue du Lac 15",
                "city": "Lausanne",
                "sector": "tech",
            },
            {
                "company_name": "Banque Léman",
                "contact_name": "Pierre Martin",
                "email": "p.martin@banqueleman.ch",
                "phone": "+41 22 456 78 90",
                "address": "Avenue de la Gare 8",
                "city": "Genève",
                "sector": "finance",
            },
            {
                "company_name": "Clinique du Parc",
                "contact_name": "Sophie Bernard",
                "email": "s.bernard@cliniqueparc.ch",
                "phone": "+41 26 567 89 01",
                "address": "Route de Berne 22",
                "city": "Fribourg",
                "sector": "sante",
            },
            {
                "company_name": "MétalPro Industries",
                "contact_name": "Jean Rochat",
                "email": "j.rochat@metalpro.ch",
                "phone": "+41 24 678 90 12",
                "address": "Zone Industrielle 5",
                "city": "Yverdon",
                "sector": "industrie",
            },
            {
                "company_name": "École Horizon",
                "contact_name": "Claire Favre",
                "email": "c.favre@ecolehorizon.ch",
                "phone": "+41 21 789 01 23",
                "address": "Chemin des Écoliers 3",
                "city": "Nyon",
                "sector": "education",
            },
        ]
        return [Client.objects.create(**item) for item in data]

    def _create_employees(self):
        """Crée 4 consultants avec des profils variés."""
        data = [
            {
                "first_name": "Lucas",
                "last_name": "Müller",
                "email": "l.muller@decisionboard.ch",
                "role": "manager",
                "hire_date": date(2020, 3, 1),
                "hourly_rate": Decimal("180.00"),
            },
            {
                "first_name": "Emma",
                "last_name": "Girard",
                "email": "e.girard@decisionboard.ch",
                "role": "senior",
                "hire_date": date(2021, 9, 15),
                "hourly_rate": Decimal("150.00"),
            },
            {
                "first_name": "Noah",
                "last_name": "Perret",
                "email": "n.perret@decisionboard.ch",
                "role": "consultant",
                "hire_date": date(2023, 1, 10),
                "hourly_rate": Decimal("120.00"),
            },
            {
                "first_name": "Léa",
                "last_name": "Bonvin",
                "email": "l.bonvin@decisionboard.ch",
                "role": "consultant",
                "hire_date": date(2023, 6, 1),
                "hourly_rate": Decimal("110.00"),
            },
        ]
        return [Employee.objects.create(**item) for item in data]

    def _create_services(self):
        """Crée 6 prestations de consulting dans différentes catégories."""
        data = [
            {
                "name": "Audit stratégique",
                "category": "strategie",
                "base_price": Decimal("5000.00"),
                "duration_hours": 40,
                "description": "Analyse complète de la stratégie d'entreprise.",
            },
            {
                "name": "Migration cloud",
                "category": "it",
                "base_price": Decimal("8000.00"),
                "duration_hours": 60,
                "description": "Accompagnement dans la migration vers le cloud.",
            },
            {
                "name": "Recrutement & talent",
                "category": "rh",
                "base_price": Decimal("3500.00"),
                "duration_hours": 25,
                "description": "Stratégie de recrutement et gestion des talents.",
            },
            {
                "name": "Audit financier",
                "category": "finance",
                "base_price": Decimal("6000.00"),
                "duration_hours": 45,
                "description": "Audit des processus financiers et recommandations.",
            },
            {
                "name": "Stratégie digitale",
                "category": "marketing",
                "base_price": Decimal("4500.00"),
                "duration_hours": 35,
                "description": "Élaboration d'une stratégie marketing digitale.",
            },
            {
                "name": "Optimisation des processus",
                "category": "organisation",
                "base_price": Decimal("4000.00"),
                "duration_hours": 30,
                "description": "Analyse et optimisation des processus internes.",
            },
        ]
        return [Service.objects.create(**item) for item in data]

    def _create_appointments(self, clients, employees, services):
        """
        Crée ~50 missions réparties sur les 12 derniers mois.
        Simule une activité réaliste avec une saisonnalité légère.
        """
        appointments = []
        today = date.today()
        start_date = today.replace(year=today.year - 1)

        # Générer des missions mois par mois
        for month_offset in range(12):
            # Plus de missions en début et fin d'année (saisonnalité)
            if month_offset in [0, 1, 9, 10, 11]:
                nb_missions = random.randint(4, 6)
            else:
                nb_missions = random.randint(3, 5)

            for _ in range(nb_missions):
                # Date aléatoire dans le mois
                mission_date = start_date + timedelta(
                    days=month_offset * 30 + random.randint(1, 28)
                )
                # Ne pas dépasser aujourd'hui
                if mission_date > today:
                    mission_date = today - timedelta(days=random.randint(1, 5))

                service = random.choice(services)
                # Variation réaliste de la durée (+/- 20%)
                variation = random.uniform(0.8, 1.2)
                duration = max(1, int(service.duration_hours * variation))

                # Les missions passées sont réalisées, les récentes peuvent être planifiées
                days_ago = (today - mission_date).days
                if days_ago > 30:
                    status = "realise"
                elif days_ago > 7:
                    status = random.choice(["realise", "realise", "annule"])
                else:
                    status = random.choice(["planifie", "realise"])

                appointment = Appointment.objects.create(
                    client=random.choice(clients),
                    employee=random.choice(employees),
                    service=service,
                    date=mission_date,
                    duration_hours=duration,
                    status=status,
                )
                appointments.append(appointment)

        return appointments

    def _create_invoices_and_payments(self, appointments):
        """
        Crée une facture pour chaque mission réalisée,
        et un paiement pour la plupart des factures.
        """
        invoice_counter = 1

        for appointment in appointments:
            # Seules les missions réalisées génèrent une facture
            if appointment.status != "realise":
                continue

            # Calcul du montant basé sur le taux horaire du consultant
            amount_ht = appointment.employee.hourly_rate * appointment.duration_hours
            tax_rate = Decimal("20.00")
            amount_ttc = amount_ht * (1 + tax_rate / 100)

            # Facture émise quelques jours après la mission
            issued_date = appointment.date + timedelta(days=random.randint(1, 5))
            due_date = issued_date + timedelta(days=30)

            # Déterminer le statut de la facture
            today = date.today()
            if due_date < today:
                # Facture échue : payée ou en retard
                status = random.choices(
                    ["payee", "en_retard"],
                    weights=[85, 15],  # 85% payées à temps
                )[0]
            else:
                status = "emise"

            invoice = Invoice.objects.create(
                appointment=appointment,
                invoice_number=f"FAC-{today.year}-{invoice_counter:04d}",
                amount_ht=amount_ht,
                tax_rate=tax_rate,
                amount_ttc=amount_ttc,
                issued_date=issued_date,
                due_date=due_date,
                status=status,
            )
            invoice_counter += 1

            # Créer un paiement pour les factures payées
            if status == "payee":
                payment_delay = random.randint(5, 30)
                Payment.objects.create(
                    invoice=invoice,
                    amount=amount_ttc,
                    payment_date=issued_date + timedelta(days=payment_delay),
                    method=random.choice(["virement", "carte", "cheque"]),
                )
