import pytest
from unittest.mock import patch, mock_open

from autocorrect_pro.utils import (
    validate_audio_file,
    find_free_port,
    ensure_config_dir,
    load_config,
    save_config,
    load_api_key,
    save_api_key,
    load_modes,
    save_custom_mode,
    get_custom_endpoint,
    save_custom_endpoint,
    restart_application
)


class TestValidateAudioFile:
    """Test cases for validate_audio_file function."""

    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('os.path.basename')
    def test_validate_audio_file_valid(self, mock_basename, mock_getsize, mock_exists):
        """
        Test validation of a valid audio file.

        This test verifies that the validate_audio_file function correctly
        identifies a valid audio file with proper extension and size.
        """
        mock_exists.return_value = True
        mock_basename.return_value = "test.mp3"
        mock_getsize.return_value = 10 * 1024 * 1024

        valid, error = validate_audio_file("/fake/path/test.mp3")
        assert valid is True
        assert error == ""

    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_validate_audio_file_invalid_extension(self, mock_basename, mock_exists):
        """Test validation of file with invalid extension."""
        mock_exists.return_value = True
        mock_basename.return_value = "test.txt"

        valid, error = validate_audio_file("/fake/path/test.txt")
        assert valid is False
        assert "Format de fichier non supporté" in error

    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('os.path.basename')
    def test_validate_audio_file_too_large(self, mock_basename, mock_getsize, mock_exists):
        """Test validation of file that's too large."""
        mock_exists.return_value = True
        mock_basename.return_value = "test.mp3"
        mock_getsize.return_value = 30 * 1024 * 1024

        valid, error = validate_audio_file("/fake/path/test.mp3")
        assert valid is False
        assert "Le fichier est trop volumineux" in error

    @patch('os.path.exists')
    def test_validate_audio_file_not_found(self, mock_exists):
        """Test validation of non-existent file."""
        mock_exists.return_value = False

        valid, error = validate_audio_file("/nonexistent/file.mp3")
        assert valid is False
        assert "Fichier audio non trouvé" in error

    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('os.path.basename')
    def test_validate_audio_file_edge_case_exact_limit(self, mock_basename, mock_getsize, mock_exists):
        """Test validation with exactly 25MB file (edge case)."""
        mock_exists.return_value = True
        mock_basename.return_value = "test.mp3"
        mock_getsize.return_value = 25 * 1024 * 1024

        valid, error = validate_audio_file("/fake/path/test.mp3")
        assert valid is True
        assert error == ""

    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('os.path.basename')
    def test_validate_audio_file_edge_case_over_limit(self, mock_basename, mock_getsize, mock_exists):
        """Test validation with 25MB + 1 byte file (edge case)."""
        mock_exists.return_value = True
        mock_basename.return_value = "test.mp3"
        mock_getsize.return_value = (25 * 1024 * 1024) + 1

        valid, error = validate_audio_file("/fake/path/test.mp3")
        assert valid is False
        assert "Le fichier est trop volumineux" in error

    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('os.path.basename')
    def test_validate_audio_file_zero_size(self, mock_basename, mock_getsize, mock_exists):
        """Test validation of zero-byte file."""
        mock_exists.return_value = True
        mock_basename.return_value = "test.mp3"
        mock_getsize.return_value = 0

        valid, error = validate_audio_file("/fake/path/test.mp3")
        assert valid is True
        assert error == ""

    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('os.path.basename')
    def test_validate_audio_file_case_insensitive_extension(self, mock_basename, mock_getsize, mock_exists):
        """Test validation with uppercase extension."""
        mock_exists.return_value = True
        mock_basename.return_value = "test.MP3"
        mock_getsize.return_value = 10 * 1024 * 1024

        valid, error = validate_audio_file("/fake/path/test.MP3")
        assert valid is True
        assert error == ""

    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('os.path.basename')
    def test_validate_audio_file_mixed_case_extension(self, mock_basename, mock_getsize, mock_exists):
        """Test validation with mixed case extension."""
        mock_exists.return_value = True
        mock_basename.return_value = "test.Mp3"
        mock_getsize.return_value = 10 * 1024 * 1024

        valid, error = validate_audio_file("/fake/path/test.Mp3")
        assert valid is True
        assert error == ""


class TestFindFreePort:
    """Test cases for find_free_port function."""

    def test_find_free_port_returns_integer(self):
        """Test that find_free_port returns an integer."""
        port = find_free_port()
        assert isinstance(port, int)
        assert 1024 <= port <= 65535


