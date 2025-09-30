"""
Entry point for pip installation.

This module provides the main entry point when the package is installed
via pip and contains the primary application initialization logic.
"""
import sys
import threading
from PyQt6.QtWidgets import QApplication
from .utils import find_free_port
from .gui import MainWindow
from . import create_app

def main() -> None:
    """
Main entry point for the application.

Initializes and starts the AI AutoCorrect application by:
- Setting up platform-specific Qt configuration
- Starting the Flask web server in a background thread
- Launching the Qt GUI application
"""
    if sys.platform.startswith('linux'):
        import os
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    else:
        import os
        os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"

    port = find_free_port()
    app = create_app()
    flask_thread = threading.Thread(target=lambda: app.run(port=port, debug=False))
    flask_thread.daemon = True
    flask_thread.start()

    qt_app = QApplication(sys.argv)
    window = MainWindow(port)
    window.show()

    sys.exit(qt_app.exec())

if __name__ == "__main__":
    main()