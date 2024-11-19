import sys
import threading
from PyQt6.QtWidgets import QApplication
from autocorrect_pro.utils import find_free_port
from autocorrect_pro.gui import MainWindow
from autocorrect_pro import create_app

def main():
    """Point d'entrée principal de l'application."""
    # Configuration pour Linux
    if sys.platform.startswith('linux'):
        import os
        os.environ["QT_QPA_PLATFORM"] = "xcb"

    # Initialisation du serveur Flask
    port = find_free_port()
    app = create_app()
    flask_thread = threading.Thread(target=lambda: app.run(port=port, debug=False))
    flask_thread.daemon = True
    flask_thread.start()

    # Initialisation de l'interface Qt
    qt_app = QApplication(sys.argv)
    window = MainWindow(port)
    window.show()

    sys.exit(qt_app.exec())

if __name__ == "__main__":
    main()
