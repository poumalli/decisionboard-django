@echo off
REM Script de démarrage du dashboard EcoDistribution

echo ========================================
echo Dashboard EcoDistribution
echo ========================================

REM Vérification de Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js n'est pas installé ou non trouvé dans le PATH
    echo Veuillez installer Node.js depuis https://nodejs.org/
    pause
    exit /b 1
)

REM Vérification de npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo npm n'est pas installé
    pause
    exit /b 1
)

REM Navigation dans le répertoire du dashboard
cd dashboard

REM Installation des dépendances si nécessaire
if not exist node_modules (
    echo Installation des dépendances React...
    npm install
    if %errorlevel% neq 0 (
        echo Erreur lors de l'installation des dépendances
        pause
        exit /b 1
    )
)

REM Démarrage du dashboard
echo.
echo Démarrage du dashboard...
echo Le dashboard sera accessible à l'adresse : http://localhost:3000
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.

npm start

pause
