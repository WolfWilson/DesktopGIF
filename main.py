#!/usr/bin/env python
# coding: utf-8
"""
main.py – Punto de entrada de DesktopGIF
"""

from __future__ import annotations

import signal
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


def _handle_sigint(*_args) -> None:
    """Permite cerrar la app con Ctrl + C cuando se ejecuta en consola."""
    QApplication.quit()


def _enable_high_dpi() -> None:
    """
    Activa los flags High-DPI solo si existen en la versión de PyQt6 instalada.
    Esto evita advertencias “atributo desconocido” en algunos stubs.
    """
    for name in ("AA_EnableHighDpiScaling", "AA_UseHighDpiPixmaps"):
        attr = getattr(Qt.ApplicationAttribute, name, None)
        if attr is not None:
            QApplication.setAttribute(attr, True)  # type: ignore[arg-type]


def main() -> None:
    _enable_high_dpi()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    signal.signal(signal.SIGINT, _handle_sigint)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
