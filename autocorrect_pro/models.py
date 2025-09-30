from typing import Generator, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import anthropic
from openai import OpenAI
from .config import AVAILABLE_MODELS
from .utils import load_config

def stream_response(mode_name: str, input_text: str, user_response: Optional[str] = None,
                    model: str = "gemini-1.5-flash", api_key: Optional[str] = None,
                    all_modes: dict = None) -> Generator[str, None, None]:
    """
    Generate streaming response based on configured model.

    Args:
        mode_name: Name of the processing mode
        input_text: Text to process
        user_response: User response for reply mode
        model: AI model to use
        api_key: API key for authentication
        all_modes: Dictionary containing all available modes

    Yields:
        str: Streamed response text
    """

    if not api_key:
        yield "Erreur: Clé API non configurée"
        return

    config = load_config()

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
        elif model_config["provider"] == "custom":
            custom_endpoint = config.get('custom_endpoint', {})
            if not custom_endpoint.get('url') or not custom_endpoint.get('model_name'):
                yield "Erreur: Configuration de l'endpoint personnalisé incomplète"
                return

            endpoint_style = custom_endpoint.get('style', 'openai')
            if endpoint_style == 'anthropic':
                yield from _stream_custom_anthropic(
                    full_prompt,
                    api_key,
                    custom_endpoint['model_name'],
                    custom_endpoint['url']
                )
            else:
                yield from _stream_custom_openai(
                    full_prompt,
                    api_key,
                    custom_endpoint['model_name'],
                    custom_endpoint['url']
                )
        else:
            yield f"Erreur: Fournisseur non supporté pour le modèle {model}"

    except Exception as e:
        yield f"Erreur AI: {str(e)}"

def _stream_gemini(prompt: str, api_key: str) -> Generator[str, None, None]:
    """
    Handles streaming responses from Gemini AI models.

    Configures the Gemini API client with appropriate safety settings
    and streams the response text chunk by chunk.

    Args:
        prompt: Text prompt to send to the model
        api_key: API key for authentication

    Yields:
        str: Streamed response text chunks
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
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
    """
    Handles streaming responses from OpenAI models.

    Creates an OpenAI client and streams the response using their
    chat completions API with streaming enabled.

    Args:
        prompt: Text prompt to send to the model
        api_key: API key for authentication
        model_name: Specific model name to use

    Yields:
        str: Streamed response text chunks
    """
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model_name,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

def _stream_custom_openai(prompt: str, api_key: str, model_name: str, base_url: str) -> Generator[str, None, None]:
    """
    Handles streaming responses from custom OpenAI-compatible models.

    Creates an OpenAI client with a custom base URL for models that
    follow the OpenAI API format but are hosted elsewhere.

    Args:
        prompt: Text prompt to send to the model
        api_key: API key for authentication
        model_name: Specific model name to use
        base_url: Custom API endpoint URL

    Yields:
        str: Streamed response text chunks
    """
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model_name,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

def _stream_custom_anthropic(prompt: str, api_key: str, model_name: str, base_url: str) -> Generator[str, None, None]:
    """
    Handles streaming responses from custom Anthropic-compatible models.

    Creates an Anthropic client with a custom base URL for models that
    follow the Anthropic API format but are hosted elsewhere.

    Args:
        prompt: Text prompt to send to the model
        api_key: API key for authentication
        model_name: Specific model name to use
        base_url: Custom API endpoint URL

    Yields:
        str: Streamed response text chunks
    """
    try:
        client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
        with client.messages.stream(
            max_tokens=4096,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
            model=model_name,
        ) as stream:
            for text in stream.text_stream:
                yield text
    except Exception as e:
        yield str(e)

def _stream_anthropic(prompt: str, api_key: str, model_name: str) -> Generator[str, None, None]:
    """
    Handles streaming responses from Anthropic models.

    Creates an Anthropic client and uses their streaming API to get
    real-time response chunks from Claude models.

    Args:
        prompt: Text prompt to send to the model
        api_key: API key for authentication
        model_name: Specific model name to use

    Yields:
        str: Streamed response text chunks
    """
    client = anthropic.Anthropic(api_key=api_key)
    with client.messages.stream(
            max_tokens=4096,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
            model=model_name,
    ) as stream:
        for text in stream.text_stream:
            yield text
