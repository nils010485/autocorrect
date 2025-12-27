import sys
import threading
from PyQt6.QtWidgets import QApplication
from waitress import serve
from autocorrect_pro.utils import find_free_port
from autocorrect_pro.gui import MainWindow
from autocorrect_pro import create_app

def main():
    """Main entry point of the application.

    Initializes the Qt GUI and Flask web server for the AI autocorrect application.
    Sets up platform-specific configurations and starts the main event loop.
    """
    if sys.platform.startswith('linux'):
        import os
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    else:
        import os
        os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"

    port = find_free_port()
    app = create_app()

    def run_waitress():
        """Run Flask app with Waitress production server."""
        serve(app, host='127.0.0.1', port=port, threads=6)

    flask_thread = threading.Thread(target=run_waitress)
    flask_thread.daemon = True
    flask_thread.start()

    qt_app = QApplication(sys.argv)
    window = MainWindow(port)
    window.show()

    sys.exit(qt_app.exec())

if __name__ == "__main__":
    main()
