import signal
import sys

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


def handle_sigint(*args):            # Ctrl + C → salir con gracia
    QApplication.quit()


if __name__ == "__main__":
    # Asegura que SIGINT (Ctrl+C) no sea absorbido por Qt
    signal.signal(signal.SIGINT, handle_sigint)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # seguimos aún si todas las ventanas se ocultan

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
