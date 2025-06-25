@echo off
REM Script de lancement de l'Assistant d'Épargne Intelligent avec Docker (Windows)

echo 🐳 Démarrage de l'Assistant d'Épargne Intelligent avec Docker...

REM Créer le répertoire data s'il n'existe pas
if not exist "data" mkdir data

REM Arrêter et supprimer les conteneurs existants
echo 🛑 Arrêt des conteneurs existants...
docker-compose down

REM Construire et démarrer l'application
echo 🔨 Construction de l'image Docker...
docker-compose up --build -d

REM Attendre que le service soit prêt
echo ⏳ Attente du démarrage du service...
timeout /t 10 /nobreak > nul

REM Vérifier si le conteneur fonctionne
docker ps | findstr "assistant-epargne-intelligent" > nul
if %errorlevel%==0 (
    echo ✅ L'application est maintenant disponible à l'adresse :
    echo 🌐 http://localhost:8501
    echo.
    echo 📋 Commandes utiles :
    echo   - Voir les logs : docker-compose logs -f
    echo   - Arrêter l'app : docker-compose down
    echo   - Redémarrer : docker-compose restart
) else (
    echo ❌ Erreur lors du démarrage du conteneur
    echo 📋 Vérifiez les logs avec : docker-compose logs
)

pause 