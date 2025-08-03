#!/usr/bin/env python
# coding: utf-8
"""
ui/library_page.py – Librería persistente con miniaturas de GIF.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, cast

from PyQt6.QtCore import QPoint, Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QKeyEvent, QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QStyle,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from modules.overlay import GifOverlay
from storage.library_store import GifEntry, LibraryStore
from utils.gif_utils import first_frame_as_pixmap


class LibraryPage(QWidget):
    """Página con la librería de GIFs importados."""

    THUMB_SIZE = QSize(96, 96)

    def __init__(self, store: LibraryStore) -> None:
        super().__init__()
        self._store = store
        self._overlay: GifOverlay | None = None

        # ---------- barra de herramientas ----------
        self.toolbar = QToolBar()
        act_add = QAction("Cargar", self)
        style = cast(QStyle, self.style())
        act_add.setIcon(style.standardIcon(style.StandardPixmap.SP_DialogOpenButton))
        self.toolbar.addAction(act_add)

        # ---------- lista ----------
        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setIconSize(self.THUMB_SIZE)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setSpacing(10)
        self.list_widget.setMovement(QListWidget.Movement.Static)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.list_widget)

        # ---------- conexiones ----------
        act_add.triggered.connect(self._add_gifs)
        self.list_widget.customContextMenuRequested.connect(self._show_menu)
        self.list_widget.installEventFilter(self)

        # ---------- carga inicial ----------
        for entry in self._store.items():
            self._add_item(Path(entry.path))

    # ===================================================
    # Slots
    # ===================================================
    def _add_gifs(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Agregar GIF(s)", "", "GIF Files (*.gif)"
        )
        for p in paths:
            self._store.add(p)
            self._add_item(Path(p))

    def _show_menu(self, pos: QPoint) -> None:
        item = self.list_widget.itemAt(pos)
        if item is None:
            return

        menu = QMenu(self)
        act_run = menu.addAction("Ejecutar")
        act_del = menu.addAction("Eliminar")
        chosen = menu.exec(self.list_widget.mapToGlobal(pos))

        if chosen is act_run:
            self._execute(item)
        elif chosen is act_del:
            self._remove_item(item)

    # ---------- ejecutar ----------
    def _execute(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        entry = self._store.get(path) or GifEntry(path)

        if self._overlay and self._overlay.isVisible():
            self._overlay.close()

        self._overlay = GifOverlay(
            gif_path=entry.path,
            scale_percent=entry.scale,
            opacity=entry.opacity,
            on_close=lambda x, y, s, o: self._save_state(entry.path, x, y, s, o),
        )
        self._overlay.move(entry.pos_x, entry.pos_y)
        self._overlay.show()

    def _save_state(self, path: str, x: int, y: int, scale: int, opacity: float) -> None:
        entry = self._store.get(path) or GifEntry(path)
        entry.pos_x, entry.pos_y, entry.scale, entry.opacity = x, y, scale, opacity
        self._store.update(entry)

    # ---------- CRUD ----------
    def _add_item(self, path: Path) -> None:
        # Evita duplicados visuales
        if any(Path(i.data(Qt.ItemDataRole.UserRole)).resolve() == path.resolve()
               for i in self._iter_items()):
            return

        pix: QPixmap = first_frame_as_pixmap(path, self.THUMB_SIZE)
        icon = QIcon(pix)
        item = QListWidgetItem(icon, "")
        item.setData(Qt.ItemDataRole.UserRole, str(path.resolve()))
        item.setToolTip(path.name)
        self.list_widget.addItem(item)

    def _remove_item(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        self._store.remove(path)
        self.list_widget.takeItem(self.list_widget.row(item))

    # ---------- util ----------
    def _iter_items(self) -> Iterator[QListWidgetItem]:
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item is not None:
                yield item

    # ---------- tecla Supr ----------
    def eventFilter(self, src, evt):  # noqa: ANN001
        if src is self.list_widget and isinstance(evt, QKeyEvent):
            if evt.key() == Qt.Key.Key_Delete and (item := self.list_widget.currentItem()):
                self._remove_item(item)
                return True
        return super().eventFilter(src, evt)
