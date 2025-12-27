import json
import logging
import os
import tempfile

from flask import Blueprint, render_template, request, jsonify, Response
import pyperclip
from openai import OpenAI

from .config import MODES, AVAILABLE_MODELS, CURRENT_VERSION, DEFAULT_SHORTCUT, CONFIG_FILE, AVAILABLE_THEMES
from .utils import load_config, save_config, restart_application, load_modes
from .models import stream_response
from .utils import validate_audio_file
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)


@bp.route('/')
def index() -> str:
    """
    Main page of the application.

    Renders the main interface with processing modes, handles version updates,
    and processes text input from URL parameters.
    """

    text_from_url = request.args.get('text', '')
    if text_from_url and text_from_url.startswith("b'") and text_from_url.endswith("'"):
        text_from_url = text_from_url[2:-1].strip()

    config = load_config()

    if config.get('last_version', 1) < CURRENT_VERSION:
        save_config(api_key=config.get('api_key'), model=config.get('model'),
                    theme=config.get('theme'), last_version=CURRENT_VERSION)
        return render_template('whatsnew.html', current_version=CURRENT_VERSION, current_theme=config.get('theme', 'light'))

    if not config.get('api_key'):
        return render_template('wizzard.html',
                               models=AVAILABLE_MODELS)

    modes_config = load_modes()
    ordered_modes = {}

    for mode_id in modes_config.get('order', []):
        if mode_id in modes_config['system']:
            ordered_modes[mode_id] = modes_config['system'][mode_id]
        elif mode_id in modes_config.get('custom', {}):
            ordered_modes[mode_id] = modes_config['custom'][mode_id]

    return render_template('index.html',
                           modes=ordered_modes,
                           models=AVAILABLE_MODELS,
                           current_model=config.get('model'),
                           current_theme=config.get('theme', 'light'),
                           has_api_key=bool(config.get('api_key')),
                           text_from_url=text_from_url)

@bp.route('/settings')
def settings_page() -> str:
    """
    Settings page of the application.

    Renders the settings interface for configuring API keys, models,
    themes, and application preferences.
    """
    config = load_config()
    if not config.get('api_key'):
        return render_template('wizzard.html',
                               models=AVAILABLE_MODELS)

    return render_template('settings.html',
                           models=AVAILABLE_MODELS,
                           current_model=config.get('model'),
                           current_shortcut=config.get('shortcut', DEFAULT_SHORTCUT),
                           current_theme=config.get('theme', 'light'),
                           available_themes=AVAILABLE_THEMES)

@bp.route('/restart', methods=['GET'])
def restart_endpoint() -> None:
    """
    Restarts the application.

    Triggers application restart to apply configuration changes.
    """
    restart_application()

@bp.route('/process', methods=['POST'])
def process() -> Response:
    """
    Processes text generation requests.

    Handles AI text processing requests by streaming responses from
    configured AI models based on the selected processing mode.
    """
    mode = request.form.get('mode')
    input_text = request.form.get('input_text')

    user_response = request.form.get('user_response') if mode == 'repondre' else None
    config = load_config()

    modes_config = load_modes()
    all_modes = {**modes_config['system'], **modes_config.get('custom', {})}

    if mode not in all_modes:
        return jsonify({'error': f"Mode '{mode}' non reconnu."}), 400

    def generate():
        """
        Generate streaming response for the text processing request.

        This generator function streams AI model responses back to the client
        in real-time using Server-Sent Events (SSE) format.
        """
        buffer = ""
        try:
            for chunk in stream_response(mode, input_text, user_response,
                                         config.get('model'), config.get('api_key'), all_modes=all_modes):
                if chunk:
                    clean_chunk = chunk.replace('\r', '')
                    buffer += clean_chunk
                    yield f"data: {json.dumps(buffer)}\n\n"

            yield "data: [END]\n\n"

        except Exception as e:
            error_msg = json.dumps(f"Erreur: {str(e)}")
            yield f"data: {error_msg}\n\n"
            yield "data: [END]\n\n"

    return Response(generate(), mimetype='text/event-stream')




