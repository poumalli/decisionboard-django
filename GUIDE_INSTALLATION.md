# Guide d'Installation - EcoDistribution

## Prérequis

### 1. Base de données
- **PostgreSQL 13+** installé et en cours d'exécution
- Créer un utilisateur `postgres` avec mot de passe `password` (ou adapter les scripts)

### 2. Python
- **Python 3.9+** installé
- `pip` (gestionnaire de packages Python)

### 3. Node.js
- **Node.js 16+** installé
- `npm` (gestionnaire de packages Node.js)

## Installation Rapide

### 1. Cloner le projet
```bash
git clone <repository-url>
cd TRAVAIL_DIPLOME
```

### 2. Configurer les bases de données
```bash
# Exécuter le script d'installation (Windows)
scripts\setup_database.bat

# Ou manuellement :
# 1. Créer les bases de données
createdb -U postgres ecodistribution_oltp
createdb -U postgres ecodistribution_dw

# 2. Installer les schémas
psql -U postgres -d ecodistribution_oltp -f database/oltp/01_create_tables.sql
psql -U postgres -d ecodistribution_oltp -f database/oltp/02_insert_data.sql
psql -U postgres -d ecodistribution_dw -f database/dw/01_create_dw_schema.sql
```

### 3. Configurer l'environnement Python
```bash
# Installer les dépendances Python
pip install -r requirements.txt

# Configurer les variables d'environnement
copy .env.example .env
# Éditer .env avec vos configurations de base de données
```

### 4. Lancer le pipeline ETL
```bash
# Exécuter le script (Windows)
scripts\run_etl.bat

# Ou manuellement :
cd etl/src
python main.py --mode full
```

### 5. Démarrer le dashboard
```bash
# Exécuter le script (Windows)
scripts\start_dashboard.bat

# Ou manuellement :
cd dashboard
npm install
npm start
```

## Accès à l'Application

- **Dashboard**: http://localhost:3000
- **Base de données OLTP**: localhost:5432/ecodistribution_oltp
- **Data Warehouse**: localhost:5432/ecodistribution_dw

## Structure du Projet

```
TRAVAIL_DIPLOME/
├── database/
│   ├── oltp/           # Base de données opérationnelle
│   └── dw/             # Data Warehouse
├── etl/
│   ├── src/            # Code Python ETL
│   └── config/         # Configuration
├── dashboard/
│   ├── src/            # Application React
│   └── public/         # Assets publics
├── docs/
│   └── architecture/   # Documentation technique
├── scripts/            # Scripts d'automatisation
├── requirements.txt    # Dépendances Python
├── package.json        # Dépendances Node.js
└── .env.example        # Configuration environnement
```

## Vérification de l'Installation

### 1. Base de données OLTP
```sql
-- Vérifier les données
SELECT COUNT(*) FROM T_CLIENTS;      -- Doit retourner 5
SELECT COUNT(*) FROM T_PRODUITS;     -- Doit retourner 20
SELECT COUNT(*) FROM T_COMMANDES_CLIENTS; -- Doit retourner 8
```

### 2. Data Warehouse
```sql
-- Vérifier les dimensions
SELECT COUNT(*) FROM dw.dim_client;     -- Doit retourner 5
SELECT COUNT(*) FROM dw.dim_produit;    -- Doit retourner 20
SELECT COUNT(*) FROM dw.fait_ventes;    -- Doit retourner > 0
```

### 3. Dashboard
- Ouvrir http://localhost:3000
- Vérifier que les KPI s'affichent
- Naviguer entre les différentes sections

## Dépannage

### Problèmes courants

#### 1. "PostgreSQL n'est pas installé"
- Télécharger et installer PostgreSQL depuis https://www.postgresql.org/download/
- Assurer que le service PostgreSQL est démarré

#### 2. "Erreur de connexion à la base de données"
- Vérifier que PostgreSQL est en cours d'exécution
- Vérifier les identifiants dans le fichier `.env`
- Vérifier que les bases de données existent

#### 3. "Python n'est pas reconnu"
- Ajouter Python au PATH système
- Redémarrer le terminal

#### 4. "Erreur lors de l'installation npm"
- Exécuter `npm cache clean --force`
- Supprimer le dossier `node_modules` et réessayer

#### 5. "Le dashboard ne se charge pas"
- Vérifier que le port 3000 n'est pas utilisé
- Vérifier la console du navigateur pour les erreurs

### Logs et monitoring

- **ETL logs**: `etl/etl.log`
- **Console navigateur**: F12 → onglet Console
- **Logs PostgreSQL**: Voir configuration PostgreSQL

## Configuration Avancée

### 1. Modification des identifiants base de données
Éditer le fichier `.env` :
```env
OLTP_HOST=localhost
OLTP_PORT=5432
OLTP_DATABASE=ecodistribution_oltp
OLTP_USERNAME=votre_user
OLTP_PASSWORD=votre_password

DW_HOST=localhost
DW_PORT=5432
DW_DATABASE=ecodistribution_dw
DW_USERNAME=votre_user
DW_PASSWORD=votre_password
```

### 2. Personnalisation du port du dashboard
Éditer `dashboard/package.json` :
```json
{
  "scripts": {
    "start": "react-scripts start --port=3001"
  }
}
```

### 3. Planification de l'ETL
Pour une exécution automatique quotidienne :
- **Windows**: Utiliser le Planificateur de tâches
- **Linux/Mac**: Utiliser cron

Exemple cron (tous les jours à 2h du matin) :
```bash
0 2 * * * cd /chemin/vers/TRAVAIL_DIPLOME && python etl/src/main.py --mode full
```

## Support

En cas de problème :
1. Consulter les logs dans les fichiers respectifs
2. Vérifier la documentation technique dans `docs/architecture/`
3. Consulter les commentaires dans les fichiers de configuration

## Prochaines Étapes

1. Explorer les données dans les bases de données
2. Personnaliser le dashboard selon vos besoins
3. Ajouter de nouveaux KPI et graphiques
4. Implémenter des fonctionnalités avancées (prévisions, alertes, etc.)
