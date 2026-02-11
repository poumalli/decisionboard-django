# decisionboard-django
# Plateforme Décisionnelle - EcoDistribution SARL

## Projet de diplôme ingénieur

**Contexte**: Développement complet d'une plateforme décisionnelle pour une PME de distribution de produits écologiques B2B.

**Technologies**:
- Base OLTP: PostgreSQL
- Data Warehouse: PostgreSQL (schéma dédié)
- ETL: Python (Pandas, SQLAlchemy)
- Dashboard: React + D3.js
- Hébergement: On-premise

## Structure du projet

```
├── database/
│   ├── oltp/          # Scripts SQL base de données opérationnelle
│   └── dw/            # Scripts SQL Data Warehouse
├── etl/
│   ├── src/           # Code Python ETL
│   └── config/        # Configuration ETL
├── dashboard/
│   ├── src/           # Application React
│   └── public/        # Assets publics
├── docs/
│   ├── architecture/  # Documentation technique
│   └── sql/           # Documentation schémas
├── data/              # Données de test
└── scripts/           # Scripts utilitaires
```

## KPI principaux

- Marge brute par produit/client
- Rentabilité client
- Rotation des stocks
- Taux de service client
- Coût logistique par commande
- Panier moyen

## Démarrage rapide

1. Configurer la base de données PostgreSQL
2. Exécuter les scripts OLTP dans `database/oltp/`
3. Lancer la chaîne ETL: `python etl/src/main.py`
4. Démarrer le dashboard: `cd dashboard && npm start`

