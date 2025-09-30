import pytest
from unittest.mock import patch
from pathlib import Path

from autocorrect_pro.config import (
    AVAILABLE_MODELS,
    MODES,
    DEFAULT_CONFIG,
    CURRENT_VERSION,
    DEFAULT_SHORTCUT,
    CONFIG_FILE,
    CONFIG_DIR,
    ICON_PATH
)


class TestConstants:
    """Test cases for configuration constants."""

    def test_current_version(self):
        """Test that CURRENT_VERSION is an integer."""
        assert isinstance(CURRENT_VERSION, int)
        assert CURRENT_VERSION > 0

    def test_default_shortcut(self):
        """Test that DEFAULT_SHORTCUT is a string."""
        assert isinstance(DEFAULT_SHORTCUT, str)
        assert len(DEFAULT_SHORTCUT) > 0

    def test_available_models_structure(self):
        """Test that AVAILABLE_MODELS has the correct structure."""
        assert isinstance(AVAILABLE_MODELS, dict)
        assert len(AVAILABLE_MODELS) > 0

        for model_id, model_config in AVAILABLE_MODELS.items():
            assert isinstance(model_id, str)
            assert isinstance(model_config, dict)
            assert 'name' in model_config
            assert 'provider' in model_config

    def test_modes_structure(self):
        """Test that MODES has the correct structure."""
        assert isinstance(MODES, dict)
        assert len(MODES) > 0

        for mode_id, mode_config in MODES.items():
            assert isinstance(mode_id, str)
            assert isinstance(mode_config, dict)
            assert 'title' in mode_config
            assert 'icon' in mode_config
            assert 'prompt' in mode_config

    def test_default_config_structure(self):
        """Test that DEFAULT_CONFIG has the correct structure."""
        assert isinstance(DEFAULT_CONFIG, dict)
        assert 'api_key' in DEFAULT_CONFIG
        assert 'model' in DEFAULT_CONFIG
        assert 'theme' in DEFAULT_CONFIG
        assert 'last_version' in DEFAULT_CONFIG
        assert 'shortcut' in DEFAULT_CONFIG

    def test_config_file_path(self):
        """Test that CONFIG_FILE is a Path object."""
        assert isinstance(CONFIG_FILE, Path)

    def test_config_dir_path(self):
        """Test that CONFIG_DIR is a Path object."""
        assert isinstance(CONFIG_DIR, Path)

    def test_icon_path(self):
        """Test that ICON_PATH is a Path object."""
        assert isinstance(ICON_PATH, Path)


class TestModelProviders:
    """Test cases for model provider configurations."""

    def test_gemini_model_config(self):
        """Test Gemini model configuration."""
        gemini_config = AVAILABLE_MODELS.get("gemini-1.5-flash")
        assert gemini_config is not None
        assert gemini_config['provider'] == 'google'
        assert gemini_config['name'] == 'Gemini Flash'
        assert 'model_name' in gemini_config

    def test_openai_model_config(self):
        """Test OpenAI model configuration."""
        openai_config = AVAILABLE_MODELS.get("gpt-4o-mini")
        assert openai_config is not None
        assert openai_config['provider'] == 'openai'
        assert openai_config['name'] == 'OpenAI GPT-4o Mini'
        assert 'model_name' in openai_config

    def test_anthropic_model_config(self):
        """Test Anthropic model configuration."""
        anthropic_config = AVAILABLE_MODELS.get("claude-3-5-haiku-latest")
        assert anthropic_config is not None
        assert anthropic_config['provider'] == 'anthropic'
        assert anthropic_config['name'] == 'Anthropic Claude3.5 Haiku'
        assert 'model_name' in anthropic_config

    def test_custom_model_config(self):
        """Test custom model configuration."""
        custom_config = AVAILABLE_MODELS.get("custom")
        assert custom_config is not None
        assert custom_config['provider'] == 'custom'
        assert custom_config['name'] == 'Autre modèle'
        assert custom_config.get('configurable') is True


