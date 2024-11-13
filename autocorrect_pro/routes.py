from flask import Blueprint, render_template, request, jsonify, Response
import pyperclip
from .config import MODES, AVAILABLE_MODELS, CURRENT_VERSION, DEFAULT_SHORTCUT, CONFIG_FILE
from .utils import load_config, save_config, restart_application, load_modes
from .models import stream_response

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Page principale de l'application."""
    config = load_config()

    # Vérifier si une mise à jour de la version est nécessaire
    if config.get('last_version', 1) < CURRENT_VERSION:
        save_config(api_key=config.get('api_key'), model=config.get('model'),
                    theme=config.get('theme'), last_version=CURRENT_VERSION)
        return render_template('whatsnew.html', current_version=CURRENT_VERSION)

    # Vérifier si la clé API est présente
    if not config.get('api_key'):
        return render_template('wizzard.html',
                               models={k: v["name"] for k, v in AVAILABLE_MODELS.items()})

    # Charger les modes avec leur ordre personnalisé
    modes_config = load_modes()
    ordered_modes = {}

    # Construire les modes dans l'ordre correct
    for mode_id in modes_config.get('order', []):
        if mode_id in modes_config['system']:
            ordered_modes[mode_id] = modes_config['system'][mode_id]
        elif mode_id in modes_config.get('custom', {}):
            ordered_modes[mode_id] = modes_config['custom'][mode_id]
    return render_template('index.html',
                           modes=ordered_modes,  # Passer un dictionnaire
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

    # Charger tous les modes (système et personnalisés)
    modes_config = load_modes()
    all_modes = {**modes_config['system'], **modes_config.get('custom', {})}

    # Vérifier si le mode est reconnu
    if mode not in all_modes:
        return jsonify({'error': f"Mode '{mode}' non reconnu."}), 400

    def generate():
        try:
            buffer = ""
            for chunk in stream_response(mode, input_text, user_response,
                                         config.get('model'), config.get('api_key'), all_modes=all_modes):
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


@bp.route('/custom-mode', methods=['GET'])
def custom_mode_page():
    """Page de création de mode personnalisé."""
    config = load_config()
    return render_template('custom_mode.html',
                         current_theme=config.get('theme', 'light'))


@bp.route('/edit-order', methods=['GET'])
def edit_order_page():
    """Page d'édition de l'ordre des modes."""
    config = load_config()
    return render_template('edit_order.html',
                         current_theme=config.get('theme', 'light'))


@bp.route('/api/modes', methods=['GET', 'POST', 'PUT'])
def manage_modes():
    """API pour gérer les modes personnalisés."""
    if request.method == 'GET':
        return jsonify(load_modes())
    elif request.method == 'POST':
        return create_custom_mode(request.json)
    elif request.method == 'PUT':
        return update_modes_order(request.json)


def create_custom_mode(data: dict) -> dict:
    """Creates a new custom mode and updates the configuration."""
    try:
        # Load the current configuration
        config = load_config()

        # Ensure the 'modes' key exists in the configuration
        if 'modes' not in config:
            config['modes'] = {'system': MODES, 'custom': {}, 'order': []}

        # Ensure the 'custom' dictionary exists
        if 'custom' not in config['modes']:
            config['modes']['custom'] = {}

        # Generate a unique ID for the new custom mode
        mode_id = f"custom_{len(config['modes']['custom']) + 1}"

        # Define the new custom mode
        new_mode = {
            'title': data.get('title'),
            'icon': data.get('icon'),
            'prompt': data.get('prompt'),
            'system': False
        }

        # Update the configuration with the new custom mode
        config['modes']['custom'][mode_id] = new_mode
        config['modes']['order'].append(mode_id)

        # Save the updated configuration
        if save_config(modes=config['modes']):
            return jsonify({'success': True, 'mode_id': mode_id})
        else:
            raise Exception("Failed to save the configuration")

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error creating custom mode: {str(e)}'
        }), 500


def update_modes_order(data: dict) -> dict:
    """Met à jour l'ordre des modes."""
    try:
        new_order = data.get('order', [])
        if not new_order:
            raise ValueError("Nouvel ordre non spécifié")

        config = load_config()
        modes = config.get('modes', {})

        # Vérifier que tous les modes existent
        all_modes = {**MODES, **modes.get('custom', {})}  # Utiliser MODES pour les modes par défaut
        missing_modes = [mode_id for mode_id in new_order if mode_id not in all_modes]
        if missing_modes:
            raise ValueError(f"Modes inconnus: {', '.join(missing_modes)}")

        # Mettre à jour l'ordre
        modes['order'] = new_order

        # Sauvegarder la configuration
        if save_config(modes=modes):
            return jsonify({'success': True})
        else:
            raise Exception("Erreur lors de la sauvegarde")

    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': f'Erreur de validation: {str(ve)}'
        }), 400
    except Exception as e:
        # Log the error for debugging
        print(f"Erreur lors de la mise à jour de l'ordre: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la mise à jour de l\'ordre: {str(e)}'
        }), 500


@bp.route('/api/modes/<mode_id>', methods=['DELETE'])
def delete_mode(mode_id):
    """Supprime un mode personnalisé."""
    try:
        config = load_config()
        modes = config.get('modes', {})

        # Vérifier si le mode existe et n'est pas un mode système
        if mode_id not in modes.get('custom', {}):
            raise ValueError("Mode non trouvé ou non supprimable")

        # Supprimer le mode
        del modes['custom'][mode_id]

        # Mettre à jour l'ordre
        if 'order' in modes:
            modes['order'] = [m for m in modes['order'] if m != mode_id]

        # Sauvegarder la configuration
        if save_config(modes=modes):
            return jsonify({'success': True})
        else:
            raise Exception("Erreur lors de la sauvegarde")

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/api/modes/<mode_id>', methods=['PATCH'])
def update_mode(mode_id):
    """Met à jour un mode personnalisé."""
    try:
        data = request.json
        config = load_config()
        modes = config.get('modes', {})

        # Vérifier si le mode existe et n'est pas un mode système
        if mode_id not in modes.get('custom', {}):
            raise ValueError("Mode non trouvé ou non modifiable")

        # Mettre à jour le prompt
        if 'prompt' in data:
            modes['custom'][mode_id]['prompt'] = data['prompt']

        # Sauvegarder la configuration
        if save_config(modes=modes):
            return jsonify({'success': True})
        else:
            raise Exception("Erreur lors de la sauvegarde")

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
