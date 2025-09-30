"""
GUI components for the application.

This module contains Qt-based GUI components including the main window,
web view integration, system tray, and keyboard shortcuts.
"""
import logging
from PyQt6.QtWidgets import QMainWindow, QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, pyqtSignal, QTimer, Qt, QObject
from PyQt6.QtGui import QKeySequence, QShortcut, QIcon
from PyQt6.QtWebChannel import QWebChannel
from pynput import keyboard
from rich.console import Console
from .config import ICON_PATH, DEFAULT_SHORTCUT
from .utils import load_config, save_config
import pyperclip

console = Console()

# Configure logging
logger = logging.getLogger(__name__)

class WebViewBridge(QObject):
    """
    Bridge for communication between web interface and application.

    Provides a communication channel between the Qt application and
    the web interface running in the embedded web view.
    """
    clipboard_text_signal = pyqtSignal(str)

class MainWindow(QMainWindow):
    """
    Main application window with Qt GUI and embedded web view.

    Handles the main application interface, global shortcuts,
    system tray integration, and communication with the web backend.
    """
    toggle_signal = pyqtSignal()

    def __init__(self, port: int) -> None:
        """
        Initialize the main window with embedded web view.

        Args:
            port: Port number for the Flask web server
        """
        super().__init__()
        self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setWindowTitle("AI-AutoCorrect")
        self.setWindowFlags(Qt.WindowType.Window)
        self._setup_window_geometry()
        self._setup_web_view(port)
        self.create_tray_icon()
        self.toggle_signal.connect(self._toggle_visibility)
        self.port = port
        self.clipboard_last_content = pyperclip.paste()

        self.web_bridge = WebViewBridge()

        self.web_channel = QWebChannel(self.web.page())
        self.web.page().setWebChannel(self.web_channel)
        self.web_channel.registerObject('pywebview', self.web_bridge)

        try:
            self.setup_keyboard_listener()
        except ValueError:
            logger.warning("Raccourcis invalide, remise à zero")
            console.print("[red]Raccourcis invalide, remise à zero")
            config = load_config()
            save_config(api_key=config['api_key'], model=config['model'],
                        theme=config['theme'], last_version=config['last_version'],
                        shortcut=DEFAULT_SHORTCUT)
            self.setup_keyboard_listener()

        self.setup_app_shortcut()
        self.is_visible = True
        self.prevent_double_activation = False

    def _setup_window_geometry(self) -> None:
        """
        Configure window geometry and DPI scaling.

        Sets up appropriate window size and minimum size based on
        screen DPI for better display scaling.
        """
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        scale_factor = dpi / 96.0

        width = int(1000 * scale_factor)
        height = int(950 * scale_factor)
        min_width = int(800 * scale_factor)
        min_height = int(600 * scale_factor)

        self.setGeometry(100, 100, width, height)
        self.setMinimumSize(min_width, min_height)

    def _setup_web_view(self, port: int) -> None:
        """
        Configure the embedded web view.

        Sets up the QWebEngineView to display the web interface
        and configures the web channel for communication.

        Args:
            port: Port number for the Flask web server
        """
        self.web = QWebEngineView()
        self.web.setUrl(QUrl(f"http://127.0.0.1:{port}"))
        self.setCentralWidget(self.web)

    def setup_keyboard_listener(self) -> None:
        """
        Set up global keyboard shortcut listener.

        Configures pynput to listen for global hotkeys that can
        toggle window visibility even when the app is not focused.
        """
        config = load_config()
        hotkey = config.get('shortcut', DEFAULT_SHORTCUT)
        pynput_hotkey = self.convert_hotkey_to_pynput(hotkey)

        self.keyboard_listener = keyboard.GlobalHotKeys({
            pynput_hotkey: self.toggle_visibility
        })
        self.keyboard_listener.start()

    def setup_app_shortcut(self) -> None:
        """
        Set up application-specific shortcut.

        Configures Qt keyboard shortcuts that work when the
        application window is focused.
        """
        config = load_config()
        shortcut_str = config.get('shortcut', DEFAULT_SHORTCUT)
        self.app_shortcut = QShortcut(QKeySequence(shortcut_str), self)
        self.app_shortcut.activated.connect(self.toggle_visibility)

    @staticmethod
    def convert_hotkey_to_pynput(hotkey: str) -> str:
        """
        Convert Qt hotkey format to pynput format.

        Translates keyboard shortcuts from Qt format (e.g., "Ctrl+Space")
        to pynput format (e.g., "<ctrl>+<space>").

        Args:
            hotkey: Hotkey string in Qt format

        Returns:
            str: Hotkey string in pynput format
        """
        parts = hotkey.split('+')
        pynput_parts = []
        for part in parts:
            if len(part) > 1:
                pynput_parts.append(f'<{part}>')
            else:
                pynput_parts.append(part)
        return '+'.join(pynput_parts)

    def create_tray_icon(self) -> None:
        """
        Create system tray icon.

        Sets up the system tray icon with context menu for
        application control when minimized to tray.
        """
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Afficher/Masquer")
        show_action.triggered.connect(self.toggle_visibility)
        quit_action = tray_menu.addAction("Quitter")
        quit_action.triggered.connect(self.quit_application)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setIcon(QIcon(str(ICON_PATH)))
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Handle system tray icon activation.

        Responds to user interactions with the system tray icon,
        particularly double-clicks to show/hide the window.

        Args:
            reason: The activation reason (e.g., double-click)
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_visibility()

    def toggle_visibility(self) -> None:
        """
        Toggle window visibility with debouncing.

        Shows or hides the application window with anti-rebound
        protection to prevent accidental multiple toggles.
        """
        if not self.prevent_double_activation:
            self.prevent_double_activation = True
            self.toggle_signal.emit()
            QTimer.singleShot(200, self.reset_activation_flag)

    def reset_activation_flag(self) -> None:
        """
        Reset the anti-rebound protection flag.

        Re-enables visibility toggling after the debouncing delay.
        """
        self.prevent_double_activation = False

    def _toggle_visibility(self) -> None:
        """
        Implement visibility toggling logic.

        Handles the actual showing/hiding of the window and
        clipboard integration for text input.
        """
        if self.is_visible:
            self.hide()
            self.is_visible = False
        else:
            clipboard_content = pyperclip.paste()
            if isinstance(clipboard_content, str) and len(clipboard_content) > 0 and clipboard_content != self.clipboard_last_content and len(clipboard_content) < 2000:
                self.clipboard_last_content = clipboard_content
                self.web_bridge.clipboard_text_signal.emit(clipboard_content)
            else:
                self.show()
                self.activateWindow()
                self.raise_()
                self.is_visible = True

    def closeEvent(self, event) -> None:
        """
        Handle window close event.

        Overrides the default close behavior to hide the window
        instead of closing it, allowing the app to run in background.

        Args:
            event: The close event
        """
        event.ignore()
        self.hide()

    def quit_application(self) -> None:
        """
        Quit the application completely.

        Stops background processes and terminates the application.
        """
        self.keyboard_listener.stop()
        QApplication.quit()
