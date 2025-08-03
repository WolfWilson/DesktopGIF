#!/usr/bin/env python
# coding: utf-8
"""
modules/overlay.py – Ventana flotante que muestra el GIF seleccionado.
• Sin bordes, transparente, siempre encima.
• Movible al arrastrar y cerrable con clic derecho.
"""

from __future__ import annotations

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QAction, QContextMenuEvent, QMovie, QMouseEvent
from PyQt6.QtWidgets import QLabel, QMainWindow, QMenu


class GifOverlay(QMainWindow):
    def __init__(self, gif_path: str) -> None:
        super().__init__()
        self.gif_path = gif_path
        self.old_pos: QPoint | None = None

        # --- Configuración de ventana ---
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool  # No aparece en la barra de tareas
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # --- Cargar y mostrar el GIF ---
        self.label = QLabel(self)
        self.movie = QMovie(self.gif_path)

        if not self.movie.isValid():
            raise FileNotFoundError(f"El GIF no es válido o no se encontró: {gif_path}")

        self.label.setMovie(self.movie)
        self.setCentralWidget(self.label)

        self.movie.frameChanged.connect(self._on_first_frame)
        self.movie.start()

    # ------------------------------------------------------------------
    # Ajuste del tamaño en el primer frame
    # ------------------------------------------------------------------
    def _on_first_frame(self) -> None:
        self.setFixedSize(self.movie.currentPixmap().size())
        self.movie.frameChanged.disconnect(self._on_first_frame)

    # ------------------------------------------------------------------
    # Arrastre de ventana
    # ------------------------------------------------------------------
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    # ------------------------------------------------------------------
    # Menú contextual (clic derecho)
    # ------------------------------------------------------------------
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu(self)
        close_action = QAction("Cerrar GIF", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)

        menu.exec(event.globalPos())
