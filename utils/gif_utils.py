#!/usr/bin/env python
# coding: utf-8
"""
utils/gif_utils.py – utilidades relacionadas con GIF.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMovie, QPixmap


def first_frame_as_pixmap(path: str | Path, thumb_size: QSize | None = None) -> QPixmap:
    """
    Devuelve el primer frame del GIF como QPixmap.
    • Si `thumb_size` se indica -> escala la miniatura.
    """
    movie = QMovie(str(path))
    if not movie.isValid():
        return QPixmap()

    # Salta al primer frame y obtén el pixmap
    movie.jumpToFrame(0)
    pix = movie.currentPixmap()
    if thumb_size is not None and not thumb_size.isNull():
        pix = pix.scaled(
            thumb_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    return pix
