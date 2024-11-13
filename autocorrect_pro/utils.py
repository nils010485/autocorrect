import json
import socket
import sys
import os
from typing import Dict, Optional
from rich.console import Console
from .config import CONFIG_FILE, CONFIG_DIR, DEFAULT_CONFIG, CURRENT_VERSION, DEFAULT_SHORTCUT

console = Console()

def find_free_port() -> int:
    """Trouve un port disponible sur le système."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
        return port

def restart_application():
    """Redémarre l'application."""
    console.print("[bold blue]Redémarrage de l'application pour appliquer les changements de raccourci...[/bold blue]")
    python = sys.executable
    os.execl(python, python, *sys.argv)

def ensure_config_dir() -> None:
    """Assure que le répertoire de configuration existe."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> Dict:
    """Charge la configuration depuis le fichier."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Ajout des valeurs par défaut si manquantes
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
    except Exception as e:
        console.print(f"[bold red]Erreur lors de la lecture de la configuration: {e}[/bold red]")
    return DEFAULT_CONFIG.copy()

def save_config(api_key: str, model: str, theme: str = 'light',
                last_version: int = CURRENT_VERSION, shortcut: str = DEFAULT_SHORTCUT) -> bool:
    """Sauvegarde la configuration dans le fichier."""
    try:
        ensure_config_dir()
        config = {
            'api_key': api_key,
            'model': model,
            'theme': theme,
            'last_version': last_version,
            'shortcut': shortcut
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        console.print(f"[bold red]Erreur lors de la sauvegarde de la configuration: {e}[/bold red]")
        return False

def load_api_key() -> Optional[str]:
    """Charge la clé API depuis le fichier de configuration."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('api_key')
    except Exception as e:
        console.print(f"[bold red]Erreur lors de la lecture de la clé API: {e}[/bold red]")
    return None

def save_api_key(api_key: str) -> bool:
    """Sauvegarde la clé API dans le fichier de configuration."""
    try:
        ensure_config_dir()
        config = {'api_key': api_key}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        console.print(f"[bold red]Erreur lors de la sauvegarde de la clé API: {e}[/bold red]")
        return False