@bp.route('/copy', methods=['POST'])
def copy() -> Response:
    """
    Copies text to clipboard.

    Extracts plain text from HTML content if provided and copies
    the cleaned text to the system clipboard.
    """
    data = request.json
    html_or_plain_text = data.get('text', '')

    try:
        soup = BeautifulSoup(html_or_plain_text, 'html.parser')
        plain_text = soup.get_text().strip()

        pyperclip.copy(plain_text)
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@bp.route('/transcribe', methods=['POST'])
def transcribe() -> Response:
    """
    Transcribes audio file to text using OpenAI Whisper.

    Processes uploaded audio files and returns transcribed text
    using OpenAI's Whisper API for speech recognition.
    """
    temp_file = None
    try:
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucun fichier audio fourni.'
            }), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Aucun fichier sélectionné.'
            }), 400

        config = load_config()

        if not config.get('api_key') or AVAILABLE_MODELS.get(config.get('model', '')).get('provider') != 'openai':
            return jsonify({
                'success': False,
                'error': 'Une clé API OpenAI est requise pour la transcription audio.'
            }), 400

        temp_file = tempfile.NamedTemporaryFile(suffix=os.path.splitext(audio_file.filename)[1], delete=False)
        audio_file.save(temp_file.name)

        is_valid, error_message = validate_audio_file(temp_file.name)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message
            }), 400

        try:
            client = OpenAI(api_key=config.get('api_key'))
            with open(temp_file.name, "rb") as audio:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="text"
                )

        except Exception:
            return jsonify({
                'success': False,
                'error': "Erreur lors de la transcription, essayez un autre format."
            }), 500

        return jsonify({
            'success': True,
            'text': transcription
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Erreur inattendue: {str(e)}"
        }), 500
    finally:
        if temp_file:
            temp_file.close()
            try:
                os.unlink(temp_file.name)
            except OSError:
                pass


@bp.route('/api/config', methods=['GET'])
def get_config() -> Response:
    """
    Retrieves the current configuration.

    Returns the current application configuration including API keys,
    model settings, theme preferences, and custom endpoint configuration.
    """
    config = load_config()
    custom_endpoint = config.get('custom_endpoint', {
        'url': '',
        'model_name': ''
    })
    return jsonify({
        'has_key': bool(config.get('api_key')),
        'api_key': config.get('api_key'),
        'model': config.get('model'),
        'theme': config.get('theme', 'light'),
        'shortcut': config.get('shortcut', DEFAULT_SHORTCUT),
        'custom_endpoint': custom_endpoint
    })

@bp.errorhandler(500)
def internal_server_error(error: Exception) -> tuple[str, int]:
    """
    Handles 500 Internal Server Error exceptions.

    Displays a custom error page when server errors occur.
    """
    return render_template('500.html'), 500


@bp.route('/api/config', methods=['POST'])
def set_config() -> Response:
    """
    Configures API key, model, theme, and shortcut settings.

    Updates application configuration and triggers restart if shortcut
    settings are changed.
    """
    data = request.json
    api_key = data.get('api_key', '').strip()
    model = data.get('model', 'gemini-1.5-flash')
    theme = data.get('theme', 'light')
    new_shortcut = data.get('shortcut', DEFAULT_SHORTCUT)

    custom_endpoint = {
        'url': data.get('custom_endpoint_url', '').strip(),
        'model_name': data.get('custom_endpoint_model', '').strip(),
        'style': data.get('custom_endpoint_style', 'openai').strip()
    }

    current_config = load_config()
    current_shortcut = current_config.get('shortcut', DEFAULT_SHORTCUT)

    if not api_key:
        try:
            if CONFIG_FILE.exists():
                CONFIG_FILE.unlink()
            restart_application()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error during deletion: {str(e)}'
            }), 500

    if save_config(
            api_key=api_key,
            model=model,
            theme=theme,
            last_version=CURRENT_VERSION,
            shortcut=new_shortcut,
            custom_endpoint=custom_endpoint

    ):
        if new_shortcut != current_shortcut:
            restart_application()
        return jsonify({'success': True})

    return jsonify({
        'success': False,
        'error': 'Error during configuration save'
    }), 500


