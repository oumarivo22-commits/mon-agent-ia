# ===================================================================
# AGENT AUTONOME DE CONTENU V1.5 - PUBLICATION WORDPRESS
#
# Rôle :
# 1. Détecte les tendances (Google Trends, Reddit).
# 2. Génère un article de qualité avec l'IA DeepSeek.
# 3. Publie automatiquement l'article sur WordPress.
# ===================================================================

import os
import time
import logging
import re
import requests
from typing import List, Dict, Optional

# --- Configuration du Logging ---
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AgentAutonome')

# --- Vérification des outils ---
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    logger.warning("Outil 'pytrends' non trouvé. (pip install pytrends)")

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    logger.warning("Outil 'praw' non trouvé. (pip install praw)")

# ===================================================================
# MODULE 1 : Le "Radar" (TrendRadar)
# ===================================================================
class TrendRadar:
    def __init__(self):
        self.logger = logging.getLogger('TrendRadar')
        self.commercial_keywords = ['achat', 'prix', 'test', 'avis', 'meilleur', 'guide']
        self.trends_client = self._init_google_trends()
        self.reddit_client = self._init_reddit()
        self.logger.info("🎯 Radar à tendances initialisé.")

    def _init_google_trends(self) -> Optional[TrendReq]:
        if not PYTRENDS_AVAILABLE: return None
        try: return TrendReq(hl='fr-FR', tz=60)
        except Exception as e:
            self.logger.error(f"❌ Erreur connexion Google Trends: {e}")
            return None
    
    def _init_reddit(self) -> Optional[praw.Reddit]:
        if not PRAW_AVAILABLE: return None
        try:
            client = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent='AgentAutonome/1.5'
            )
            assert client.read_only
            self.logger.info("✅ Connecté à l'API Reddit.")
            return client
        except Exception as e:
            self.logger.error(f"❌ Erreur connexion Reddit: {e}")
            return None
    
    def detect_trends(self) -> List[Dict]:
        trends = []
        if self.trends_client:
            try:
                df = self.trends_client.trending_searches(pn='france')
                for i, trend in enumerate(df[0].head(5)):
                    trends.append({"title": trend, "source": "Google", "score": 100 - i*10})
            except Exception: pass
        if self.reddit_client:
            try:
                for post in self.reddit_client.subreddit("france+technologie").hot(limit=5):
                    if not post.stickied:
                        trends.append({"title": post.title, "source": "Reddit", "score": post.score / 5})
            except Exception: pass
        self.logger.info(f"📈 {len(trends)} tendances détectées.")
        return trends

    def select_best_topic(self, trends: List[Dict]) -> Optional[Dict]:
        if not trends: return None
        for trend in trends:
            trend['score'] += sum(1 for kw in self.commercial_keywords if kw in trend['title'].lower()) * 20
        best_topic = sorted(trends, key=lambda x: x['score'], reverse=True)[0]
        self.logger.info(f"🎯 Sujet choisi: '{best_topic['title']}' (Score: {best_topic['score']:.0f})")
        return best_topic

# ===================================================================
# MODULE 2 : Le "Moteur" (ContentEngine)
# ===================================================================
class ContentEngine:
    def __init__(self):
        self.logger = logging.getLogger('ContentEngine')
        self.logger.info("⚙️ Moteur de contenu initialisé.")

    def generate_content(self, prompt: str) -> Optional[str]:
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            self.logger.error("❌ Clé API DEEPSEEK_API_KEY non trouvée.")
            return None
        self.logger.info("✍️ Envoi de la demande à l'IA...")
        try:
            response = requests.post(
                url="https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]},
                timeout=180
            )
            response.raise_for_status()
            self.logger.info("✅ L'IA a terminé d'écrire l'article.")
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            self.logger.error(f"❌ Erreur pendant l'écriture par l'IA: {e}")
            return None

    def publish_to_wordpress(self, title: str, content: str) -> bool:
        """Publie l'article sur WordPress via l'API REST."""
        wp_url = os.getenv('WP_URL')
        wp_user = os.getenv('WP_USERNAME')
        wp_pass = os.getenv('WP_APPLICATION_PASSWORD')

        if not all([wp_url, wp_user, wp_pass]):
            self.logger.warning("⚠️ Identifiants WordPress non configurés. Publication annulée.")
            return False
        
        api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts"
        post_data = {"title": title, "content": content, "status": "publish"}

        self.logger.info(f"📤 Publication de l'article sur {wp_url}...")
        try:
            response = requests.post(api_url, json=post_data, auth=(wp_user, wp_pass), timeout=30)
            response.raise_for_status()
            self.logger.info(f"✅ Article publié avec succès ! URL : {response.json().get('link')}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur de publication WordPress : {e}")
            return False

# ===================================================================
# MODULE 3 : Le "Chef d'Orchestre" (AutonomousAgent)
# ===================================================================
class AutonomousAgent:
    def __init__(self, cycle_hours: int = 12):
        self.trend_radar = TrendRadar()
        self.content_engine = ContentEngine()
        self.cycle_interval_seconds = cycle_hours * 3600
        self.logger = logging.getLogger('AutonomousAgent')
        self.logger.info(f"🤖 Agent V1.5 prêt. Cycle de {cycle_hours} heures.")

    def create_prompt_from_topic(self, topic: Dict) -> str:
        return (
            f"Rédige un article de blog détaillé sur le sujet : '{topic['title']}'. "
            "Structure l'article avec une introduction, plusieurs sections avec des sous-titres, et une conclusion. "
            "Le ton doit être professionnel. Longueur : environ 800 mots."
        )

    def run_single_cycle(self):
        self.logger.info("--- Lancement d'un nouveau cycle ---")
        trends = self.trend_radar.detect_trends()
        best_topic = self.trend_radar.select_best_topic(trends)
        if not best_topic:
            self.logger.warning("Aucun sujet intéressant trouvé.")
            return

        prompt = self.create_prompt_from_topic(best_topic)
        article_content = self.content_engine.generate_content(prompt)
        if article_content:
            # Publication sur WordPress
            success = self.content_engine.publish_to_wordpress(best_topic['title'], article_content)
            if not success:
                self.logger.error("Échec de la publication, l'article n'est pas en ligne.")
        else:
            self.logger.error("Échec de la création de l'article.")
        
        self.logger.info("--- Fin du cycle ---")

    def start(self):
        while True:
            self.run_single_cycle()
            self.logger.info(f"En pause pour {self.cycle_interval_seconds / 3600:.0f} heures...")
            time.sleep(self.cycle_interval_seconds)

# ===================================================================
# POINT DE DÉPART DU PROGRAMME
# ===================================================================
if __name__ == "__main__":
    print("Démarrage de l'Agent Autonome V1.5 (Publication WordPress)")
    try:
        from dotenv import load_dotenv
        if load_dotenv():
            print("Fichier de configuration .env chargé.")
        else:
            print("Fichier .env non trouvé.")
    except ImportError:
        print("Outil 'python-dotenv' non trouvé.")
    
    agent = AutonomousAgent(cycle_hours=12)
    agent.start()

