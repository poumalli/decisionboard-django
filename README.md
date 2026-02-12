# DecisionBoard

Plateforme décisionnelle pour un cabinet de consulting.
Transforme les données opérationnelles (clients, missions, consultants, facturation) en indicateurs de pilotage via un tableau de bord web.

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

## Dashboard (4 pages)

### Tableau de bord (vue d'ensemble)
- 4 cartes KPI : CA, panier moyen, clients actifs, taux d'occupation
- Graphique : évolution du CA mensuel
- Graphique : top 5 services par CA
- Tableau : performance des consultants

### Analyse des revenus
- CA par mois (graphique barres)
- CA par catégorie de service (doughnut)
- Détail par service et par client (tableaux)

### Performance consultants
- CA et heures par consultant (graphique barres)
- Taux d'occupation individuel (jauges visuelles)
- Tableau détaillé : missions, heures, moyenne

### Analyse clients
- Répartition du CA par secteur (doughnut)
- Classement des clients par CA
- Fréquence des missions (barres de progression)
- Clients inactifs (alerte)

## Installation

### Prérequis

- Python 3.10+
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

# 6. Créer un utilisateur admin
python manage.py createsuperuser

# 7. Charger les données de démo
python manage.py seed_data

# 8. Exécuter le pipeline ETL
python manage.py run_etl

# 9. Lancer le serveur
python manage.py runserver
```

Accéder au dashboard : http://localhost:8000

## Structure du projet

```
decisionboard-django/
├── config/                  # Configuration Django
│   ├── settings.py          # Paramètres (DB, sécurité, i18n)
│   ├── urls.py              # Routes principales
│   └── db_router.py         # Routeur OLTP / DW
├── core/                    # Application OLTP
│   ├── models.py            # 6 modèles (Client, Employee, Service...)
│   ├── admin.py             # Interface d'administration
│   └── management/commands/
│       └── seed_data.py     # Données de démonstration
├── dw/                      # Data Warehouse
│   └── models.py            # 4 dimensions + 1 table de faits
├── etl/                     # Pipeline ETL
│   └── management/commands/
│       └── run_etl.py       # Commande ETL (OLTP → DW)
├── dashboard/               # Application Dashboard
│   ├── views.py             # Vues (4 pages + export CSV)
│   ├── services.py          # Calcul des KPIs
│   └── urls.py              # Routes du dashboard
├── templates/               # Templates HTML
│   ├── base.html            # Layout commun
│   ├── login.html           # Page de connexion
│   └── dashboard/
│       ├── base_dashboard.html  # Layout avec sidebar
│       ├── home.html            # Tableau de bord
│       ├── revenue.html         # Analyse des revenus
│       ├── consultants.html     # Performance consultants
│       └── clients.html         # Analyse clients
├── static/
│   ├── css/style.css        # Styles
│   └── js/charts.js         # Graphiques Chart.js
├── .env.example             # Variables d'environnement (template)
├── requirements.txt         # Dépendances Python
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

- Authentification obligatoire (`@login_required`)
- Protection CSRF (Django)
- Variables sensibles dans `.env`
- ORM Django uniquement (pas de SQL brut)

## Technologies

- **Backend** : Django 4.2
- **Base de données** : PostgreSQL / SQLite
- **Graphiques** : Chart.js 4
- **CSS** : CSS custom (pas de framework)
- **Serveur statique** : WhiteNoise

## Licence

Projet académique — Travail de diplôme.
