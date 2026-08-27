"""
Commande Django — Données réalistes d'un cabinet d'audit suisse.

Génère :
  - 16 clients PME dans des secteurs variés
  - 8 auditeurs / consultants avec des profils réels
  - 10 services d'audit et de conseil
  - ~250 missions réparties sur 24 mois (saisonnalité réaliste)
  - Factures et paiements correspondants

Usage : python manage.py seed_data
"""

import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import Client, Employee, Service, Appointment, Invoice, Payment

# Seed fixe pour la reproductibilité
random.seed(42)


class Command(BaseCommand):
    help = "Génère des données réalistes pour un cabinet d'audit suisse"

    def handle(self, *args, **options):
        self.stdout.write("Nettoyage des données existantes...")
        Payment.objects.all().delete()
        Invoice.objects.all().delete()
        Appointment.objects.all().delete()
        Service.objects.all().delete()
        Employee.objects.all().delete()
        Client.objects.all().delete()

        self.stdout.write("Création des clients PME...")
        clients = self._create_clients()

        self.stdout.write("Création de l'équipe d'audit...")
        employees = self._create_employees()

        self.stdout.write("Création des services...")
        services = self._create_services()

        self.stdout.write("Création des missions (24 mois)...")
        appointments = self._create_appointments(clients, employees, services)

        self.stdout.write("Création des factures et paiements...")
        self._create_invoices_and_payments(appointments)

        self.stdout.write(
            self.style.SUCCESS("\n✓ Base de données réelle générée avec succès !")
        )
        self.stdout.write(f"  - {Client.objects.count()} clients")
        self.stdout.write(f"  - {Employee.objects.count()} auditeurs / consultants")
        self.stdout.write(f"  - {Service.objects.count()} services")
        self.stdout.write(f"  - {Appointment.objects.count()} missions")
        self.stdout.write(f"  - {Invoice.objects.count()} factures")
        self.stdout.write(f"  - {Payment.objects.count()} paiements")

    # ─── CLIENTS ──────────────────────────────────────────────────────────────

    def _create_clients(self):
        data = [
            # Finance
            {
                "company_name": "Banque Cantonale Vaudoise",
                "contact_name": "Alexandre Rochat",
                "email": "a.rochat@bcv-clients.ch",
                "phone": "+41 21 212 10 00",
                "address": "Place Saint-François 14",
                "city": "Lausanne",
                "sector": "finance",
            },
            {
                "company_name": "Helvetia Assurances SA",
                "contact_name": "Nathalie Zimmermann",
                "email": "n.zimmermann@helvetia-clients.ch",
                "phone": "+41 71 858 91 00",
                "address": "St-Alban-Anlage 26",
                "city": "Bâle",
                "sector": "finance",
            },
            {
                "company_name": "Groupe Mutuel Holding SA",
                "contact_name": "Pierre-André Favre",
                "email": "pa.favre@groupemutuel-clients.ch",
                "phone": "+41 58 758 71 11",
                "address": "Rue des Cèdres 5",
                "city": "Martigny",
                "sector": "finance",
            },
            # Tech
            {
                "company_name": "Kudelski SA",
                "contact_name": "Isabelle Bonnet",
                "email": "i.bonnet@kudelski-clients.ch",
                "phone": "+41 21 732 01 01",
                "address": "Route de Genève 22",
                "city": "Cheseaux-sur-Lausanne",
                "sector": "tech",
            },
            {
                "company_name": "Temenos AG",
                "contact_name": "Michael Schneider",
                "email": "m.schneider@temenos-clients.ch",
                "phone": "+41 22 708 11 50",
                "address": "2 Rue de l'Ecole-de-Chimie",
                "city": "Genève",
                "sector": "tech",
            },
            {
                "company_name": "SoftwarePlus Sàrl",
                "contact_name": "Laura Meier",
                "email": "l.meier@softwareplus.ch",
                "phone": "+41 31 550 44 00",
                "address": "Länggassstrasse 23",
                "city": "Berne",
                "sector": "tech",
            },
            # Santé
            {
                "company_name": "Hirslanden Clinique Bois-Cerf",
                "contact_name": "Dr. Marc Devaud",
                "email": "m.devaud@hirslanden-clients.ch",
                "phone": "+41 21 619 81 11",
                "address": "Avenue d'Ouchy 31",
                "city": "Lausanne",
                "sector": "sante",
            },
            {
                "company_name": "Pharmacies Populaires SA",
                "contact_name": "Claire Vaucher",
                "email": "c.vaucher@pharmapop-clients.ch",
                "phone": "+41 26 347 22 22",
                "address": "Boulevard de Pérolles 12",
                "city": "Fribourg",
                "sector": "sante",
            },
            # Industrie
            {
                "company_name": "Bobst Group SA",
                "contact_name": "Jean-Pascal Bobst",
                "email": "jp.bobst@bobst-clients.ch",
                "phone": "+41 21 621 21 11",
                "address": "Route de Faraz 2",
                "city": "Mex",
                "sector": "industrie",
            },
            {
                "company_name": "Romande Energie SA",
                "contact_name": "Sophie Mermoud",
                "email": "s.mermoud@romande-energie-clients.ch",
                "phone": "+41 21 802 92 00",
                "address": "Chemin de Mornex 10",
                "city": "Morges",
                "sector": "industrie",
            },
            {
                "company_name": "Chocolats Camille Bloch SA",
                "contact_name": "Philippe Bloch",
                "email": "p.bloch@camillebloch-clients.ch",
                "phone": "+41 32 358 58 58",
                "address": "Rue de la Chocolatière 1",
                "city": "Courtelary",
                "sector": "industrie",
            },
            # Commerce
            {
                "company_name": "Interdiscount SA",
                "contact_name": "Reto Müller",
                "email": "r.mueller@interdiscount-clients.ch",
                "phone": "+41 31 960 11 11",
                "address": "Bernstrasse 1",
                "city": "Jegenstorf",
                "sector": "commerce",
            },
            {
                "company_name": "Landi Romandie SA",
                "contact_name": "Antoine Gerber",
                "email": "a.gerber@landi-clients.ch",
                "phone": "+41 21 613 34 34",
                "address": "Route de Cossonay 4",
                "city": "Bussigny",
                "sector": "commerce",
            },
            # Éducation
            {
                "company_name": "École Hôtelière de Lausanne",
                "contact_name": "Dominique Morin",
                "email": "d.morin@ehl-clients.ch",
                "phone": "+41 21 785 11 11",
                "address": "Route de Cojonnex 18",
                "city": "Lausanne",
                "sector": "education",
            },
            {
                "company_name": "EPFL Innovation Park SA",
                "contact_name": "Fabienne Leclerc",
                "email": "f.leclerc@epfl-ip-clients.ch",
                "phone": "+41 21 693 72 00",
                "address": "Route J-D Colladon 1",
                "city": "Lausanne",
                "sector": "education",
            },
            {
                "company_name": "Institut Le Rosey",
                "contact_name": "Charles Bédert",
                "email": "c.bedert@rosey-clients.ch",
                "phone": "+41 21 822 55 00",
                "address": "Grand-Rue 5",
                "city": "Rolle",
                "sector": "education",
            },
        ]
        return [Client.objects.create(**item) for item in data]

    # ─── EMPLOYÉS ─────────────────────────────────────────────────────────────

    def _create_employees(self):
        data = [
            {
                "first_name": "Étienne",
                "last_name": "Dufour",
                "email": "e.dufour@cabinet-audit.ch",
                "role": "manager",
                "hire_date": date(2016, 9, 1),
                "hourly_rate": Decimal("220.00"),
                "is_active": True,
            },
            {
                "first_name": "Caroline",
                "last_name": "Wenger",
                "email": "c.wenger@cabinet-audit.ch",
                "role": "manager",
                "hire_date": date(2018, 3, 15),
                "hourly_rate": Decimal("200.00"),
                "is_active": True,
            },
            {
                "first_name": "Maxime",
                "last_name": "Aubry",
                "email": "m.aubry@cabinet-audit.ch",
                "role": "senior",
                "hire_date": date(2019, 8, 1),
                "hourly_rate": Decimal("165.00"),
                "is_active": True,
            },
            {
                "first_name": "Lucie",
                "last_name": "Fontaine",
                "email": "l.fontaine@cabinet-audit.ch",
                "role": "senior",
                "hire_date": date(2020, 2, 1),
                "hourly_rate": Decimal("155.00"),
                "is_active": True,
            },
            {
                "first_name": "Thomas",
                "last_name": "Rieder",
                "email": "t.rieder@cabinet-audit.ch",
                "role": "senior",
                "hire_date": date(2020, 9, 1),
                "hourly_rate": Decimal("150.00"),
                "is_active": True,
            },
            {
                "first_name": "Amélie",
                "last_name": "Bourgeois",
                "email": "a.bourgeois@cabinet-audit.ch",
                "role": "consultant",
                "hire_date": date(2022, 1, 10),
                "hourly_rate": Decimal("120.00"),
                "is_active": True,
            },
            {
                "first_name": "Nathan",
                "last_name": "Chevalier",
                "email": "n.chevalier@cabinet-audit.ch",
                "role": "consultant",
                "hire_date": date(2022, 9, 1),
                "hourly_rate": Decimal("115.00"),
                "is_active": True,
            },
            {
                "first_name": "Sara",
                "last_name": "Porchet",
                "email": "s.porchet@cabinet-audit.ch",
                "role": "consultant",
                "hire_date": date(2023, 3, 1),
                "hourly_rate": Decimal("110.00"),
                "is_active": True,
            },
        ]
        return [Employee.objects.create(**item) for item in data]

    # ─── SERVICES ─────────────────────────────────────────────────────────────

    def _create_services(self):
        data = [
            # Audit légal — missions longues et récurrentes
            {
                "name": "Audit légal des comptes annuels",
                "category": "finance",
                "base_price": Decimal("18000.00"),
                "duration_hours": 120,
                "description": "Commissariat aux comptes — révision des états financiers annuels "
                "selon CO et Swiss GAAP RPC.",
            },
            {
                "name": "Révision restreinte",
                "category": "finance",
                "base_price": Decimal("6500.00"),
                "duration_hours": 40,
                "description": "Révision restreinte pour PME selon art. 727a CO.",
            },
            # Audit interne
            {
                "name": "Audit interne — processus financiers",
                "category": "finance",
                "base_price": Decimal("9500.00"),
                "duration_hours": 60,
                "description": "Évaluation indépendante des contrôles internes financiers.",
            },
            {
                "name": "Audit interne — systèmes d'information",
                "category": "it",
                "base_price": Decimal("11000.00"),
                "duration_hours": 70,
                "description": "Audit des systèmes IT : sécurité, continuité, contrôles applicatifs.",
            },
            # Due diligence
            {
                "name": "Due diligence financière",
                "category": "finance",
                "base_price": Decimal("22000.00"),
                "duration_hours": 140,
                "description": "Analyse approfondie pré-acquisition : passifs cachés, "
                "qualité des actifs, normalisation du résultat.",
            },
            # Consolidation
            {
                "name": "Assistance à la consolidation des comptes",
                "category": "finance",
                "base_price": Decimal("13500.00"),
                "duration_hours": 85,
                "description": "Élaboration ou revue des comptes consolidés selon IFRS ou Swiss GAAP.",
            },
            # Conseil fiscal
            {
                "name": "Conseil fiscal et optimisation",
                "category": "finance",
                "base_price": Decimal("7000.00"),
                "duration_hours": 45,
                "description": "Structuration fiscale, TVA, impôt anticipé, optimisation de la charge.",
            },
            # Gestion des risques
            {
                "name": "Cartographie et gestion des risques",
                "category": "strategie",
                "base_price": Decimal("8500.00"),
                "duration_hours": 55,
                "description": "Identification, évaluation et plan de traitement des risques métier.",
            },
            # Compliance
            {
                "name": "Conformité réglementaire (LBA / FINMA)",
                "category": "finance",
                "base_price": Decimal("10000.00"),
                "duration_hours": 65,
                "description": "Revue conformité LBA, directives FINMA, politique KYC/AML.",
            },
            # Organisation
            {
                "name": "Optimisation des processus comptables",
                "category": "organisation",
                "base_price": Decimal("5500.00"),
                "duration_hours": 35,
                "description": "Diagnostic et amélioration de la clôture mensuelle, "
                "automatisation des rapprochements.",
            },
        ]
        return [Service.objects.create(**item) for item in data]

    # ─── MISSIONS ─────────────────────────────────────────────────────────────

    def _create_appointments(self, clients, employees, services):
        """
        Génère ~250 missions sur 24 mois avec une saisonnalité réaliste :
        - Q1 (jan-mars) : pic fort — clôtures annuelles, audits légaux
        - Q2 (avr-juin) : activité soutenue
        - Q3 (juil-sep) : creux estival
        - Q4 (oct-déc)  : pic modéré — préparations de fin d'année

        Les managers sont associés aux grosses missions (due diligence, audit légal).
        Les seniors et consultants aux missions plus courtes.
        """
        appointments = []
        today = date.today()
        start = today.replace(day=1) - timedelta(days=730)  # ~24 mois en arrière

        # Services "lourds" réservés aux managers/seniors
        heavy_services = [s for s in services if s.duration_hours >= 60]
        light_services = [s for s in services if s.duration_hours < 60]

        managers = [e for e in employees if e.role == "manager"]
        seniors = [e for e in employees if e.role == "senior"]
        juniors = [e for e in employees if e.role == "consultant"]

        # Saisonnalité : nb de missions par mois (index 0 = janvier)
        seasonality = [9, 8, 7, 5, 5, 4, 2, 3, 4, 5, 6, 8]

        for month_offset in range(24):
            # Calcul du mois courant
            year_offset = month_offset // 12
            month_index = month_offset % 12
            year = (
                start.year + year_offset + (1 if start.month + month_index > 12 else 0)
            )
            month = (start.month + month_index - 1) % 12 + 1

            nb_missions = seasonality[month_index] + random.randint(-1, 2)
            nb_missions = max(1, nb_missions)

            for _ in range(nb_missions):
                # Date dans le mois — jour borné à 28, valide pour tous les mois
                mission_date = date(year, month, random.randint(1, 28))

                if mission_date > today:
                    mission_date = today - timedelta(days=random.randint(1, 10))

                # Choisir le service et l'assigné selon la complexité
                if random.random() < 0.35:
                    service = random.choice(heavy_services)
                    employee = random.choice(managers + seniors)
                else:
                    service = random.choice(light_services)
                    employee = random.choice(seniors + juniors)

                # Variation de durée réaliste (+/- 25%)
                variation = random.uniform(0.75, 1.25)
                duration = max(4, int(service.duration_hours * variation))

                # Statut selon l'ancienneté de la mission
                days_ago = (today - mission_date).days
                if days_ago > 45:
                    status = random.choices(
                        ["realise", "realise", "realise", "annule"],
                        weights=[88, 5, 5, 2],
                    )[0]
                elif days_ago > 14:
                    status = random.choices(
                        ["realise", "planifie", "annule"],
                        weights=[70, 25, 5],
                    )[0]
                else:
                    status = random.choice(["planifie", "planifie", "realise"])

                # Affecter un client — les gros clients ont plus de missions
                weights = [
                    3 if c.sector in ("finance", "industrie") else 1 for c in clients
                ]
                client = random.choices(clients, weights=weights)[0]

                appointment = Appointment.objects.create(
                    client=client,
                    employee=employee,
                    service=service,
                    date=mission_date,
                    duration_hours=duration,
                    status=status,
                    notes="",
                )
                appointments.append(appointment)

        return appointments

    # ─── FACTURES ET PAIEMENTS ────────────────────────────────────────────────

    def _create_invoices_and_payments(self, appointments):
        """
        Crée une facture pour chaque mission réalisée.
        Taux de recouvrement réaliste : 90% payées, 10% en retard.
        """
        invoice_counter = 1
        today = date.today()
        tax_rate = Decimal("8.10")  # TVA suisse actuelle

        for appointment in appointments:
            if appointment.status != "realise":
                continue

            # Montant basé sur le taux horaire du consultant
            amount_ht = appointment.employee.hourly_rate * appointment.duration_hours
            amount_ttc = amount_ht * (1 + tax_rate / 100)

            # Facturation émise 3-7 jours après la mission
            issued_date = appointment.date + timedelta(days=random.randint(3, 7))
            due_date = issued_date + timedelta(days=30)

            # Statut de la facture
            if due_date < today:
                status = random.choices(
                    ["payee", "en_retard"],
                    weights=[90, 10],
                )[0]
            else:
                status = "emise"

            # Année de la facture pour le numéro
            inv_year = issued_date.year
            invoice = Invoice.objects.create(
                appointment=appointment,
                invoice_number=f"AUD-{inv_year}-{invoice_counter:04d}",
                amount_ht=amount_ht.quantize(Decimal("0.01")),
                tax_rate=tax_rate,
                amount_ttc=amount_ttc.quantize(Decimal("0.01")),
                issued_date=issued_date,
                due_date=due_date,
                status=status,
            )
            invoice_counter += 1

            # Paiement pour les factures soldées
            if status == "payee":
                Payment.objects.create(
                    invoice=invoice,
                    amount=amount_ttc.quantize(Decimal("0.01")),
                    payment_date=issued_date + timedelta(days=random.randint(5, 28)),
                    method=random.choices(
                        ["virement", "carte", "cheque"],
                        weights=[80, 15, 5],
                    )[0],
                )
