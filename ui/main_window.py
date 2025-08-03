#!/usr/bin/env python
# coding: utf-8
"""
ui/main_window.py – Panel de control de DesktopGIF
· Permite elegir un GIF, lanzarlo como ventana flotante y
  minimizarse a la bandeja del sistema.
"""

from __future__ import annotations

import signal
import sys
from typing import cast

from PyQt6.QtCore import QEvent, QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QStyle,          # ← ¡QStyle vive en QtWidgets!
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)
from modules.overlay import GifOverlay

class MainWindow(QMainWindow):
    """
    Ventana principal que funciona como panel de control.
    Permite seleccionar un GIF, lanzarlo y se minimiza a la bandeja de sistema.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DesktopGIF Launcher")
        self.setFixedSize(400, 150)

        # Estado interno
        self.gif_path: str | None = None
        self.overlay_window: GifOverlay | None = None
        self._force_quit: bool = False  # Controla el cierre definitivo

        # ---------------------- UI ----------------------
        layout = QVBoxLayout()
        self.label = QLabel("Ningún archivo GIF seleccionado.")
        self.btn_select = QPushButton("Seleccionar GIF")
        self.btn_launch = QPushButton("Lanzar GIF")
        self.btn_launch.setEnabled(False)

        layout.addWidget(self.label)
        layout.addWidget(self.btn_select)
        layout.addWidget(self.btn_launch)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # ------------------ Conexiones ------------------
        self.btn_select.clicked.connect(self.select_file)
        self.btn_launch.clicked.connect(self.launch_overlay)

        # -------------- Ícono de bandeja ---------------
        self.setup_tray_icon()

        # -------------- Ctrl+C en consola --------------
        signal.signal(signal.SIGINT, lambda *_: self.close_app())

    # ------------------------------------------------------------------
    # Selección y lanzamiento del GIF
    # ------------------------------------------------------------------
    def select_file(self) -> None:
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar GIF", "", "GIF Files (*.gif)"
        )
        if filepath:
            self.gif_path = filepath
            self.label.setText(f"Archivo: …{self.gif_path[-35:]}")
            self.btn_launch.setEnabled(True)

    def launch_overlay(self) -> None:
        if self.gif_path:
            if self.overlay_window and self.overlay_window.isVisible():
                self.overlay_window.close()

            self.overlay_window = GifOverlay(self.gif_path)
            self.overlay_window.show()

    # ------------------------------------------------------------------
    # Configuración bandeja de sistema
    # ------------------------------------------------------------------
    def setup_tray_icon(self) -> None:
        try:
            icon = QIcon("icon.png")
            if icon.isNull():
                raise FileNotFoundError
            self.setWindowIcon(icon)
        except FileNotFoundError:
            # Pylance feliz: aseguramos que style no sea None
            style = cast(QStyle, self.style())
            icon = style.standardIcon(style.StandardPixmap.SP_TitleBarMenuButton)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("DesktopGIF Launcher")

        tray_menu = QMenu()
        show_action = QAction("Mostrar Panel", self)
        quit_action = QAction("Salir", self)

        show_action.triggered.connect(self.show_from_tray)
        quit_action.triggered.connect(self.close_app)

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    # ------------------------------------------------------------------
    # Eventos de ventana
    # ------------------------------------------------------------------
    def changeEvent(self, event: QEvent) -> None:
        """Detecta el minimizado y esconde la ventana."""
        if event.type() == QEvent.Type.WindowStateChange and self.isMinimized():
            QTimer.singleShot(0, self.hide)
            self.tray_icon.showMessage(
                "Minimizado a la bandeja",
                "DesktopGIF sigue ejecutándose.",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )
        super().changeEvent(event)

    def closeEvent(self, event) -> None:  # noqa: D401
        """Intercepta el cierre de ventana."""
        if self._force_quit:
            if self.overlay_window:
                self.overlay_window.close()
            self.tray_icon.hide()
            event.accept()
        else:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "En segundo plano",
                "DesktopGIF sigue ejecutándose. Hacé clic derecho en el ícono para salir.",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )

    # ------------------------------------------------------------------
    # Acciones de bandeja
    # ------------------------------------------------------------------
    def show_from_tray(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def close_app(self) -> None:
        """Cierra por completo la aplicación."""
        self._force_quit = True
        self.close()


# ----------------------------------------------------------------------
# Lanzador principal (para ejecutar directamente este módulo)
# ----------------------------------------------------------------------
def main() -> None:
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