@bp.route('/edit-order', methods=['GET'])
def edit_order_page() -> str:
    """
    Mode ordering edit page.

    Renders the interface for customizing the order of processing modes.
    """
    config = load_config()
    return render_template('edit_order.html',
                           current_theme=config.get('theme', 'light'))


@bp.route('/whatsnew')
def whatsnew_page() -> str:
    """
    What's new page.

    Displays information about recent updates and new features.
    """
    config = load_config()
    return render_template('whatsnew.html',
                           current_version=CURRENT_VERSION,
                           current_theme=config.get('theme', 'light'))


@bp.route('/api/modes', methods=['GET', 'POST', 'PUT'])
def manage_modes() -> Response:
    """
    API for managing custom modes.

    Handles CRUD operations for custom processing modes.
    """
    if request.method == 'GET':
        return jsonify(load_modes())
    elif request.method == 'POST':
        return create_custom_mode(request.json)
    elif request.method == 'PUT':
        return update_modes_order(request.json)


def create_custom_mode(data: dict) -> Response:
    """
    Creates a new custom mode and updates the configuration.

    Validates input data, generates a unique mode ID, and saves
    the new custom mode to the configuration.
    """
    try:
        config = load_config()

        if 'modes' not in config:
            config['modes'] = {'system': MODES, 'custom': {}, 'order': []}

        if 'custom' not in config['modes']:
            config['modes']['custom'] = {}

        mode_id = f"custom_{len(config['modes']['custom']) + 1}"

        new_mode = {
            'title': data.get('title'),
            'icon': data.get('icon'),
            'prompt': data.get('prompt'),
            'system': False
        }

        config['modes']['custom'][mode_id] = new_mode
        config['modes']['order'].append(mode_id)

        if save_config(modes=config['modes']):
            return jsonify({'success': True, 'mode_id': mode_id})
        else:
            raise Exception("Failed to save the configuration")

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error creating custom mode: {str(e)}'
        }), 500


def update_modes_order(data: dict) -> Response:
    """
    Updates the order of modes.

    Validates the new order and updates the configuration to
    reflect the new sequence of processing modes.
    """
    try:
        new_order = data.get('order', [])
        if not new_order:
            raise ValueError("New order not specified")

        config = load_config()
        modes = config.get('modes', {})

        all_modes = {**MODES, **modes.get('custom', {})}
        missing_modes = [mode_id for mode_id in new_order if mode_id not in all_modes]
        if missing_modes:
            raise ValueError(f"Unknown modes: {', '.join(missing_modes)}")

        modes['order'] = new_order

        if save_config(modes=modes):
            return jsonify({'success': True})
        else:
            raise Exception("Error during save")

    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': f'Validation error: {str(ve)}'
        }), 400
    except Exception as e:
        logger.error(f"Error during order update: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error during order update: {str(e)}'
        }), 500


@bp.route('/api/modes/<mode_id>', methods=['DELETE'])
def delete_mode(mode_id: str) -> Response:
    """
    Deletes a custom mode.

    Removes a custom mode from the configuration and updates
    the mode order accordingly.
    """
    try:
        config = load_config()
        modes = config.get('modes', {})

        if mode_id not in modes.get('custom', {}):
            raise ValueError("Mode not found or cannot be deleted")

        del modes['custom'][mode_id]

        if 'order' in modes:
            modes['order'] = [m for m in modes['order'] if m != mode_id]

        if save_config(modes=modes):
            return jsonify({'success': True})
        else:
            raise Exception("Error during save")

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/api/modes/<mode_id>', methods=['PATCH'])
def update_mode(mode_id: str) -> Response:
    """
    Updates a custom mode.

    Modifies the prompt of an existing custom mode and saves
    the changes to the configuration.
    """
    try:
        data = request.json
        config = load_config()
        modes = config.get('modes', {})

        if mode_id not in modes.get('custom', {}):
            raise ValueError("Mode not found or cannot be modified")

        if 'prompt' in data:
            modes['custom'][mode_id]['prompt'] = data['prompt']

        if save_config(modes=modes):
            return jsonify({'success': True})
        else:
            raise Exception("Error during save")

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
