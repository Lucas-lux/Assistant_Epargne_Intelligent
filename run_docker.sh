#!/bin/bash

# Script de lancement de l'Assistant d'Épargne Intelligent avec Docker

echo "🐳 Démarrage de l'Assistant d'Épargne Intelligent avec Docker..."

# Créer le répertoire data s'il n'existe pas
mkdir -p data

# Arrêter et supprimer les conteneurs existants
echo "🛑 Arrêt des conteneurs existants..."
docker-compose down

# Construire et démarrer l'application
echo "🔨 Construction de l'image Docker..."
docker-compose up --build -d

# Attendre que le service soit prêt
echo "⏳ Attente du démarrage du service..."
sleep 10

# Vérifier si le conteneur fonctionne
if docker ps | grep -q "assistant-epargne-intelligent"; then
    echo "✅ L'application est maintenant disponible à l'adresse :"
    echo "🌐 http://localhost:8501"
    echo ""
    echo "📋 Commandes utiles :"
    echo "  - Voir les logs : docker-compose logs -f"
    echo "  - Arrêter l'app : docker-compose down"
    echo "  - Redémarrer : docker-compose restart"
else
    echo "❌ Erreur lors du démarrage du conteneur"
    echo "📋 Vérifiez les logs avec : docker-compose logs"
fi 