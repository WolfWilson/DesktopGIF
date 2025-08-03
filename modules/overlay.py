#!/usr/bin/env python
# coding: utf-8
"""
modules/overlay.py – Ventana flotante para mostrar un GIF reescalable.
"""

from __future__ import annotations

from typing import cast

from PyQt6.QtCore import QPoint, QSize, Qt
from PyQt6.QtGui import QAction, QContextMenuEvent, QMovie, QMouseEvent
from PyQt6.QtWidgets import QLabel, QMainWindow, QMenu


class GifOverlay(QMainWindow):
    def __init__(self, gif_path: str, scale_percent: int = 100) -> None:
        super().__init__()
        self.gif_path = gif_path
        self.scale_percent = max(scale_percent, 1)
        self.old_pos: QPoint | None = None
        self.original_size: QSize | None = None  # Se define al primer frame

        # Configuración de ventana
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Cargar GIF
        self.label = QLabel(self)
        self.movie = QMovie(self.gif_path)

        if not self.movie.isValid():
            raise FileNotFoundError(f"El GIF no es válido o no se encontró: {gif_path}")

        self.label.setMovie(self.movie)
        self.setCentralWidget(self.label)

        self.movie.frameChanged.connect(self._on_first_frame)
        self.movie.start()

    # ------------------------------------------------------------------
    # Primer frame → calculamos tamaño y aplicamos escala
    # ------------------------------------------------------------------
    def _on_first_frame(self) -> None:
        self.original_size = self.movie.currentPixmap().size()
        self.apply_scale(self.scale_percent)
        self.movie.frameChanged.disconnect(self._on_first_frame)

    # ------------------------------------------------------------------
    # Redimensionamiento
    # ------------------------------------------------------------------
    def apply_scale(self, percent: int) -> None:
        if self.original_size is None:
            return
        self.scale_percent = percent
        w = int(self.original_size.width() * percent / 100)
        h = int(self.original_size.height() * percent / 100)
        new_size = QSize(max(w, 1), max(h, 1))
        self.movie.setScaledSize(new_size)
        self.setFixedSize(new_size)

    # ------------------------------------------------------------------
    # Arrastre
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
    # Menú contextual
    # ------------------------------------------------------------------
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu(self)

        # Escalas rápidas
        scale_menu = menu.addMenu("Escala")
        assert scale_menu is not None  # ← Pylance ya no avisa
        for pct in (50, 100, 150, 200):
            act = QAction(f"{pct}%", self)
            act.setCheckable(True)
            act.setChecked(pct == self.scale_percent)
            act.triggered.connect(lambda chk, p=pct: self.apply_scale(p))
            scale_menu.addAction(act)

        # Separador + cerrar
        menu.addSeparator()
        close_action = QAction("Cerrar GIF", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)

        menu.exec(event.globalPos())
