import json
import socket
import sys
import os
from typing import Dict, Optional
from rich.console import Console
from .config import CONFIG_FILE, CONFIG_DIR, DEFAULT_CONFIG, CURRENT_VERSION, DEFAULT_SHORTCUT, CUSTOM_MODES_SCHEMA, \
    MODES

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


def load_config() -> dict:
    """Charge la configuration depuis le fichier JSON."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Assurez-vous que toutes les clés nécessaires sont présentes
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
    except Exception as e:
        print(f"Erreur lors de la lecture de la configuration: {e}")
    return DEFAULT_CONFIG.copy()


def save_config(api_key=None, model=None, theme=None, last_version=None, shortcut=None, modes=None) -> bool:
    """Sauvegarde la configuration dans le fichier JSON."""
    try:
        config = load_config()
        if api_key is not None:
            config['api_key'] = api_key
        if model is not None:
            config['model'] = model
        if theme is not None:
            config['theme'] = theme
        if last_version is not None:
            config['last_version'] = last_version
        if shortcut is not None:
            config['shortcut'] = shortcut
        if modes is not None:
            config['modes'] = modes

        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la configuration: {e}")
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



def load_modes() -> dict:
    """Charge les modes depuis la configuration."""
    config = load_config()
    if 'modes' not in config:
        # Initialiser avec les modes par défaut si aucun mode n'est configuré
        config['modes'] = {
            'system': MODES,
            'custom': {},
            'order': list(MODES.keys())
        }
        save_config(modes=config['modes'])
    else:
        # Assurez-vous que les modes système sont toujours présents
        if 'system' not in config['modes']:
            config['modes']['system'] = MODES
        else:
            # Mettre à jour les modes système existants
            for mode_id, mode_data in MODES.items():
                if mode_id not in config['modes']['system']:
                    config['modes']['system'][mode_id] = mode_data

        # Initialiser les modes personnalisés s'ils n'existent pas
        if 'custom' not in config['modes']:
            config['modes']['custom'] = {}

        # S'assurer que l'ordre contient tous les modes
        if 'order' not in config['modes']:
            all_modes = {**config['modes']['system'], **config['modes']['custom']}
            config['modes']['order'] = list(all_modes.keys())

    return config['modes']


def save_custom_mode(mode_data):
    """Sauvegarde un nouveau mode personnalisé."""
    config = load_config()
    if 'modes' not in config:
        config['modes'] = CUSTOM_MODES_SCHEMA['modes']

    mode_id = f"custom_{len(config['modes']['custom']) + 1}"
    config['modes']['custom'][mode_id] = {
        'title': mode_data['title'],
        'icon': mode_data['icon'],
        'prompt': mode_data['prompt'],
        'order': len(config['modes']['order']) + 1,
        'page': (len(config['modes']['order']) // 3) + 1,
        'system': False
    }

    config['modes']['order'].append(mode_id)
    return save_config(config)

