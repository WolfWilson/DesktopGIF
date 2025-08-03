#!/usr/bin/env python
# coding: utf-8
#modules/overlay.py
"""
modules/overlay.py – Ventana flotante para mostrar un GIF reescalable.

• Sin bordes, transparente y siempre encima.
• Arrastrable con clic izquierdo.
• Menú contextual con escalas rápidas y cerrar.
• Callback opcional `on_close(x, y, scale)` para persistir estado.
"""

from __future__ import annotations

from typing import Callable, Optional, cast

from PyQt6.QtCore import QPoint, QSize, Qt
from PyQt6.QtGui import QAction, QContextMenuEvent, QMovie, QMouseEvent
from PyQt6.QtWidgets import QLabel, QMainWindow, QMenu


class GifOverlay(QMainWindow):
    def __init__(
        self,
        gif_path: str,
        scale_percent: int = 100,
        on_close: Optional[Callable[[int, int, int], None]] = None,
    ) -> None:
        super().__init__()
        self.gif_path = gif_path
        self.scale_percent = max(scale_percent, 1)
        self._on_close = on_close

        # Para arrastre
        self._drag_origin: QPoint | None = None
        self._original_size: QSize | None = None

        # ---------- Config ventana ----------
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # ---------- Cargar GIF ----------
        self._label = QLabel(self)
        self._movie = QMovie(self.gif_path)

        if not self._movie.isValid():
            raise FileNotFoundError(f"GIF inválido o no encontrado: {gif_path}")

        self._label.setMovie(self._movie)
        self.setCentralWidget(self._label)

        self._movie.frameChanged.connect(self._on_first_frame)
        self._movie.start()

    # ------------------------------------------------------------------
    # Primer frame → tamaño real
    # ------------------------------------------------------------------
    def _on_first_frame(self) -> None:
        self._original_size = self._movie.currentPixmap().size()
        self.apply_scale(self.scale_percent)
        self._movie.frameChanged.disconnect(self._on_first_frame)

    # ------------------------------------------------------------------
    # Escalado
    # ------------------------------------------------------------------
    def apply_scale(self, percent: int) -> None:
        if self._original_size is None:
            return
        self.scale_percent = max(percent, 1)
        w = self._original_size.width() * self.scale_percent // 100
        h = self._original_size.height() * self.scale_percent // 100
        new_size = QSize(max(w, 1), max(h, 1))
        self._movie.setScaledSize(new_size)
        self.setFixedSize(new_size)

    # ------------------------------------------------------------------
    # Arrastre
    # ------------------------------------------------------------------
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_origin is not None:
            delta = event.globalPosition().toPoint() - self._drag_origin
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_origin = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = None

    # ------------------------------------------------------------------
    # Menú contextual
    # ------------------------------------------------------------------
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu(self)

        scale_menu = cast(QMenu, menu.addMenu("Escala"))
        for pct in (50, 75, 100, 125, 150, 200):
            act = QAction(f"{pct} %", self)
            act.setCheckable(True)
            act.setChecked(pct == self.scale_percent)
            act.triggered.connect(lambda _=False, p=pct: self.apply_scale(p))
            scale_menu.addAction(act)

        menu.addSeparator()
        menu.addAction("Cerrar GIF", self.close)

        menu.exec(event.globalPos())

    # ------------------------------------------------------------------
    # Persistencia al cerrar
    # ------------------------------------------------------------------
    def closeEvent(self, event):  # noqa: ANN001
        if self._on_close:
            self._on_close(self.x(), self.y(), self.scale_percent)
        super().closeEvent(event)
