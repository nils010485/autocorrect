import os
import sys
from pathlib import Path
from typing import Dict

# Configuration des chemins
if sys.platform == "win32":
    CONFIG_DIR = Path(os.getenv('APPDATA')) / "AutoCorrectPro"
else:
    CONFIG_DIR = Path.home() / ".config"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "gemini.json"
ICON_PATH = Path(__file__).resolve().parent / 'templates' / 'faveicon.ico'

# Configuration générale
CURRENT_VERSION = 5
DEFAULT_SHORTCUT = "Ctrl+Space"

# Configuration des modèles AI
AVAILABLE_MODELS = {
    "gemini-1.5-flash": {
        "name": "Gemini Flash",
        "provider": "google",
        "model_name": "gemini-1.5-flash"
    },
    "gpt-4o-mini": {
        "name": "OpenAI GPT-4o Mini",
        "provider": "openai",
        "model_name": "gpt-4o-mini"
    },
    "claude-3-5-haiku-latest": {
        "name": "Anthropic Claude3.5 Haiku",
        "provider": "anthropic",
        "model_name": "claude-3-5-haiku-latest"
    }
}

# Prompts prédéfinis
PROMPTS = {
    "traduire": """Rôle : Traducteur professionnel
Tâche : Traduire le texte suivant entre le français et l'anglais
Instructions spécifiques :
- Si le texte est en français → traduire en anglais
- Si le texte est dans une autre langue → traduire en français
Format de sortie : Uniquement la traduction, sans commentaire ni texte original
Message à traduire :""",

    "analyser": """Rôle : Expert en analyse textuelle
Tâche : Identifier et expliquer les erreurs dans le texte
Instructions :
- Fournir une analyse concise et directe
- Se concentrer uniquement sur les erreurs principales
- Utiliser un langage simple et clair
Format : Réponse courte en points clés
Message à analyser :""",

    "corriger": """Rôle : Correcteur linguistique
Tâche : Corriger les erreurs orthographiques et grammaticales
Contraintes :
- Conserver la langue d'origine
- Maintenir le format et la structure du texte
- Préserver le style et le ton
Format de sortie : Uniquement le texte corrigé, sans commentaire
Message à corriger :""",

    "professionaliser": """Rôle : Consultant en communication professionnelle
Tâche : Transformer le message en version professionnelle
Directives :
- Maintenir l'intention et le message principal
- Adopter un ton professionnel mais naturel
- Éviter le langage trop formel ou pompeux il faut être raisonnable
Format de sortie : Uniquement le message transformé
Message à professionnaliser :""",

    "reformuler": """Rôle : Rédacteur expert
Tâche : Corriger et reformuler le message
Instructions :
- Corriger les erreurs linguistiques
- Améliorer la clarté et la fluidité
- Conserver la langue d'origine
- Garde le même ton que le message original
Format de sortie : Uniquement le message reformulé
Message à reformuler :""",

    "etendre": """Rôle : Rédacteur créatif
Tâche : Développer et enrichir le message
Objectifs :
- Ajouter des détails pertinents
- Améliorer la structure et la cohérence
- Maintenir le ton et le style original
Format de sortie : Uniquement le message étendu
Message à étendre :""",

    "repondre": """Rôle : Assistant de communication personnalisé

    Objectif : Générer une réponse naturelle et cohérente qui s'aligne parfaitement avec le message d'origine

    Instructions détaillées :
    1. Analyse du message reçu
    - Identifier l'expéditeur (pas le destinataire !!) si possible et personnaliser la salutation
    - Repérer le ton (formel/informel/amical/professionnel)
    - Noter le niveau de langue et le vocabulaire utilisé
    - Identifier les expressions et tournures de phrases caractéristiques

    2. Adaptation de la réponse souhaitez pas l'utilisateur en accord avec la message reçu
    - Maintenir une cohérence stylistique avec le message reçu
    - Reformuler (pas de fautes, pas d'écriture SMS ou autres)
    - Reproduire le même niveau de formalité
    - Utiliser un vocabulaire similaire
    - Conserver les expressions idiomatiques si présentes
    - Respecter la longueur et la structure des phrases

    3. Intégration du contenu
    - Incorporer naturellement les éléments de réponse fournis
    - Assurer une transition fluide entre les idées
    - Maintenir la logique conversationnelle

    4. Vérification finale
    - Confirmer l'alignement stylistique avec le message original
    - Vérifier la cohérence du ton
    - S'assurer que la réponse est appropriée au contexte

    Entrées :
    Message reçu : {original_message}
    Éléments de réponse : {user_response}

    Format de sortie : 
    Réponse au message originel formatée et avec une bonen syntaxe uniquement, sans métadonnées ni explications
    """
}

DEFAULT_CONFIG: Dict = {
    'api_key': None,
    'model': 'gemini-1.5-flash',
    'theme': 'light',
    'last_version': 1,
    'shortcut': DEFAULT_SHORTCUT
}