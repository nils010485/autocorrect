import pytest
from unittest.mock import patch, MagicMock

from autocorrect_pro.models import (
    stream_response,
    _stream_gemini,
    _stream_openai,
    _stream_custom_openai,
    _stream_anthropic
)


class TestStreamResponse:
    """Test cases for stream_response function."""

    def test_stream_response_no_api_key(self):
        """Test stream_response when no API key is provided."""
        result = list(stream_response("traduire", "Hello world", api_key=None))
        assert result == ["Erreur: Clé API non configurée"]

    def test_stream_response_invalid_mode(self):
        """Test stream_response with invalid mode."""
        result = list(stream_response("invalid_mode", "Hello world", api_key="test_key", all_modes={}))
        assert result == ["Erreur: Mode 'invalid_mode' non reconnu."]

    def test_stream_response_mode_no_prompt(self):
        """Test stream_response when mode has no prompt."""
        result = list(stream_response("traduire", "Hello world", api_key="test_key",
                                   all_modes={"traduire": {"title": "Traduire"}}))
        assert result == ["Erreur: Prompt non défini pour le mode 'traduire'."]

    def test_stream_response_repondre_mode_no_user_response(self):
        """Test stream_response with 'repondre' mode but no user response."""
        modes = {
            "repondre": {"prompt": "Répondre à: {original_message}"}
        }
        result = list(stream_response("repondre", "Hello", api_key="test_key", all_modes=modes))
        assert result == ["Erreur: Réponse utilisateur manquante pour le mode 'répondre'."]

    @patch('autocorrect_pro.models._stream_gemini')
    def test_stream_response_gemini_success(self, mock_stream_gemini):
        """Test stream_response with Gemini model."""
        mock_stream_gemini.return_value = iter(["Translated text"])

        modes = {
            "traduire": {"prompt": "Translate: {input}"}
        }

        result = list(stream_response("traduire", "Hello world", api_key="test_key",
                                   model="gemini-1.5-flash", all_modes=modes))
        assert result == ["Translated text"]

    @patch('autocorrect_pro.models._stream_openai')
    def test_stream_response_openai_success(self, mock_stream_openai):
        """Test stream_response with OpenAI model."""
        mock_stream_openai.return_value = iter(["OpenAI response"])

        modes = {
            "traduire": {"prompt": "Translate: {input}"}
        }

        result = list(stream_response("traduire", "Hello world", api_key="test_key",
                                   model="gpt-4o-mini", all_modes=modes))
        assert result == ["OpenAI response"]

    @patch('autocorrect_pro.models._stream_anthropic')
    def test_stream_response_anthropic_success(self, mock_stream_anthropic):
        """Test stream_response with Anthropic model."""
        mock_stream_anthropic.return_value = iter(["Anthropic response"])

        modes = {
            "traduire": {"prompt": "Translate: {input}"}
        }

        result = list(stream_response("traduire", "Hello world", api_key="test_key",
                                   model="claude-3-5-haiku-latest", all_modes=modes))
        assert result == ["Anthropic response"]

    @patch('autocorrect_pro.models._stream_custom_openai')
    def test_stream_response_custom_success(self, mock_stream_custom):
        """Test stream_response with custom endpoint."""
        mock_stream_custom.return_value = iter(["Custom response"])

        modes = {
            "traduire": {"prompt": "Translate: {input}"}
        }

        with patch('autocorrect_pro.models.load_config') as mock_load_config:
            mock_load_config.return_value = {
                'custom_endpoint': {
                    'url': 'http://localhost:8000',
                    'model_name': 'custom-model'
                }
            }

            result = list(stream_response("traduire", "Hello world", api_key="test_key",
                                       model="custom", all_modes=modes))
            assert result == ["Custom response"]

    def test_stream_response_custom_incomplete_config(self):
        """Test stream_response with incomplete custom endpoint config."""
        modes = {
            "traduire": {"prompt": "Translate: {input}"}
        }

        with patch('autocorrect_pro.models.load_config') as mock_load_config:
            mock_load_config.return_value = {
                'custom_endpoint': {'url': '', 'model_name': ''}
            }

            result = list(stream_response("traduire", "Hello world", api_key="test_key",
                                       model="custom", all_modes=modes))
            assert result == ["Erreur: Configuration de l'endpoint personnalisé incomplète"]

    def test_stream_response_invalid_model(self):
        """Test stream_response with invalid model."""
        modes = {
            "traduire": {"prompt": "Translate: {input}"}
        }

        result = list(stream_response("traduire", "Hello world", api_key="test_key",
                                   model="invalid_model", all_modes=modes))
        assert result == ["Erreur: Modèle 'invalid_model' non reconnu."]

    def test_stream_response_exception_handling(self):
        """Test stream_response exception handling."""
        modes = {
            "traduire": {"prompt": "Translate: {input}"}
        }

        with patch('autocorrect_pro.models._stream_gemini', side_effect=Exception("API Error")):
            result = list(stream_response("traduire", "Hello world", api_key="test_key",
                                       model="gemini-1.5-flash", all_modes=modes))
            assert result == ["Erreur AI: API Error"]

    def test_stream_response_repondre_mode_with_user_response(self):
        """Test stream_response with 'repondre' mode and user response."""
        modes = {
            "repondre": {"prompt": "Original: {original_message}\nResponse: {user_response}"}
        }

        with patch('autocorrect_pro.models._stream_gemini') as mock_stream:
            mock_stream.return_value = iter(["Generated response"])

            result = list(stream_response("repondre", "Hello", api_key="test_key",
                                       user_response="Hi there", all_modes=modes))
            assert result == ["Generated response"]


