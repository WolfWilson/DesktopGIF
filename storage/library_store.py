#!/usr/bin/env python
# coding: utf-8
#storage/library_store.py
"""
storage/library_store.py – Persiste la librería de GIFs en JSON.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

CONFIG_FILE = Path(__file__).parent / "library.json"


@dataclass
class GifEntry:
    path: str            # ruta absoluta, única
    scale: int = 100
    pos_x: int = 100
    pos_y: int = 100


class LibraryStore:
    """Carga y guarda objetos GifEntry – evita duplicados."""

    def __init__(self) -> None:
        self._items: Dict[str, GifEntry] = {}
        self.load()

    # ---------- API ----------
    def items(self) -> List[GifEntry]:
        return list(self._items.values())

    def add(self, raw_path: str) -> None:
        path = str(Path(raw_path).resolve())
        if path not in self._items:
            self._items[path] = GifEntry(path)
            self.save()

    def remove(self, raw_path: str) -> None:
        path = str(Path(raw_path).resolve())
        if path in self._items:
            del self._items[path]
            self.save()

    def update(self, entry: GifEntry) -> None:
        self._items[entry.path] = entry
        self.save()

    def get(self, raw_path: str) -> GifEntry | None:
        return self._items.get(str(Path(raw_path).resolve()))

    # ---------- persistencia ----------
    def load(self) -> None:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._items = {d["path"]: GifEntry(**d) for d in data}

    def save(self) -> None:
        data = [asdict(e) for e in self._items.values()]
        CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
