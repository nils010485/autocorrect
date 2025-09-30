import json
import logging
import socket
import sys
import os
from rich.console import Console
from .config import CONFIG_FILE, CONFIG_DIR, DEFAULT_CONFIG, CUSTOM_MODES_SCHEMA, \
    MODES

console = Console()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_audio_file(file_path: str) -> tuple[bool, str]:
    """
    Validates an audio file.

    Args:
        file_path: Path to the audio file

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    ALLOWED_EXTENSIONS = {'flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm'}
    MAX_SIZE_MB = 25

    if not os.path.exists(file_path):
        return False, "Fichier audio non trouvé."

    extension = os.path.basename(file_path).lower().split('.')[-1]
    if extension not in ALLOWED_EXTENSIONS:
        return False, f"Format de fichier non supporté. Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}"

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > MAX_SIZE_MB:
        return False, f"Le fichier est trop volumineux. Taille maximale: {MAX_SIZE_MB}MB"

    return True, ""

def find_free_port() -> int:
    """
    Finds a free port on the system.

    Returns:
        int: Available port number
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
        return port

def restart_application():
    """
    Restarts the application.

    This function restarts the current application by replacing the
    current process with a new instance using the same arguments.
    """
    console.print("[bold blue]Redémarrage de l'application pour appliquer les changements de raccourci...[/bold blue]")
    python = sys.executable
    os.execl(python, python, *sys.argv)

def ensure_config_dir() -> None:
    """
    Ensures that the configuration directory exists.

    Creates the configuration directory if it doesn't exist.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict[str, any]:
    """
    Loads configuration from the JSON file.

    Returns:
        dict[str, any]: Configuration dictionary with defaults applied
    """
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value

                if 'custom_endpoint' in config:
                    if 'style' not in config['custom_endpoint']:
                        config['custom_endpoint']['style'] = 'openai'

                return config
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de la configuration: {e}")
    return DEFAULT_CONFIG.copy()

def save_config(api_key: str | None = None, model: str | None = None, theme: str | None = None, last_version: int | None = None,
                shortcut: str | None = None, modes: dict | None = None, custom_endpoint: dict | None = None) -> bool:
    """
    Saves configuration to the JSON file.

    Args:
        api_key: API key for authentication
        model: AI model name
        theme: UI theme name
        last_version: Last version used
        shortcut: Global shortcut key
        modes: Dictionary of processing modes
        custom_endpoint: Custom API endpoint configuration

    Returns:
        bool: True if save was successful, False otherwise
    """
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
        if custom_endpoint is not None:
            config['custom_endpoint'] = custom_endpoint

        if 'custom_endpoint' not in config:
            config['custom_endpoint'] = {'url': '', 'model_name': ''}

        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
        return False

def load_api_key() -> str | None:
    """
    Loads the API key from the configuration file.

    Returns:
        str | None: API key if found, None otherwise
    """
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('api_key')
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de la clé API: {e}")
        console.print(f"[bold red]Erreur lors de la lecture de la clé API: {e}[/bold red]")
    return None

def save_api_key(api_key: str) -> bool:
    """
    Saves the API key to the configuration file.

    Args:
        api_key: API key to save

    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        ensure_config_dir()
        config = load_config()
        config['api_key'] = api_key
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la clé API: {e}")
        console.print(f"[bold red]Erreur lors de la sauvegarde de la clé API: {e}[/bold red]")
        return False

def load_modes() -> dict[str, any]:
    """
    Loads modes from the configuration.

    Returns:
        dict[str, any]: Dictionary containing system and custom modes
    """
    config = load_config()
    if 'modes' not in config:
        config['modes'] = {
            'system': MODES,
            'custom': {},
            'order': list(MODES.keys())
        }
        save_config(modes=config['modes'])
    else:
        if 'system' not in config['modes']:
            config['modes']['system'] = MODES
        else:
            for mode_id, mode_data in MODES.items():
                if mode_id not in config['modes']['system']:
                    config['modes']['system'][mode_id] = mode_data

        if 'custom' not in config['modes']:
            config['modes']['custom'] = {}

        if 'order' not in config['modes']:
            all_modes = {**config['modes']['system'], **config['modes']['custom']}
            config['modes']['order'] = list(all_modes.keys())

    return config['modes']

def save_custom_mode(mode_data: dict) -> bool:
    """
    Saves a new custom mode.

    Args:
        mode_data: Dictionary containing mode information

    Returns:
        bool: True if save was successful, False otherwise
    """
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
    return save_config(modes=config['modes'])

def get_custom_endpoint() -> dict[str, str]:
    """
    Retrieves the custom endpoint configuration.

    Returns:
        dict[str, str]: Custom endpoint configuration with url, model_name, and style
    """
    config = load_config()
    endpoint = config.get('custom_endpoint', {'url': '', 'model_name': ''})
    if 'style' not in endpoint:
        endpoint['style'] = 'openai'
    return endpoint

def save_custom_endpoint(url: str, model_name: str, style: str = 'openai') -> bool:
    """
    Saves the custom endpoint configuration.

    Args:
        url: Custom API endpoint URL
        model_name: Model name for custom endpoint
        style: Endpoint style ('openai' or 'anthropic')

    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        config = load_config()
        config['custom_endpoint'] = {
            'url': url.strip(),
            'model_name': model_name.strip(),
            'style': style.strip()
        }
        return save_config(custom_endpoint=config['custom_endpoint'])
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de l'endpoint personnalisé: {e}")
        console.print(f"[bold red]Erreur lors de la sauvegarde de l'endpoint personnalisé: {e}[/bold red]")
        return False
