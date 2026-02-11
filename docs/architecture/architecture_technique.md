# Architecture Technique - EcoDistribution

## Vue d'ensemble

L'architecture de la plateforme décisionnelle EcoDistribution est basée sur une approche moderne et scalable, utilisant des technologies open-source éprouvées pour garantir performance, fiabilité et maintenabilité.

## Architecture Globale

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Applications  │    │   Data Warehouse│    │   Base OLTP     │
│   Dashboard     │    │   PostgreSQL    │    │   PostgreSQL    │
│   (React)       │    │   (Schéma DW)   │    │   (Schéma OLTP)  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │              ┌───────▼───────┐              │
          │              │   Pipeline ETL │              │
          │              │   (Python)     │              │
          │              └───────┬───────┘              │
          └──────────────┬───────▼───────┬──────────────┘
                         │   Réseau      │
                         └───────────────┘
```

## Composants Techniques

### 1. Base de Données Opérationnelle (OLTP)

**Technologie**: PostgreSQL 13+

**Caractéristiques**:
- Schéma normalisé 3NF
- Transactions ACID
- Indexation optimisée pour les requêtes transactionnelles
- Triggers pour la cohérence des données

**Tables principales**:
- T_CLIENTS, T_PRODUITS, T_COMMANDES_CLIENTS
- T_STOCKS, T_MOUVEMENTS_STOCKS
- T_FACTURES, T_LIVRAISONS

### 2. Data Warehouse

**Technologie**: PostgreSQL 13+ (schéma dédié)

**Architecture**: Schéma en étoile (Star Schema)

**Dimensions**:
- dim_temps: Hiérarchie temporelle complète
- dim_client: Informations clients et segmentations
- dim_produit: Caractéristiques produits et classifications
- dim_commercial: Équipe commerciale
- dim_entrepôt: Sites logistiques
- dim_transporteur: Partenaires transport

**Faits**:
- fait_ventes: Ventes et marges
- fait_stocks: Mouvements et valeurs stocks
- fait_livraisons: Performance logistique
- fait_facturation: Suivi financier

### 3. Pipeline ETL

**Technologie**: Python 3.9+

**Librairies principales**:
- SQLAlchemy: ORM et connexion DB
- Pandas: Manipulation données
- Psycopg2: Driver PostgreSQL

**Architecture**:
- Extraction depuis l'OLTP
- Transformation avec règles métier
- Loading dans le Data Warehouse
- Vues matérialisées pour performance

### 4. Dashboard Web

**Technologie**: React 18+

**Librairies principales**:
- Ant Design: Composants UI
- Recharts: Graphiques
- Axios: Appels API
- React Router: Navigation

**Fonctionnalités**:
- Tableau de bord principal avec KPI
- Analytics détaillés par domaine
- Filtres dynamiques
- Export des données

## Flux de Données

### 1. Flux Transactionnel (temps réel)

```
Client → Application → Base OLTP → Réponse
```

### 2. Flux Analytique (batch)

```
Base OLTP → ETL → Data Warehouse → API → Dashboard
```

**Fréquence de rafraîchissement**:
- Dimensions: Quotidien
- Faits: Quotidien
- Vues matérialisées: Quotidien

## Sécurité

### 1. Authentification
- Base de données: Utilisateurs dédiés par application
- Dashboard: JWT tokens (optionnel)

### 2. Autorisation
- Base OLTP: Rôles PostgreSQL (read/write)
- Data Warehouse: Lecture seule pour le dashboard
- ETL: Droits d'écriture sur le DW

### 3. Réseau
- Connexions chiffrées (SSL/TLS)
- Isolation des environnements

## Performance

### 1. Base de données
- Indexation stratégique
- Partitionnement des tables de faits (par date)
- Vues matérialisées pour les agrégations

### 2. ETL
- Traitement par lots (batch processing)
- Parallélisation des transformations
- Gestion des erreurs et reprise

### 3. Dashboard
- Mise en cache côté serveur
- Pagination des tableaux
- Chargement asynchrone des données

## Scalabilité

### 1. Verticale
- Augmentation des ressources serveur
- Optimisation des requêtes

### 2. Horizontale (future)
- Réplication de la base de données
- Clusterisation du Data Warehouse
- Microservices pour l'ETL

## Monitoring

### 1. Base de données
- Logs PostgreSQL
- Métriques de performance
- Alertes sur les seuils critiques

### 2. ETL
- Logs d'exécution détaillés
- Métriques de durée et volume
- Alertes en cas d'échec

### 3. Dashboard
- Monitoring des performances
- Logs des erreurs utilisateur
- Analytics d'utilisation

## Déploiement

### 1. Environnement de développement
- PostgreSQL local avec Docker
- Serveur de développement React
- Scripts de test automatisés

### 2. Environnement de production
- Serveur dédié ou cloud
- Sauvegardes automatisées
- Plan de reprise d'activité

## Maintenance

### 1. Base de données
- Maintenance régulière (VACUUM, ANALYZE)
- Sauvegardes quotidiennes
- Monitoring de l'espace disque

### 2. ETL
- Mise à jour des règles métier
- Optimisation des performances
- Gestion des évolutions de schéma

### 3. Dashboard
- Mises à jour des librairies
- Évolution des fonctionnalités
- Gestion des retours utilisateurs

## Évolutions Futures

### 1. Court terme (3-6 mois)
- API REST pour le dashboard
- Notifications en temps réel
- Export PDF des rapports

### 2. Moyen terme (6-12 mois)
- Machine Learning pour les prévisions
- Mobile application
- Intégration avec d'autres sources de données

### 3. Long terme (1+ an)
- Architecture microservices
- Data Lake pour les données brutes
- Advanced Analytics et AI

## Technologies Alternatives

### Base de données
- OLTP: MySQL, SQL Server
- DW: Snowflake, BigQuery, Redshift

### ETL
- Apache Airflow (orchestration)
- Talend (ETL visuel)
- Apache Spark (big data)

### Dashboard
- Tableau, Power BI (BI tools)
- Vue.js, Angular (frameworks)
- D3.js (graphiques personnalisés)

## Conclusion

Cette architecture technique offre un équilibre optimal entre simplicité, performance et évolutivité pour une PME comme EcoDistribution. L'utilisation de technologies open-source réduit les coûts tout en garantissant la pérennité de la solution.
