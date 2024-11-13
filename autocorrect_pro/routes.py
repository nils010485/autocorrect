from flask import Blueprint, render_template, request, jsonify, Response
import pyperclip
from .config import PROMPTS, AVAILABLE_MODELS, CURRENT_VERSION, DEFAULT_SHORTCUT, CONFIG_FILE
from .utils import load_config, save_config, restart_application
from .models import stream_response

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Page principale de l'application."""
    config = load_config()
    if config.get('last_version', 1) < CURRENT_VERSION:
        save_config(config.get('api_key'), config.get('model'),
                    config.get('theme'), CURRENT_VERSION)
        return render_template('whatsnew.html', current_version=CURRENT_VERSION)

    if not config.get('api_key'):
        return render_template('wizzard.html',
                               models={k: v["name"] for k, v in AVAILABLE_MODELS.items()})

    return render_template('index.html',
                           prompts=PROMPTS,
                           models={k: v["name"] for k, v in AVAILABLE_MODELS.items()},
                           current_model=config.get('model'),
                           current_theme=config.get('theme', 'light'),
                           has_api_key=bool(config.get('api_key')))


@bp.route('/process', methods=['POST'])
def process():
    """Traite les requêtes de génération de texte."""
    mode = request.form.get('mode')
    input_text = request.form.get('input_text')
    user_response = request.form.get('user_response') if mode == 'repondre' else None
    config = load_config()

    def generate():
        try:
            buffer = ""
            for chunk in stream_response(mode, input_text, user_response,
                                         config.get('model'), config.get('api_key')):
                if chunk:
                    clean_chunk = chunk.replace('\r', '').replace('\n', ' ')
                    buffer += clean_chunk
                    yield f"data: {buffer}\n\n"

            if buffer:
                yield f"data: {buffer}\n\n"
            yield "data: [END]\n\n"

        except Exception as e:
            yield f"data: Erreur: {str(e)}\n\n"
            yield "data: [END]\n\n"

    return Response(generate(), mimetype='text/event-stream')


@bp.route('/copy', methods=['POST'])
def copy():
    """Copie le texte dans le presse-papiers."""
    data = request.json
    text = data.get('text', '')
    try:
        pyperclip.copy(text)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@bp.route('/api/config', methods=['GET'])
def get_config():
    """Récupère la configuration actuelle."""
    config = load_config()
    return jsonify({
        'has_key': bool(config.get('api_key')),
        'api_key': config.get('api_key'),
        'model': config.get('model'),
        'theme': config.get('theme', 'light'),
        'shortcut': config.get('shortcut', DEFAULT_SHORTCUT)
    })


@bp.route('/api/config', methods=['POST'])
def set_config():
    """Configure l'API key, le modèle, le thème et le raccourci."""
    data = request.json
    api_key = data.get('api_key', '').strip()
    model = data.get('model', 'gemini-1.5-flash')
    theme = data.get('theme', 'light')
    new_shortcut = data.get('shortcut', DEFAULT_SHORTCUT)

    current_config = load_config()
    current_shortcut = current_config.get('shortcut', DEFAULT_SHORTCUT)

    if not api_key:
        try:
            if CONFIG_FILE.exists():
                CONFIG_FILE.unlink()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erreur lors de la suppression: {str(e)}'
            }), 500

    if not model:
        return jsonify({
            'success': False,
            'error': 'Configuration incomplète'
        }), 400

    if save_config(api_key, model, theme, CURRENT_VERSION, new_shortcut):
        if new_shortcut != current_shortcut:
            restart_application()
        return jsonify({'success': True})

    return jsonify({
        'success': False,
        'error': 'Erreur lors de la sauvegarde de la configuration'
    }), 500