class TestConfigFunctions:
    """Test cases for configuration functions."""

    @patch('autocorrect_pro.utils.CONFIG_FILE')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_config_existing_file(self, mock_file, mock_config_file):
        """Test loading configuration from existing file."""
        mock_config_file.exists.return_value = True
        mock_file.return_value.read.return_value = '{"api_key": "test_key"}'

        with patch('json.load', return_value={"api_key": "test_key"}):
            config = load_config()
            assert config["api_key"] == "test_key"

    @patch('autocorrect_pro.utils.CONFIG_FILE')
    def test_load_config_no_file(self, mock_config_file):
        """Test loading configuration when file doesn't exist."""
        mock_config_file.exists.return_value = False

        from autocorrect_pro.config import DEFAULT_CONFIG
        config = load_config()
        assert config == DEFAULT_CONFIG.copy()

    @patch('autocorrect_pro.utils.CONFIG_FILE')
    @patch('builtins.open', new_callable=mock_open)
    @patch('autocorrect_pro.utils.load_config')
    def test_save_config_success(self, mock_load_config, mock_file, mock_config_file):
        """Test successful configuration saving."""
        mock_load_config.return_value = {"api_key": "old_key"}

        result = save_config(api_key="new_key")
        assert result is True

        mock_file.assert_called_once()

    @patch('autocorrect_pro.utils.CONFIG_FILE')
    @patch('builtins.open', new_callable=mock_open)
    @patch('autocorrect_pro.utils.load_config')
    def test_save_config_failure(self, mock_load_config, mock_file, mock_config_file):
        """Test configuration saving failure."""
        mock_load_config.return_value = {"api_key": "old_key"}
        mock_file.side_effect = Exception("Permission denied")

        result = save_config(api_key="new_key")
        assert result is False

    @patch('autocorrect_pro.utils.CONFIG_FILE')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_api_key_success(self, mock_file, mock_config_file):
        """Test successful API key loading."""
        mock_config_file.exists.return_value = True
        mock_file.return_value.read.return_value = '{"api_key": "test_key"}'

        with patch('json.load', return_value={"api_key": "test_key"}):
            api_key = load_api_key()
            assert api_key == "test_key"

    @patch('autocorrect_pro.utils.CONFIG_FILE')
    def test_load_api_key_no_file(self, mock_config_file):
        """Test API key loading when file doesn't exist."""
        mock_config_file.exists.return_value = False

        api_key = load_api_key()
        assert api_key is None

    @patch('autocorrect_pro.utils.CONFIG_FILE')
    @patch('builtins.open', new_callable=mock_open)
    @patch('autocorrect_pro.utils.load_config')
    def test_save_api_key_success(self, mock_load_config, mock_file, mock_config_file):
        """Test successful API key saving."""
        mock_load_config.return_value = {"api_key": "old_key"}

        result = save_api_key("new_key")
        assert result is True

    @patch('autocorrect_pro.utils.CONFIG_FILE')
    @patch('builtins.open', new_callable=mock_open)
    @patch('autocorrect_pro.utils.load_config')
    def test_save_api_key_failure(self, mock_load_config, mock_file, mock_config_file):
        """Test API key saving failure."""
        mock_load_config.return_value = {"api_key": "old_key"}
        mock_file.side_effect = Exception("Permission denied")

        result = save_api_key("new_key")
        assert result is False


class TestModesFunctions:
    """Test cases for modes functions."""

    @patch('autocorrect_pro.utils.load_config')
    @patch('autocorrect_pro.utils.save_config')
    def test_load_modes_no_modes_config(self, mock_save_config, mock_load_config):
        """Test loading modes when no modes are configured."""
        mock_load_config.return_value = {}

        from autocorrect_pro.config import MODES
        modes = load_modes()

        assert 'system' in modes
        assert 'custom' in modes
        assert 'order' in modes
        assert modes['system'] == MODES

    @patch('autocorrect_pro.utils.load_config')
    @patch('autocorrect_pro.utils.save_config')
    def test_load_modes_existing_config(self, mock_save_config, mock_load_config):
        """Test loading modes from existing configuration."""
        mock_load_config.return_value = {
            'modes': {
                'system': {'traduire': {'title': 'Traduire'}},
                'custom': {'custom_1': {'title': 'Custom Mode'}},
                'order': ['traduire', 'custom_1']
            }
        }

        modes = load_modes()

        assert modes['system']['traduire']['title'] == 'Traduire'
        assert modes['custom']['custom_1']['title'] == 'Custom Mode'
        assert modes['order'] == ['traduire', 'custom_1']

    @patch('autocorrect_pro.utils.load_config')
    @patch('autocorrect_pro.utils.save_config')
    def test_save_custom_mode_success(self, mock_save_config, mock_load_config):
        """Test successful custom mode saving."""
        mock_load_config.return_value = {
            'modes': {'system': {}, 'custom': {}, 'order': []}
        }
        mock_save_config.return_value = True

        mode_data = {
            'title': 'Test Mode',
            'icon': 'fas fa-test',
            'prompt': 'Test prompt'
        }

        result = save_custom_mode(mode_data)
        assert result is True

        mock_save_config.assert_called_once()

    @patch('autocorrect_pro.utils.load_config')
    @patch('autocorrect_pro.utils.save_config')
    def test_save_custom_mode_failure(self, mock_save_config, mock_load_config):
        """Test custom mode saving failure."""
        mock_load_config.return_value = {
            'modes': {'system': {}, 'custom': {}, 'order': []}
        }
        mock_save_config.return_value = False

        mode_data = {
            'title': 'Test Mode',
            'icon': 'fas fa-test',
            'prompt': 'Test prompt'
        }

        result = save_custom_mode(mode_data)
        assert result is False


