@echo off
REM Script d'installation des bases de données EcoDistribution
REM PostgreSQL doit être installé et en cours d'exécution

echo ========================================
echo Installation des bases de données EcoDistribution
echo ========================================

REM Configuration des variables
set PGUSER=postgres
set PGPASSWORD=password
set PGHOST=localhost
set PGPORT=5432

REM Création des bases de données
echo.
echo Création de la base de données OLTP...
createdb -U %PGUSER% -h %PGHOST% -p %PGPORT% ecodistribution_oltp
if %errorlevel% neq 0 (
    echo Erreur lors de la création de la base OLTP
    pause
    exit /b 1
)

echo Création de la base de données Data Warehouse...
createdb -U %PGUSER% -h %PGHOST% -p %PGPORT% ecodistribution_dw
if %errorlevel% neq 0 (
    echo Erreur lors de la création de la base DW
    pause
    exit /b 1
)

REM Installation du schéma OLTP
echo.
echo Installation du schéma OLTP...
psql -U %PGUSER% -h %PGHOST% -p %PGPORT% -d ecodistribution_oltp -f "database\oltp\01_create_tables.sql"
if %errorlevel% neq 0 (
    echo Erreur lors de la création des tables OLTP
    pause
    exit /b 1
)

echo Insertion des données de test OLTP...
psql -U %PGUSER% -h %PGHOST% -p %PGPORT% -d ecodistribution_oltp -f "database\oltp\02_insert_data.sql"
if %errorlevel% neq 0 (
    echo Erreur lors de l'insertion des données OLTP
    pause
    exit /b 1
)

REM Installation du schéma Data Warehouse
echo.
echo Installation du schéma Data Warehouse...
psql -U %PGUSER% -h %PGHOST% -p %PGPORT% -d ecodistribution_dw -f "database\dw\01_create_dw_schema.sql"
if %errorlevel% neq 0 (
    echo Erreur lors de la création du schéma DW
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation terminée avec succès !
echo ========================================
echo.
echo Bases de données créées :
echo - ecodistribution_oltp (base opérationnelle)
echo - ecodistribution_dw (data warehouse)
echo.
echo Vous pouvez maintenant :
echo 1. Lancer le pipeline ETL : python etl\src\main.py
echo 2. Démarrer le dashboard : cd dashboard && npm install && npm start
echo.
pause
