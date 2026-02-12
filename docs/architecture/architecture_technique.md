# Architecture Technique — DecisionBoard

## Vue d'ensemble

Plateforme décisionnelle pour un cabinet de consulting suisse.
Transforme les données opérationnelles (clients, missions, consultants, facturation) en indicateurs de pilotage via un dashboard web.

## Architecture globale

```
Base OLTP (PostgreSQL/SQLite)  →  ETL (Django ORM)  →  Data Warehouse  →  Dashboard Web
```

| Couche | Rôle | Technologie |
|--------|------|-------------|
| **OLTP** | Base opérationnelle (6 tables) | PostgreSQL / SQLite |
| **ETL** | Pipeline d'alimentation du DW | Django Management Command |
| **DW** | Schéma en étoile (4 dims + 1 fait) | PostgreSQL / SQLite |
| **Dashboard** | Interface web avec KPIs | Django + Chart.js |

## Stack technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Django | 4.2 |
| Base de données | PostgreSQL / SQLite | 13+ |
| Graphiques | Chart.js | 4.4 |
| Serveur statique | WhiteNoise | 6.6 |
| CSS | Custom (pas de framework) | — |
| Authentification | Django Auth | intégré |

## Modèle de données

### OLTP — 6 tables (app `core`)

```
Client ──< Appointment >── Employee
               │
             Service
               │
            Invoice ──< Payment
```

| Table | Rôle |
|-------|------|
| `Client` | Entreprises clientes (secteur, ville, contact) |
| `Employee` | Consultants (rôle, taux horaire, ancienneté) |
| `Service` | Prestations (catégorie, prix, durée) |
| `Appointment` | Missions (client + consultant + service + date) |
| `Invoice` | Factures (montant HT/TTC, statut, échéance) |
| `Payment` | Paiements reçus (montant, mode, date) |

### Data Warehouse — schéma en étoile (app `dw`)

```
DimDate ────┐
DimClient ──┤
DimEmployee ┼── FactSales
DimService ─┘
```

| Dimension | Champs clés |
|-----------|-------------|
| `DimDate` | full_date, year, quarter, month, day_of_week |
| `DimClient` | company_name, sector, city |
| `DimEmployee` | full_name, role, seniority_years |
| `DimService` | name, category, base_price |

| Fait | Mesures |
|------|---------|
| `FactSales` | duration_hours, total_ht, total_ttc, is_paid |

**Indexes composites** sur FactSales : `(date, client)`, `(date, employee)`, `(date, service)`, `(is_paid)`.

## Pipeline ETL

Commande Django : `python manage.py run_etl`

```
1. Charger DimDate     (2 ans passés + 3 mois futur)
2. Charger DimClient   (depuis core.Client)
3. Charger DimEmployee (depuis core.Employee, calcul ancienneté)
4. Charger DimService  (depuis core.Service)
5. Charger FactSales   (Appointment réalisé + Invoice jointe)
```

- Utilise `bulk_create` pour la performance
- `select_related` pour éviter les N+1
- Idempotent (ignore les doublons via `source_appointment_id`)
- Enregistre l'horodatage dans `.etl_last_run`

## Dashboard — 4 pages

### 1. Tableau de bord (vue d'ensemble)
- 6 cartes KPI avec variation N-1 (CA, missions, panier moyen, clients actifs, taux d'occupation, créances)
- Graphique ligne : évolution du CA mensuel (avec tendance)
- Graphique barres horizontales : top 5 services par CA
- Tableau triable : performance des consultants

### 2. Analyse des revenus
- KPIs : CA total, missions, heures, variation N-1
- Filtre par catégorie de service
- Graphique barres : CA par mois
- Doughnut : répartition par catégorie
- Tableaux : top services, détail par client

### 3. Performance consultants
- KPIs : nombre, taux d'occupation moyen, CA/heure
- Graphique barres : CA par consultant
- Tableau : détail individuel (missions, heures, jauges)

### 4. Analyse clients
- KPIs : clients total, actifs, CA
- Doughnut : répartition par secteur
- Classement clients (% du CA, barres de progression)
- Fréquence des missions
- Alerte clients inactifs (> 3 mois)

## Séparation des responsabilités

```
dashboard/services.py   → Logique métier, calcul des KPIs (requêtes ORM)
dashboard/views.py      → Orchestration, contexte template, sérialisation JSON
dashboard/urls.py       → Routing (5 routes)
templates/              → Présentation HTML
static/js/charts.js     → Rendu graphique (Chart.js)
static/css/style.css    → Styles visuels
```

## Sécurité

- Authentification obligatoire sur toutes les vues (`@login_required`)
- Protection CSRF (middleware Django)
- Variables sensibles dans `.env` (SECRET_KEY, DB credentials)
- `ALLOWED_HOSTS` configurable par environnement
- Settings de production conditionnels (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `X_FRAME_OPTIONS`)
- ORM Django exclusivement (pas de SQL brut)

## Routage base de données

`DWRouter` dans `config/db_router.py` :
- App `dw` → base `dw` (lecture/écriture)
- Toutes les autres apps → base `default`
- Pas de relations cross-database

## Performance

- Indexes composites sur `FactSales` pour les jointures fréquentes
- `_base_qs()` factorise les filtres de dates
- Agrégats combinés (2 requêtes au lieu de 6 sur le dashboard)
- Requête clients inactifs optimisée (1 requête annotée au lieu de N)
- WhiteNoise pour le service des fichiers statiques

## Déploiement

```bash
# Production
DEBUG=False
SECRET_KEY=<clé-sécurisée-50-chars>
ALLOWED_HOSTS=mondomaine.ch
DATABASE_URL=postgres://user:pass@host/dbname
DW_DATABASE_URL=postgres://user:pass@host/dw_dbname
```

Serveur recommandé : Gunicorn + Nginx (ou Railway/Render pour le PaaS).
