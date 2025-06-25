# 🐳 Assistant d'Épargne Intelligent - Installation Docker

## 🚀 Démarrage Rapide avec Docker

### Prérequis
- **Docker** installé sur votre système
- **Docker Compose** (inclus avec Docker Desktop)

### 📥 Installation et Lancement

#### Option 1 : Utilisation des scripts automatiques

**Linux/Mac :**
```bash
chmod +x run_docker.sh
./run_docker.sh
```

**Windows :**
```cmd
run_docker.bat
```

#### Option 2 : Commandes manuelles

1. **Cloner le projet**
```bash
git clone https://github.com/votre-repo/assistant-epargne-intelligent.git
cd assistant-epargne-intelligent
```

2. **Créer le répertoire de données**
```bash
mkdir -p data
```

3. **Construire et lancer l'application**
```bash
docker-compose up --build -d
```

4. **Accéder à l'application**
Ouvrez votre navigateur à l'adresse : **http://localhost:8501**

## 🛠️ Gestion du Conteneur

### Commandes Utiles

- **📊 Voir les logs en temps réel :**
```bash
docker-compose logs -f
```

- **🛑 Arrêter l'application :**
```bash
docker-compose down
```

- **🔄 Redémarrer l'application :**
```bash
docker-compose restart
```

- **🔧 Reconstruire l'image après modifications :**
```bash
docker-compose up --build -d
```

- **🗑️ Supprimer complètement (image + conteneur) :**
```bash
docker-compose down --rmi all -v
```

### 📁 Persistance des Données

Les données générées par l'application sont sauvegardées dans le répertoire `./data` de votre machine hôte, monté dans le conteneur. Cela permet de conserver vos données même après redémarrage du conteneur.

## 🔧 Configuration Avancée

### Variables d'Environnement

Vous pouvez modifier les variables d'environnement dans le fichier `docker-compose.yml` :

```yaml
environment:
  - STREAMLIT_SERVER_PORT=8501
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0
  - STREAMLIT_SERVER_HEADLESS=true
  - STREAMLIT_SERVER_ENABLE_CORS=false
```

### Personnalisation du Port

Pour changer le port (par défaut 8501), modifiez la ligne dans `docker-compose.yml` :

```yaml
ports:
  - "VOTRE_PORT:8501"
```

## 🐛 Dépannage

### Problèmes Courants

1. **Port déjà utilisé :**
   - Vérifiez qu'aucune autre application n'utilise le port 8501
   - Ou changez le port dans docker-compose.yml

2. **Erreur de construction :**
   - Vérifiez que Docker fonctionne : `docker --version`
   - Essayez : `docker-compose down && docker-compose up --build --no-cache`

3. **Problèmes de permissions (Linux) :**
   - Assurez-vous que votre utilisateur est dans le groupe docker
   - Ou exécutez avec `sudo`

### Vérification de l'État

- **État des conteneurs :**
```bash
docker ps
```

- **Utilisation des ressources :**
```bash
docker stats assistant-epargne-intelligent
```

## 📦 Architecture Docker

### Structure des Fichiers

```
assistant-epargne-intelligent/
├── Dockerfile              # Configuration de l'image
├── docker-compose.yml      # Orchestration des services  
├── .dockerignore           # Fichiers exclus du build
├── run_docker.sh          # Script de lancement Unix
├── run_docker.bat         # Script de lancement Windows
└── data/                  # Volume persistant pour les données
```

### Image Docker

- **Base :** Python 3.10-slim (légère et sécurisée)
- **Taille finale :** ~400MB
- **Sécurité :** Utilisateur non-root
- **Health check :** Vérification automatique de l'état

## 🌐 Déploiement en Production

Pour déployer en production, vous pouvez :

1. **Utiliser un serveur cloud** (AWS, Google Cloud, Azure)
2. **Configurer un reverse proxy** (Nginx)
3. **Ajouter HTTPS** avec Let's Encrypt
4. **Utiliser Docker Swarm** ou Kubernetes pour la scalabilité

### Exemple de configuration Nginx

```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez les logs : `docker-compose logs`
2. Consultez la documentation Docker officielle
3. Ouvrez une issue sur GitHub 