class TestStreamGemini:
    """Test cases for _stream_gemini function."""

    @patch('autocorrect_pro.models.genai')
    def test_stream_gemini_success(self, mock_genai):
        """
        Test successful Gemini streaming response.

        This test verifies that the _stream_gemini function correctly handles
        a successful streaming response from the Gemini API, including proper
        model configuration and response processing.
        """
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_chunk = MagicMock()
        mock_chunk.text = "Gemini response"
        mock_response.__iter__ = MagicMock(return_value=iter([mock_chunk]))
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = list(_stream_gemini("Test prompt", "test_api_key"))
        assert result == ["Gemini response"]

        mock_genai.configure.assert_called_once_with(api_key="test_api_key")
        mock_genai.GenerativeModel.assert_called_once_with('gemini-2.5-flash')

    @patch('autocorrect_pro.models.genai')
    def test_stream_gemini_empty_chunk(self, mock_genai):
        """Test Gemini streaming with empty chunk."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_chunk = MagicMock()
        mock_chunk.text = None
        mock_response.__iter__ = MagicMock(return_value=iter([mock_chunk]))
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = list(_stream_gemini("Test prompt", "test_api_key"))
        assert result == []

    @patch('autocorrect_pro.models.genai')
    def test_stream_gemini_exception(self, mock_genai):
        """Test Gemini streaming exception handling."""
        mock_genai.GenerativeModel.side_effect = Exception("Gemini Error")

        with pytest.raises(Exception):
            list(_stream_gemini("Test prompt", "test_api_key"))


class TestStreamOpenAI:
    """Test cases for _stream_openai function."""

    @patch('autocorrect_pro.models.OpenAI')
    def test_stream_openai_success(self, mock_openai_class):
        """
        Test successful OpenAI streaming response.

        This test verifies that the _stream_openai function correctly handles
        a successful streaming response from the OpenAI API, including proper
        client configuration and response processing.
        """
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "OpenAI response"
        mock_response.__iter__ = MagicMock(return_value=iter([mock_chunk]))
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        result = list(_stream_openai("Test prompt", "test_api_key", "gpt-4"))
        assert result == ["OpenAI response"]

        mock_openai_class.assert_called_once_with(api_key="test_api_key")
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            temperature=0,
            messages=[{"role": "user", "content": "Test prompt"}],
            stream=True
        )

    @patch('autocorrect_pro.models.OpenAI')
    def test_stream_openai_empty_delta(self, mock_openai_class):
        """Test OpenAI streaming with empty delta content."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = None
        mock_response.__iter__ = MagicMock(return_value=iter([mock_chunk]))
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        result = list(_stream_openai("Test prompt", "test_api_key", "gpt-4"))
        assert result == []

    @patch('autocorrect_pro.models.OpenAI')
    def test_stream_openai_exception(self, mock_openai_class):
        """Test OpenAI streaming exception handling."""
        mock_openai_class.side_effect = Exception("OpenAI Error")

        with pytest.raises(Exception):
            list(_stream_openai("Test prompt", "test_api_key", "gpt-4"))


