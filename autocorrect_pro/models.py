from typing import Generator, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import anthropic
from openai import OpenAI
from .config import MODES, AVAILABLE_MODELS

def stream_response(mode_name: str, input_text: str, user_response: Optional[str] = None,
                    model: str = "gemini-1.5-flash", api_key: Optional[str] = None,
                    all_modes: dict = None) -> Generator[str, None, None]:
    """Génère la réponse en streaming selon le modèle configuré."""

    if not api_key:
        yield "Erreur: Clé API non configurée"
        return

    # Utiliser all_modes au lieu de MODES
    mode_config = all_modes.get(mode_name)
    if not mode_config:
        yield f"Erreur: Mode '{mode_name}' non reconnu."
        return

    prompt_text = mode_config.get('prompt')
    if not prompt_text:
        yield f"Erreur: Prompt non défini pour le mode '{mode_name}'."
        return

    if mode_name == "repondre":
        if user_response is None:
            yield "Erreur: Réponse utilisateur manquante pour le mode 'répondre'."
            return
        full_prompt = prompt_text.format(original_message=input_text, user_response=user_response)
    else:
        full_prompt = f"{prompt_text}\n\n{input_text}"

    try:
        model_config = AVAILABLE_MODELS.get(model)
        if not model_config:
            yield f"Erreur: Modèle '{model}' non reconnu."
            return

        if model_config["provider"] == "google":
            yield from _stream_gemini(full_prompt, api_key)
        elif model_config["provider"] == "openai":
            yield from _stream_openai(full_prompt, api_key, model_config["model_name"])
        elif model_config["provider"] == "anthropic":
            yield from _stream_anthropic(full_prompt, api_key, model_config["model_name"])
        else:
            yield f"Erreur: Fournisseur non supporté pour le modèle {model}"

    except Exception as e:
        yield f"Erreur AI: {str(e)}"

def _stream_gemini(prompt: str, api_key: str) -> Generator[str, None, None]:
    """Gère le streaming pour les modèles Gemini."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    response = model.generate_content(prompt, safety_settings=safety_settings, stream=True)
    for chunk in response:
        if chunk.text:
            yield chunk.text

def _stream_openai(prompt: str, api_key: str, model_name: str) -> Generator[str, None, None]:
    """Gère le streaming pour les modèles OpenAI."""
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

def _stream_anthropic(prompt: str, api_key: str, model_name: str) -> Generator[str, None, None]:
    """Gère le streaming pour les modèles Anthropic."""
    client = anthropic.Anthropic(api_key=api_key)
    with client.messages.stream(
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            model=model_name,
    ) as stream:
        for text in stream.text_stream:
            yield text
