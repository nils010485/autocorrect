
# 🤖 AI AUTOCORRECT

![AI AUTOCORRECT DEMO](https://autocorrect.fieryaura.eu/app.png)

> Transformez votre façon d'écrire avec l'intelligence artificielle !

## 🎯 Un petit mot avant de commencer...

Hey ! Je suis [Nils](https://nils.begou.dev), le créateur d'AI AUTOCORRECT. Je dois vous avouer quelque chose : le code n'est pas encore aussi propre que je le voudrais (vous savez, quand on est passionné, on code d'abord, on range après 😅). Si vous êtes développeur et que vous avez envie de m'aider à faire briller ce projet, vos PR sont plus que bienvenues !

## ✨ Pourquoi AI AUTOCORRECT ?

Imaginez avoir un assistant personnel qui :
- 🚀 Corrige vos textes instantanément (vraiment, en moins d'une seconde !)
- 🌍 Traduit vos messages comme un natif
- ✍️ Reformule vos idées pour qu'elles brillent
- 🎩 Transforme vos brouillons en textes professionnels
- 💡 Analyse et améliore votre style d'écriture

## 🛠️ Comment ça marche ?

AI AUTOCORRECT s'appuie sur les meilleurs modèles d'IA du marché :
- 🧠 **Google Gemini** (gratuit !)
- 🎯 **Anthropic Claude**
- ⚡ **OpenAI GPT**

Le plus cool ? Vous gardez le contrôle total avec vos propres clés API !

## 🚀 Démarrez en 2 minutes

### 📦 Option "Je veux juste l'utiliser"
1. Direction [autocorrect.fieryaura.eu](https://autocorrect.fieryaura.eu/)
2. Téléchargez la version qui correspond à votre système
3. Et c'est parti ! 

> 🐧 Utilisateurs Linux : N'oubliez pas d'installer `python3.11` et `python3.11-devel` !

### 👨‍💻 Option "Je veux bidouiller"

```bash
# On clone le projet
git clone https://github.com/yourusername/ai-autocorrect.git
cd ai-autocorrect

# On crée notre environnement Python
python3.11 -m venv venv

# On l'active (Linux/Mac)
source venv/bin/activate
# ou (Windows)
venv\Scripts\activate

# On installe les dépendances
pip install -r requirements.txt

# Et on lance !
python main.py
```

### 🤔 Option: Je suis à l'aise avec Python  
J'aurais aimé vous permettre d'installer l'application avec pip, mais pour l'instant ce n'est pas le cas (je rendrai tout ça compatible bientôt ou vous pouvez faire une PR si vous voulez m'aider).  

## 🗂️ Structure python du projet

```
ai-autocorrect/
├── 🔧 config.py      # Le cerveau de la configuration
├── 🖥️ gui.py         # L'interface qui fait tout briller
├── 🤖 models.py      # La magie de l'IA
├── 🛣️ routes.py      # Le traffic controller de l'app
└── 🛠️ utils.py       # La boîte à outils
```

## 🔒 Confidentialité avant tout !

Votre vie privée, c'est sacré ! AI AUTOCORRECT :
- Ne stocke AUCUNE donnée
- Communique directement avec les API
- Garde vos clés API en local
- Ne fait pas de télémétrie

## 🤝 Envie de contribuer ?

Que vous soyez développeur chevronné ou débutant enthousiaste, votre aide est précieuse ! Voici quelques façons de participer :
- 🐛 Traquer les bugs
- 💡 Proposer des fonctionnalités
- 🧹 Nettoyer le code
- 📝 Améliorer la documentation

## 📫 Besoin d'aide ?

- 🌟 Ouvrez une issue sur GitHub
- 📧 Contactez-moi directement
## 🗺️ Roadmap

Voici les améliorations prévues pour AI AUTOCORRECT :

### 🧹 Nettoyage & Architecture
- [ ] Refactorisation complète du code pour plus de clarté et de maintenabilité
- [ ] Centralisation des ressources dans une structure plus cohérente
- [ ] Migration des CDN vers des ressources statiques locales pour une meilleure fiabilité
- [ ] Préparation du code pour une distribution via pip

### 🌍 Internationalisation
- [ ] Support multilingue complet de l'interface
- [ ] Traduction des prompts et messages système
- [ ] Détection automatique de la langue du système

### 🔌 Backend & API
- [ ] Migration vers l'endpoint OpenAI-compatible de Google (adieu la lib propriétaire !)
- [ ] Intégration de nouveaux backends :
  - [ ] OpenRouter
  - [ ] LocalAI
  - [ ] Autres fournisseurs d'IA
- [ ] Interface unifiée pour tous les backends

### 🎯 En cours de réalisation
#### 13/11/2024
- [x] Interface utilisateur intuitive
- [x] Support des principaux modèles d'IA
- [x] Système de prompts personnalisables

> 💡 Vous avez des idées pour améliorer AI AUTOCORRECT ? N'hésitez pas à ouvrir une issue ou à proposer une PR !

## 📜 Licence

Ce projet est sous licence **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**

### Ce que vous pouvez faire :
- ✅ Copier et redistribuer le code
- ✅ Modifier et adapter le code
- ✅ Utiliser le projet pour un usage personnel

### À condition de :
- 📝 **Créditer** le projet et son auteur (attribution)
- 💰 **Ne pas** l'utiliser à des fins commerciales

### Ce qui est interdit :
- ❌ Vendre le code ou une version modifiée
- ❌ Utiliser le code dans un projet commercial
- ❌ Distribuer le code sans attribution

Pour voir le texte complet de la licence : [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
---

<p align="center">
  Made with ❤️ by Nils<br>
  © 2022-2024 AI AUTOCORRECT
</p>

