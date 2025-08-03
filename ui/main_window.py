#!/usr/bin/env python
# coding: utf-8
"""
ui/main_window.py – Ventana principal de DesktopGIF.
"""

from __future__ import annotations

from typing import Dict, cast

from PyQt6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, Qt, QTimer, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QStackedWidget,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from storage.library_store import LibraryStore
from ui.library_page import LibraryPage
from ui.edit_page import EditPage


class MainWindow(QMainWindow):
    COLLAPSED = 60
    EXPANDED = 200

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DesktopGIF – Librería y Edición")
        self.resize(960, 640)

        self._store = LibraryStore()
        self._menu_anim: QPropertyAnimation | None = None
        self._menu_expanded = False

        # ---------- menú lateral ----------
        self.menu_frame = QFrame()
        self.menu_frame.setObjectName("menuFrame")       #  ← setObjectName en vez de parámetro
        self.menu_frame.setStyleSheet("#menuFrame { background-color: #333; }")
        self.menu_frame.setFixedWidth(self.COLLAPSED)

        self.btn_toggle = QPushButton("Menú")
        self.btn_library = QPushButton("Librería")
        self.btn_edit = QPushButton("Panel de Edición")

        self.menu_buttons: Dict[QPushButton, str] = {
            self.btn_toggle: "Menú",
            self.btn_library: "Librería",
            self.btn_edit: "Panel de Edición",
        }

        menu_layout = QVBoxLayout(self.menu_frame)
        menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        menu_layout.setContentsMargins(4, 4, 4, 4)
        menu_layout.setSpacing(8)

        for btn, text in self.menu_buttons.items():
            btn.setIcon(self._icon_for(text))
            btn.setIconSize(QSize(32, 32))
            btn.setText("")
            btn.setStyleSheet(
                """
                QPushButton {
                    color: white; background: transparent; border: none;
                    padding: 8px; text-align: left;
                }
                QPushButton:hover { background-color: #444; }
                """
            )
            menu_layout.addWidget(btn)

        # ---------- páginas ----------
        self.pages = QStackedWidget()
        self.page_library = LibraryPage(self._store)
        self.page_edit = EditPage()

        self.pages.addWidget(self.page_library)
        self.pages.addWidget(self.page_edit)

        # ---------- layout raíz ----------
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self.menu_frame)
        root_layout.addWidget(self.pages)

        container = QWidget()
        container.setLayout(root_layout)
        self.setCentralWidget(container)

        # ---------- conexiones ----------
        self.btn_toggle.clicked.connect(self._toggle_menu)
        self.btn_library.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.page_library)
        )
        self.btn_edit.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.page_edit)
        )

        # ---------- bandeja ----------
        self._init_tray()

    # ------------------------------------------------------------------
    # Icono helper
    # ------------------------------------------------------------------
    def _icon_for(self, text: str) -> QIcon:
        style = cast(QStyle, self.style())
        return {
            "Menú": style.standardIcon(style.StandardPixmap.SP_FileDialogListView),
            "Librería": style.standardIcon(style.StandardPixmap.SP_DirIcon),
            "Panel de Edición": style.standardIcon(style.StandardPixmap.SP_DesktopIcon),
        }.get(text, QIcon())

    # ------------------------------------------------------------------
    # Animar menú
    # ------------------------------------------------------------------
    def _toggle_menu(self) -> None:
        anim = QPropertyAnimation(self.menu_frame, b"minimumWidth", self)
        anim.setDuration(300)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        if self._menu_expanded:
            anim.setStartValue(self.EXPANDED)
            anim.setEndValue(self.COLLAPSED)
            for btn in self.menu_buttons:
                btn.setText("")
        else:
            anim.setStartValue(self.COLLAPSED)
            anim.setEndValue(self.EXPANDED)
            for btn, text in self.menu_buttons.items():
                btn.setText(text)

        anim.start()
        self._menu_anim = anim
        self._menu_expanded = not self._menu_expanded

    # ------------------------------------------------------------------
    # Bandeja
    # ------------------------------------------------------------------
    def _init_tray(self) -> None:
        style = cast(QStyle, self.style())
        icon = style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)

        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("DesktopGIF")

        menu = QMenu()
        menu.addAction("Mostrar", self._restore_from_tray)
        menu.addAction("Salir", self.close)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def _restore_from_tray(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    # ------------------------------------------------------------------
    # Minimizar a bandeja
    # ------------------------------------------------------------------
    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.WindowStateChange and self.isMinimized():
            QTimer.singleShot(0, self.hide)
            self.tray.showMessage(
                "Minimizado",
                "DesktopGIF sigue ejecutándose.",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )
        super().changeEvent(event)
