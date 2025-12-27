# AI AUTOCORRECT

![AI AUTOCORRECT DEMO](https://autocorrect.fieryaura.eu/app.png)

> Transform your writing with artificial intelligence

## About

Hey! I'm [Nils](https://nils.begou.dev), the creator of AI AUTOCORRECT. I'll be honest - the code isn't as clean as I'd like it to be yet (you know how it is when you're passionate, you code first, organize later). If you're a developer and want to help make this project shine, your PRs are more than welcome!

## Why AI AUTOCORRECT?

Imagine having a personal assistant that:
- Corrects your text instantly (really, in less than a second!)
- Translates your messages like a native speaker
- Rephrases your ideas to make them shine
- Transforms your drafts into professional text
- Analyzes and improves your writing style
- Transcribes all your audio files in a flash

## How it works

AI AUTOCORRECT relies on the best AI models on the market:
- **Google Gemini** (free!)
- **Anthropic Claude**
- **OpenAI GPT**
- **Local models**

The best part? You keep full control with your own API keys!

## Get Started in 2 Minutes

### Option "I just want to use it"
1. Go to [autocorrect.fieryaura.eu](https://autocorrect.fieryaura.eu/)
2. Download the version for your system
3. You're done!

> Linux users: Don't forget to install `python3.11` and `python3.11-devel`!

### Option "I want to tinker"

```bash
# Clone the project
git clone https://github.com/nils010485/autocorrect.git
cd autocorrect

# Create Python virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Build frontend (optional - pre-built assets included)
# Only needed if modifying Tailwind CSS
npm install
npm run build

# Run the application
python main.py
```

### Option: I'm comfortable with Python
```bash
# Installation via pip (after cloning the repo)
pip install --editable .

# Direct launch
ai-autocorrect
```

## Frontend Build Process (For Developers)

The application uses Tailwind CSS. Pre-built assets are included, so you don't need to build anything unless you're modifying styles.

### Prerequisites
- Node.js 18+ and npm

### Build Commands
```bash
npm install      # Install dependencies
npm run build    # Build CSS for production
npm run dev      # Watch for changes during development
```

## Project Structure

```
ai-autocorrect/
├── autocorrect_pro/
│   ├── config.py      # Configuration management
│   ├── gui.py         # The interface that makes everything shine
│   ├── models.py      # The AI magic
│   ├── routes.py      # The traffic controller
│   └── utils.py       # The toolbox
├── static/
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   └── vendor/        # Third-party libraries
├── templates/         # Jinja2 templates
└── main.py           # Application entry point
```

## Privacy First

Your privacy is sacred! AI AUTOCORRECT:
- Stores NO data
- Communicates directly with APIs
- Keeps your API keys local
- Does no telemetry

## Contributing

Whether you're a seasoned developer or an enthusiastic beginner, your help is precious! Here are some ways to participate:
- Track bugs
- Propose features
- Clean up code
- Improve documentation

## Need Help?

- Open an issue on GitHub
- Contact me directly

## License

This project is under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license

### What you can do:
- Copy and redistribute the code
- Modify and adapt the code
- Use the project for personal use

### Provided that you:
- **Credit** the project and its author
- **Do NOT** use it for commercial purposes

### What is prohibited:
- Selling the code or a modified version
- Using the code in a commercial project
- Distributing the code without attribution

For the full license text: [CC BY-NC 4.0](https://creativecommons.org/by-nc/4.0/)

---

<p align="center">
  Made with ❤️ by Nils<br>
  © 2022-2026 AI AUTOCORRECT
</p>
