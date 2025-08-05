# 🚀 Agent Autonome - Déploiement Railway

Ce guide vous explique comment déployer votre agent autonome sur Railway gratuitement.

## 📋 Prérequis

- Un compte GitHub
- Un compte Railway (gratuit)
- Vos clés API (DeepSeek, Reddit, WordPress)

## 🔧 Étapes de Déploiement

### 1. Préparer votre projet GitHub

1. Créez un nouveau repository sur GitHub
2. Uploadez ces fichiers dans votre repository :
   - `agent_autonome.py` (votre script principal)
   - `requirements.txt`
   - `Procfile`
   - `.env.example`
   - `README.md`

### 2. Déployer sur Railway

1. Allez sur [railway.app](https://railway.app)
2. Connectez-vous avec votre compte GitHub
3. Cliquez sur "New Project"
4. Sélectionnez "Deploy from GitHub repo"
5. Choisissez votre repository

### 3. Configurer les Variables d'Environnement

Dans Railway, allez dans l'onglet "Variables" et ajoutez :

```
DEEPSEEK_API_KEY=votre_vraie_clé_deepseek
REDDIT_CLIENT_ID=votre_reddit_client_id
REDDIT_CLIENT_SECRET=votre_reddit_client_secret
WP_URL=https://votre-site-wordpress.com
WP_USERNAME=votre_username_wordpress
WP_APPLICATION_PASSWORD=votre_mot_de_passe_app_wordpress
LOG_LEVEL=INFO
```

### 4. Déploiement Automatique

Railway détectera automatiquement :
- `requirements.txt` → Installera les dépendances Python
- `Procfile` → Lancera votre agent avec `python agent_autonome.py`

## 🔑 Obtenir vos Clés API

### DeepSeek (via OpenRouter)
1. Allez sur [openrouter.ai](https://openrouter.ai)
2. Créez un compte
3. Générez une clé API
4. Format : `sk-or-v1-xxxxx`

### Reddit API
1. Allez sur [reddit.com/prefs/apps](https://reddit.com/prefs/apps)
2. Créez une nouvelle application (type "script")
3. Notez le `client_id` et `client_secret`

### WordPress
1. Dans votre WordPress, allez dans "Utilisateurs > Votre Profil"
2. Descendez à "Mots de passe d'application"
3. Créez un nouveau mot de passe pour l'agent
4. Utilisez ce mot de passe (pas votre mot de passe habituel)

## ⚡ Fonctionnement

Une fois déployé, votre agent :
- Se lance automatiquement sur Railway
- Détecte les tendances toutes les 12 heures
- Génère des articles avec l'IA
- Les publie automatiquement sur WordPress

## 🆓 Limites du Plan Gratuit Railway

- 500 heures d'exécution par mois (largement suffisant)
- 1 GB de RAM
- Parfait pour un agent qui tourne en continu

## 🔧 Dépannage

Si le déploiement échoue :
1. Vérifiez que tous les fichiers sont présents
2. Vérifiez que vos variables d'environnement sont correctes
3. Consultez les logs dans Railway pour voir les erreurs

## 📞 Support

En cas de problème, vérifiez :
- Que votre site WordPress accepte l'API REST
- Que vos clés API sont valides
- Que le nom de votre fichier principal est bien `agent_autonome.py`

