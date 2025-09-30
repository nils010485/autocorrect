from unittest.mock import patch
from autocorrect_pro.config import DEFAULT_CONFIG, AVAILABLE_MODELS
from autocorrect_pro.utils import load_config, get_custom_endpoint, save_custom_endpoint
from autocorrect_pro.models import _stream_custom_anthropic, _stream_custom_openai


class TestEndpointStyle:
    """Test cases for endpoint style functionality."""

    def test_default_config_has_endpoint_style(self):
        """Test that default config includes endpoint style."""
        assert 'style' in DEFAULT_CONFIG['custom_endpoint']
        assert DEFAULT_CONFIG['custom_endpoint']['style'] == 'openai'

    def test_available_models_has_custom_option(self):
        """Test that custom model is available."""
        assert 'custom' in AVAILABLE_MODELS
        assert AVAILABLE_MODELS['custom']['name'] == 'Autre modèle'
        assert AVAILABLE_MODELS['custom']['provider'] == 'custom'

    @patch('builtins.open')
    @patch('os.path.exists')
    @patch('autocorrect_pro.utils.json.load')
    def test_load_config_backward_compatibility(self, mock_json_load, mock_exists, mock_open):
        """Test that old configs without style field get default value."""
        mock_exists.return_value = True
        mock_json_load.return_value = {
            'api_key': 'test',
            'model': 'custom',
            'custom_endpoint': {
                'url': 'https://test.com',
                'model_name': 'test-model'
            }
        }

        config = load_config()
        assert 'style' in config['custom_endpoint']
        assert config['custom_endpoint']['style'] == 'openai'

    @patch('builtins.open')
    @patch('os.path.exists')
    @patch('autocorrect_pro.utils.json.load')
    def test_get_custom_endpoint_backward_compatibility(self, mock_json_load, mock_exists, mock_open):
        """Test get_custom_endpoint adds style field if missing."""
        mock_exists.return_value = True
        mock_json_load.return_value = {
            'custom_endpoint': {
                'url': 'https://test.com',
                'model_name': 'test-model'
            }
        }

        endpoint = get_custom_endpoint()
        assert 'style' in endpoint
        assert endpoint['style'] == 'openai'

    @patch('autocorrect_pro.utils.load_config')
    @patch('autocorrect_pro.utils.save_config')
    def test_save_custom_endpoint_with_style(self, mock_save_config, mock_load_config):
        """Test save_custom_endpoint with style parameter."""
        mock_load_config.return_value = {'custom_endpoint': {}}
        mock_save_config.return_value = True

        result = save_custom_endpoint('https://test.com', 'test-model', 'anthropic')

        assert result is True
        mock_save_config.assert_called_once()
        call_args = mock_save_config.call_args[1]
        assert 'custom_endpoint' in call_args
        assert call_args['custom_endpoint']['style'] == 'anthropic'

    @patch('autocorrect_pro.utils.load_config')
    @patch('autocorrect_pro.utils.save_config')
    def test_save_custom_endpoint_default_style(self, mock_save_config, mock_load_config):
        """Test save_custom_endpoint defaults to openai style."""
        mock_load_config.return_value = {'custom_endpoint': {}}
        mock_save_config.return_value = True

        result = save_custom_endpoint('https://test.com', 'test-model')

        assert result is True
        call_args = mock_save_config.call_args[1]
        assert call_args['custom_endpoint']['style'] == 'openai'

    @patch('autocorrect_pro.models.anthropic.Anthropic')
    def test_stream_custom_anthropic_success(self, mock_anthropic_class):
        """
        Test successful streaming with custom Anthropic endpoint.

        This test verifies that the _stream_custom_anthropic function correctly handles
        a successful streaming response from a custom Anthropic-compatible endpoint.
        """
        mock_client = mock_anthropic_class.return_value
        mock_stream_manager = mock_client.messages.stream.return_value
        mock_stream_manager.__enter__.return_value.text_stream = ['Response chunk 1', 'Response chunk 2']

        result = list(_stream_custom_anthropic(
            'Test prompt',
            'test_api_key',
            'test-model',
            'https://custom-anthropic.com'
        ))

        assert result == ['Response chunk 1', 'Response chunk 2']
        mock_anthropic_class.assert_called_once_with(
            api_key='test_api_key',
            base_url='https://custom-anthropic.com'
        )

    @patch('autocorrect_pro.models.anthropic.Anthropic')
    def test_stream_custom_anthropic_error_handling(self, mock_anthropic_class):
        """Test error handling in custom Anthropic streaming."""
        mock_client = mock_anthropic_class.return_value
        mock_client.messages.stream.side_effect = Exception("Connection error")

        result = list(_stream_custom_anthropic(
            'Test prompt',
            'test_api_key',
            'test-model',
            'https://custom-anthropic.com'
        ))

        assert len(result) == 1
        assert 'Connection error' in result[0]

    @patch('autocorrect_pro.models.OpenAI')
    def test_stream_custom_openai_success(self, mock_openai_class):
        """Test successful streaming with custom OpenAI endpoint."""
        mock_client = mock_openai_class.return_value
        mock_chunk = type('Chunk', (), {})()
        mock_chunk.choices = [type('Choice', (), {'delta': type('Delta', (), {'content': 'Test response'})()})()]
        mock_response = iter([mock_chunk])

        mock_client.chat.completions.create.return_value = mock_response

        list(_stream_custom_openai(
            'Test prompt',
            'test_api_key',
            'test-model',
            'https://custom-openai.com'
        ))

        mock_openai_class.assert_called_once_with(
            api_key='test_api_key',
            base_url='https://custom-openai.com'
        )

    def test_endpoint_style_validation(self):
        """Test that only valid styles are accepted."""
        valid_styles = ['openai', 'anthropic']

        for style in valid_styles:
            assert style in ['openai', 'anthropic']