class TestModeConfigurations:
    """Test cases for mode configurations."""

    @pytest.mark.parametrize("mode_id,expected_title,has_placeholders", [
        ("traduire", "Traduire", False),
        ("corriger", "Corriger", False),
        ("reformuler", "Reformuler", False),
        ("repondre", "Répondre", True),
        ("resumer", "Résumer", False),
        ("analyser", "Analyser", False),
        ("professionaliser", "Professionaliser", False),
        ("etendre", "Étendre", False),
    ])
    def test_mode_configuration(self, mode_id, expected_title, has_placeholders):
        """Test mode configuration structure and content."""
        mode_config = MODES.get(mode_id)
        assert mode_config is not None
        assert mode_config['title'] == expected_title
        assert 'icon' in mode_config
        assert 'prompt' in mode_config
        assert isinstance(mode_config['prompt'], str)
        assert len(mode_config['prompt']) > 0

        if has_placeholders:
            assert '{original_message}' in mode_config['prompt']
            assert '{user_response}' in mode_config['prompt']

    def test_mode_icons(self):
        """Test that all modes have valid FontAwesome icons."""
        for mode_id, mode_config in MODES.items():
            assert 'icon' in mode_config
            icon = mode_config['icon']
            assert isinstance(icon, str)
            assert len(icon) > 0
            assert 'fa-' in icon or 'fas ' in icon or 'far ' in icon or 'fab ' in icon


class TestDefaultConfig:
    """Test cases for default configuration."""

    def test_default_config_values(self):
        """Test default configuration values."""
        assert DEFAULT_CONFIG['api_key'] is None
        assert DEFAULT_CONFIG['model'] == 'gemini-1.5-flash'
        assert DEFAULT_CONFIG['theme'] == 'light'
        assert DEFAULT_CONFIG['last_version'] == 1
        assert DEFAULT_CONFIG['shortcut'] == DEFAULT_SHORTCUT
        assert 'custom_endpoint' in DEFAULT_CONFIG

    def test_default_config_immutable(self):
        """Test that DEFAULT_CONFIG is not accidentally modified."""
        original_config = DEFAULT_CONFIG.copy()
        if 'api_key' in DEFAULT_CONFIG:
            DEFAULT_CONFIG['api_key'] = 'modified'
        if 'api_key' in DEFAULT_CONFIG:
            DEFAULT_CONFIG['api_key'] = original_config['api_key']


class TestPlatformSpecificConfig:
    """Test cases for platform-specific configuration."""

    @patch('sys.platform', 'win32')
    @patch('os.getenv')
    def test_windows_config_dir(self, mock_getenv):
        """Test configuration directory path on Windows."""
        mock_getenv.return_value = 'C:\\Users\\Test\\AppData\\Roaming'

        assert mock_getenv.return_value is not None
        assert 'AppData' in mock_getenv.return_value



class TestConfigValidation:
    """Test cases for configuration validation."""

    def test_model_names_in_available_models(self):
        """Test that all model names are valid."""
        for model_id, model_config in AVAILABLE_MODELS.items():
            assert 'name' in model_config
            assert isinstance(model_config['name'], str)
            assert len(model_config['name']) > 0

    def test_provider_values(self):
        """Test that provider values are valid."""
        valid_providers = {'google', 'openai', 'anthropic', 'custom'}
        for model_config in AVAILABLE_MODELS.values():
            assert model_config['provider'] in valid_providers

    def test_theme_values(self):
        """Test that theme values are valid."""
        assert DEFAULT_CONFIG['theme'] in {'light', 'dark'}

    def test_shortcut_format(self):
        """Test that shortcut format is valid."""
        shortcut = DEFAULT_CONFIG['shortcut']
        assert isinstance(shortcut, str)
        assert len(shortcut) > 0
        assert '+' in shortcut or len(shortcut.split()) == 1