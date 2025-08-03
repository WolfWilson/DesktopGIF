#!/usr/bin/env python
# coding: utf-8
"""
ui/edit_page.py – Panel de Edición (placeholder para futuro).
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout


class EditPage(QWidget):
    def __init__(self) -> None:
        super().__init__()

        lbl = QLabel("<h2>Panel de Edición</h2><p>Próximamente…</p>")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(lbl)
        self.setLayout(layout)
