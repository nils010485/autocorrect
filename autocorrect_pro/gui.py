# gui.py
from PyQt6.QtWidgets import QMainWindow, QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QIcon
from pynput import keyboard
from rich.console import Console

from .config import ICON_PATH, DEFAULT_SHORTCUT
from .utils import load_config, save_config

console = Console()
class MainWindow(QMainWindow):
    toggle_signal = pyqtSignal()

    def __init__(self, port: int):
        super().__init__()
        self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setWindowTitle("AI-AutoCorrect")
        self.setWindowFlags(Qt.WindowType.Window)  # Ajouter cette ligne
        self._setup_window_geometry()
        self._setup_web_view(port)
        self.create_tray_icon()
        self.toggle_signal.connect(self._toggle_visibility)

        try:
            self.setup_keyboard_listener()
        except ValueError:
            console.print("[red]Raccourcis invalide, remise à zero")
            config = load_config()
            save_config(api_key=config['api_key'], model=config['model'],
                        theme=config['theme'], last_version=config['last_version'],
                        shortcut=DEFAULT_SHORTCUT)
            self.setup_keyboard_listener()

        self.setup_app_shortcut()
        self.is_visible = True
        self.prevent_double_activation = False

    def _setup_window_geometry(self):
        """Configure la géométrie de la fenêtre."""
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        scale_factor = dpi / 96.0

        width = int(1000 * scale_factor)
        height = int(900 * scale_factor)
        min_width = int(800 * scale_factor)
        min_height = int(600 * scale_factor)

        self.setGeometry(100, 100, width, height)
        self.setMinimumSize(min_width, min_height)

    def _setup_web_view(self, port: int):
        """Configure la vue web."""
        self.web = QWebEngineView()
        self.web.setUrl(QUrl(f"http://127.0.0.1:{port}"))
        self.setCentralWidget(self.web)

    def setup_keyboard_listener(self):
        """Configure l'écouteur de raccourcis clavier global."""
        config = load_config()
        hotkey = config.get('shortcut', DEFAULT_SHORTCUT)
        pynput_hotkey = self.convert_hotkey_to_pynput(hotkey)

        self.keyboard_listener = keyboard.GlobalHotKeys({
            pynput_hotkey: self.toggle_visibility
        })
        self.keyboard_listener.start()

    def setup_app_shortcut(self):
        """Configure le raccourci de l'application."""
        config = load_config()
        shortcut_str = config.get('shortcut', DEFAULT_SHORTCUT)
        self.app_shortcut = QShortcut(QKeySequence(shortcut_str), self)
        self.app_shortcut.activated.connect(self.toggle_visibility)

    @staticmethod
    def convert_hotkey_to_pynput(hotkey):
        """Convertit un raccourci Qt en format pynput."""
        parts = hotkey.split('+')
        pynput_parts = []
        for part in parts:
            if len(part) > 1:
                pynput_parts.append(f'<{part}>')
            else:
                pynput_parts.append(part)
        return '+'.join(pynput_parts)

    def create_tray_icon(self):
        """Crée l'icône de la barre des tâches."""
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

    def tray_icon_activated(self, reason):
        """Gère l'activation de l'icône de la barre des tâches."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_visibility()

    def toggle_visibility(self):
        """Bascule la visibilité de la fenêtre avec protection anti-rebond."""
        if not self.prevent_double_activation:
            self.prevent_double_activation = True
            self.toggle_signal.emit()
            QTimer.singleShot(200, self.reset_activation_flag)

    def reset_activation_flag(self):
        """Réinitialise le drapeau de protection anti-rebond."""
        self.prevent_double_activation = False

    def _toggle_visibility(self):
        """Implémente la bascule de visibilité."""
        if self.is_visible:
            self.hide()
            self.is_visible = False
        else:
            self.show()
            self.activateWindow()
            self.raise_()
            self.is_visible = True

    def closeEvent(self, event):
        """Gère l'événement de fermeture."""
        event.ignore()
        self.hide()

    def quit_application(self):
        """Quitte l'application."""
        self.keyboard_listener.stop()
        QApplication.quit()
