#!/usr/bin/env python
# coding: utf-8
"""
ui/main_window.py – Panel de control con UI mejorada y estilo desacoplado.
"""

from __future__ import annotations

import signal
import sys
from typing import cast

from PyQt6.QtCore import Qt, QEvent, QTimer         # ← se importa Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QSpinBox,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from modules.overlay import GifOverlay
from ui.style_gui import APP_STYLE


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DesktopGIF Launcher")
        self.setFixedSize(440, 210)

        # Estado interno
        self.gif_path: str | None = None
        self.scale_percent: int = 100
        self.overlay_window: GifOverlay | None = None
        self._force_quit: bool = False

        # --------------- UI -----------------
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        # Título
        title = QLabel("DesktopGIF Launcher")
        title.setObjectName("titleLabel")                   # ← se asigna después
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Info
        self.info_label = QLabel("Ningún archivo GIF seleccionado.")
        self.info_label.setObjectName("infoLabel")
        self.info_label.setWordWrap(True)

        # Botón seleccionar
        self.btn_select = QPushButton("Seleccionar GIF")

        # Escala
        scale_box = QHBoxLayout()
        scale_label = QLabel("Escala:")
        self.spin_scale = QSpinBox()
        self.spin_scale.setRange(10, 400)
        self.spin_scale.setValue(100)
        self.spin_scale.setSuffix("%")
        scale_box.addWidget(scale_label)
        scale_box.addWidget(self.spin_scale)
        scale_box.addStretch()

        # Botón lanzar
        self.btn_launch = QPushButton("Lanzar GIF")
        self.btn_launch.setEnabled(False)

        # Añadir al layout principal
        main_layout.addWidget(title)
        main_layout.addSpacing(4)
        main_layout.addWidget(self.info_label)
        main_layout.addWidget(self.btn_select)
        main_layout.addLayout(scale_box)
        main_layout.addWidget(self.btn_launch)

        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # Estilo global
        self.setStyleSheet(APP_STYLE)

        # --------------- Conexiones ----------
        self.btn_select.clicked.connect(self.select_file)
        self.btn_launch.clicked.connect(self.launch_overlay)
        self.spin_scale.valueChanged.connect(lambda v: setattr(self, "scale_percent", v))

        self.setup_tray_icon()
        signal.signal(signal.SIGINT, lambda *_: self.close_app())

    # ------------------------------------------------------------------
    # Lógica principal
    # ------------------------------------------------------------------
    def select_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar GIF", "", "GIF Files (*.gif)")
        if path:
            self.gif_path = path
            self.info_label.setText(f"Archivo: …{path[-40:]}")
            self.btn_launch.setEnabled(True)

    def launch_overlay(self) -> None:
        if self.gif_path:
            if self.overlay_window and self.overlay_window.isVisible():
                self.overlay_window.close()
            self.overlay_window = GifOverlay(self.gif_path, self.scale_percent)
            self.overlay_window.show()

    # ------------------------------------------------------------------
    # Bandeja de sistema
    # ------------------------------------------------------------------
    def setup_tray_icon(self) -> None:
        try:
            icon = QIcon("icon.png")
            if icon.isNull():
                raise FileNotFoundError
            self.setWindowIcon(icon)
        except FileNotFoundError:
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
    # Eventos ventana / bandeja
    # ------------------------------------------------------------------
    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.WindowStateChange and self.isMinimized():
            QTimer.singleShot(0, self.hide)
            self.tray_icon.showMessage(
                "Minimizado",
                "DesktopGIF sigue ejecutándose.",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )
        super().changeEvent(event)

    def closeEvent(self, event):  # noqa: ANN001
        if self._force_quit:
            if self.overlay_window:
                self.overlay_window.close()
            self.tray_icon.hide()
            event.accept()
        else:
            event.ignore()
            self.hide()

    def show_from_tray(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def close_app(self) -> None:
        self._force_quit = True
        self.close()


# --------- Ejecutar directamente ----------
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())
