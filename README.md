# DecisionBoard

Plateforme décisionnelle pour un cabinet de consulting.
Transforme les données opérationnelles (clients, missions, consultants, facturation) en indicateurs de pilotage via un tableau de bord web, avec gestion complète des données et pipeline ETL pilotable depuis l'interface.

## Architecture

```
Base OLTP (PostgreSQL)  →  ETL (Django ORM)  →  Data Warehouse  →  Dashboard Web
```

| Couche | Description | Technologie |
|--------|-------------|-------------|
| **OLTP** | Base opérationnelle (6 tables) | PostgreSQL / SQLite |
| **ETL** | Pipeline d'alimentation du DW | Django Management Command |
| **DW** | Schéma en étoile (4 dims + 1 fait) | PostgreSQL / SQLite |
| **Dashboard** | Interface web avec KPIs | Django + Chart.js |

## Fonctionnalités

### Dashboard (5 pages)

**Tableau de bord** (vue d'ensemble)
- 6 cartes KPI : CA, missions, panier moyen, clients actifs, taux d'occupation, créances en cours
- Suivi des objectifs stratégiques (progression vs cible, alertes)
- Graphique : évolution du CA mensuel · Top 5 services par CA
- Tableau : performance des consultants

**Analyse des revenus** — CA par mois et par catégorie de service, détail par service et par client, filtre par catégorie

**Performance consultants** — CA et heures par consultant, taux d'occupation individuel (jauges), tableau détaillé

**Analyse clients** — répartition du CA par secteur, classement des clients, fréquence des missions, alerte clients inactifs

**Paramètres stratégiques** — configuration des objectifs (CA mensuel, taux d'occupation, panier moyen) et seuils d'alerte (inactivité client, créances)

Filtres communs à toutes les pages : raccourcis de période (mois/trimestre/année), plage de dates personnalisée, export CSV au choix (performance consultants, revenus mensuels ou classement clients).

### Gestion des données (CRUD)

Interface complète pour créer, modifier et supprimer les 6 entités OLTP — clients, consultants, services, missions, factures, paiements — sans passer par l'admin Django. Fiches détail avec historique des missions pour les clients et les consultants. Réservée au groupe **Administrateur**.

### Pipeline ETL

Déclenchable en un clic depuis la sidebar (bouton "Lancer l'ETL", avec horodatage de la dernière exécution) ou en ligne de commande :

```bash
python manage.py run_etl
```

## Contrôle d'accès

Deux groupes Django, créés automatiquement après chaque migration (et via `setup_groups`) :

| Groupe | Accès |
|--------|-------|
| **Administrateur** | Dashboard + Gestion des données (CRUD) + ETL |
| **Consultant** | Dashboard en lecture seule |

## Installation

### Prérequis

- Python 3.11+
- PostgreSQL 13+ (optionnel, SQLite par défaut)

### Mise en place

```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/decisionboard-django.git
cd decisionboard-django

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env
# Modifier .env avec vos paramètres de base de données

# 5. Appliquer les migrations
python manage.py migrate
python manage.py migrate --database=dw

# 6. Créer les groupes d'accès (Administrateur / Consultant)
python manage.py setup_groups

# 7. Créer un utilisateur admin et l'ajouter au groupe Administrateur
python manage.py createsuperuser

# 8. Charger les données de démo
python manage.py seed_data

# 9. Exécuter le pipeline ETL
python manage.py run_etl

# 10. Lancer le serveur
python manage.py runserver
```

Accéder au dashboard : http://localhost:8000

En production, définir `DJANGO_ENV=production` (voir `config/settings_prod.py` pour les variables requises : `SECRET_KEY`, `DATABASE_URL`, `DW_DATABASE_URL`, `ALLOWED_HOSTS`).

## Structure du projet

```
decisionboard-django/
├── config/                       # Configuration Django
│   ├── settings.py               # Dispatcher (DJANGO_ENV → dev/prod)
│   ├── settings_base.py          # Réglages communs
│   ├── settings_dev.py           # Développement (DEBUG=True)
│   ├── settings_prod.py          # Production (sécurité renforcée)
│   ├── urls.py                   # Routes principales
│   └── db_router.py              # Routeur OLTP / DW
├── core/                         # Application OLTP
│   ├── models.py                 # 6 modèles (Client, Employee, Service...)
│   ├── forms.py                  # ModelForms du CRUD
│   ├── views.py                  # CRUD (list/create/update/delete/detail)
│   ├── urls.py                   # Routes /data/...
│   ├── permissions.py            # Décorateurs admin_required / consultant_required
│   ├── context_processors.py     # user_is_admin, etl_last_run (globaux)
│   ├── admin.py                  # Interface d'administration Django
│   └── management/commands/
│       ├── seed_data.py          # Données de démonstration
│       └── setup_groups.py       # Création des groupes d'accès
├── dw/                            # Data Warehouse
│   └── models.py                 # 4 dimensions + 1 table de faits
├── etl/                           # Pipeline ETL
│   ├── views.py                  # Déclenchement depuis l'UI
│   ├── urls.py
│   └── management/commands/
│       └── run_etl.py            # Commande ETL (OLTP → DW)
├── dashboard/                     # Application Dashboard
│   ├── views.py                  # 5 pages + export CSV
│   ├── forms.py                  # BusinessSettingsForm
│   ├── services/                 # Logique métier (KPIs)
│   │   ├── kpi.py
│   │   └── business_metrics.py
│   └── urls.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── errors/                   # 404 / 500 personnalisées
│   ├── dashboard/                 # 5 pages du dashboard
│   └── core/                      # Gestion des données (11 templates)
├── static/
│   ├── css/style.css
│   └── js/charts.js
├── tests/                         # Suite pytest (miroir de la structure ci-dessus)
├── .env.example
├── requirements.txt
└── manage.py
```

## Modèle de données

### OLTP (6 tables)

```
Client ──< Appointment >── Employee
               │
             Service
               │
            Invoice ──< Payment
```

### Data Warehouse (schéma en étoile)

```
dim_date ──┐
dim_client ─┤
dim_employee┼── fact_sales
dim_service─┘
```

## Sécurité

- Authentification obligatoire, contrôle d'accès par groupe (`admin_required` / `consultant_required`)
- Protection CSRF (Django), redirection `next` validée (anti-open-redirect)
- Variables sensibles dans `.env` (jamais commité)
- ORM Django uniquement (pas de SQL brut)
- Settings production : cookies sécurisés, `SECRET_KEY` par défaut refusée au démarrage, fichiers statiques avec manifest

## Tests

Développement en TDD strict (Red → Green → Refactor). 170 tests, **99% de couverture**.

```bash
python -m pytest                                      # tous les tests
python -m pytest --cov=. --cov-report=term-missing    # avec couverture
python -m flake8 .                                     # linter
python -m mypy .                                        # typage
```

## Technologies

- **Backend** : Django 4.2
- **Base de données** : PostgreSQL / SQLite
- **Graphiques** : Chart.js 4
- **CSS** : CSS custom (pas de framework)
- **Serveur statique** : WhiteNoise
- **Tests** : pytest, pytest-django, pytest-cov
- **Qualité** : flake8, black, mypy (django-stubs)

## Licence

Projet académique — Travail de diplôme.