class TestCustomEndpointFunctions:
    """Test cases for custom endpoint functions."""

    @patch('autocorrect_pro.utils.load_config')
    def test_get_custom_endpoint_default(self, mock_load_config):
        """Test getting custom endpoint with default values."""
        mock_load_config.return_value = {}

        endpoint = get_custom_endpoint()
        assert endpoint == {'url': '', 'model_name': '', 'style': 'openai'}

    @patch('autocorrect_pro.utils.load_config')
    def test_get_custom_endpoint_existing(self, mock_load_config):
        """Test getting existing custom endpoint."""
        mock_load_config.return_value = {
            'custom_endpoint': {
                'url': 'http://localhost:8000',
                'model_name': 'test-model'
            }
        }

        endpoint = get_custom_endpoint()
        assert endpoint['url'] == 'http://localhost:8000'
        assert endpoint['model_name'] == 'test-model'

    @patch('autocorrect_pro.utils.load_config')
    @patch('autocorrect_pro.utils.save_config')
    def test_save_custom_endpoint_success(self, mock_save_config, mock_load_config):
        """Test successful custom endpoint saving."""
        mock_load_config.return_value = {}
        mock_save_config.return_value = True

        result = save_custom_endpoint('http://localhost:8000', 'test-model')
        assert result is True

        mock_save_config.assert_called_once()

    @patch('autocorrect_pro.utils.load_config')
    @patch('autocorrect_pro.utils.save_config')
    def test_save_custom_endpoint_failure(self, mock_save_config, mock_load_config):
        """Test custom endpoint saving failure."""
        mock_load_config.return_value = {}
        mock_save_config.return_value = False

        result = save_custom_endpoint('http://localhost:8000', 'test-model')
        assert result is False


class TestEnsureConfigDir:
    """Test cases for ensure_config_dir function."""

    @patch('autocorrect_pro.utils.CONFIG_DIR')
    def test_ensure_config_dir_creates_directory(self, mock_config_dir):
        """Test that ensure_config_dir creates the directory."""
        mock_config_dir.exists.return_value = False

        ensure_config_dir()

        mock_config_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('autocorrect_pro.utils.CONFIG_DIR')
    def test_ensure_config_dir_directory_exists(self, mock_config_dir):
        """Test ensure_config_dir when directory already exists."""
        mock_config_dir.exists.return_value = True

        ensure_config_dir()

        mock_config_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestRestartApplication:
    """Test cases for restart_application function."""

    @patch('autocorrect_pro.utils.os.execl')
    @patch('autocorrect_pro.utils.sys.executable', '/usr/bin/python3')
    @patch('autocorrect_pro.utils.sys.argv', ['main.py', '--arg1', 'value1'])
    def test_restart_application_calls_os_execl(self, mock_execl):
        """Test that restart_application calls os.execl with correct parameters."""
        restart_application()

        mock_execl.assert_called_once_with('/usr/bin/python3', '/usr/bin/python3', 'main.py', '--arg1', 'value1')

    @patch('autocorrect_pro.utils.console.print')
    @patch('autocorrect_pro.utils.os.execl')
    def test_restart_application_prints_message(self, mock_execl, mock_print):
        """Test that restart_application prints restart message."""
        restart_application()

        mock_print.assert_called_once_with("[bold blue]Redémarrage de l'application pour appliquer les changements de raccourci...[/bold blue]")

    @patch('autocorrect_pro.utils.os.execl')
    def test_restart_application_raises_exception_on_failure(self, mock_execl):
        """Test that restart_application raises exception when os.execl fails."""
        mock_execl.side_effect = OSError("Cannot exec")

        with pytest.raises(OSError, match="Cannot exec"):
            restart_application()