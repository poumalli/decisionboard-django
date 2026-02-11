@echo off
REM Script d'exécution du pipeline ETL EcoDistribution

echo ========================================
echo Pipeline ETL EcoDistribution
echo ========================================

REM Vérification de Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installé ou non trouvé dans le PATH
    pause
    exit /b 1
)

REM Installation des dépendances si nécessaire
echo Vérification des dépendances Python...
pip show sqlalchemy >nul 2>&1
if %errorlevel% neq 0 (
    echo Installation des dépendances...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Erreur lors de l'installation des dépendances
        pause
        exit /b 1
    )
)

REM Configuration des variables d'environnement
if not exist .env (
    echo Création du fichier .env depuis .env.example...
    copy .env.example .env
    echo Veuillez éditer le fichier .env avec vos configurations de base de données
    pause
)

REM Exécution du pipeline ETL
echo.
echo Démarrage du pipeline ETL...
cd etl\src
python main.py --mode full

if %errorlevel% neq 0 (
    echo Erreur lors de l'exécution du pipeline ETL
    pause
    exit /b 1
)

echo.
echo ========================================
echo Pipeline ETL terminé avec succès !
echo ========================================
echo.
pause