class TestStreamCustomOpenAI:
    """Test cases for _stream_custom_openai function."""

    @patch('autocorrect_pro.models.OpenAI')
    def test_stream_custom_openai_success(self, mock_openai_class):
        """
        Test successful custom OpenAI endpoint streaming response.

        This test verifies that the _stream_custom_openai function correctly handles
        a successful streaming response from a custom OpenAI-compatible endpoint,
        including proper client configuration with custom base URL and response processing.
        """
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "Custom response"
        mock_response.__iter__ = MagicMock(return_value=iter([mock_chunk]))
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        result = list(_stream_custom_openai("Test prompt", "test_api_key",
                                           "custom-model", "http://localhost:8000"))
        assert result == ["Custom response"]

        mock_openai_class.assert_called_once_with(
            api_key="test_api_key",
            base_url="http://localhost:8000"
        )
        mock_client.chat.completions.create.assert_called_once_with(
            model="custom-model",
            temperature=0,
            messages=[{"role": "user", "content": "Test prompt"}],
            stream=True
        )


class TestStreamAnthropic:
    """Test cases for _stream_anthropic function."""

    @patch('autocorrect_pro.models.anthropic')
    def test_stream_anthropic_success(self, mock_anthropic):
        """
        Test successful Anthropic streaming response.

        This test verifies that the _stream_anthropic function correctly handles
        a successful streaming response from the Anthropic API, including proper
        client configuration and response processing using the text stream.
        """
        mock_client = MagicMock()
        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=None)
        mock_stream.text_stream = iter(["Anthropic response"])
        mock_client.messages.stream.return_value = mock_stream
        mock_anthropic.Anthropic.return_value = mock_client

        result = list(_stream_anthropic("Test prompt", "test_api_key", "claude-3-5-sonnet"))
        assert result == ["Anthropic response"]

        mock_anthropic.Anthropic.assert_called_once_with(api_key="test_api_key")
        mock_client.messages.stream.assert_called_once_with(
            max_tokens=4096,
            temperature=0,
            messages=[{"role": "user", "content": "Test prompt"}],
            model="claude-3-5-sonnet",
        )

    @patch('autocorrect_pro.models.anthropic')
    def test_stream_anthropic_empty_stream(self, mock_anthropic):
        """Test Anthropic streaming with empty stream."""
        mock_client = MagicMock()
        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=None)
        mock_stream.text_stream = iter([])
        mock_client.messages.stream.return_value = mock_stream
        mock_anthropic.Anthropic.return_value = mock_client

        result = list(_stream_anthropic("Test prompt", "test_api_key", "claude-3-5-sonnet"))
        assert result == []

    @patch('autocorrect_pro.models.anthropic')
    def test_stream_anthropic_exception(self, mock_anthropic):
        """Test Anthropic streaming exception handling."""
        mock_anthropic.Anthropic.side_effect = Exception("Anthropic Error")

        with pytest.raises(Exception):
            list(_stream_anthropic("Test prompt", "test_api_key", "claude-3-5-sonnet"))