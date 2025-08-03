"""
Hoja de estilos (QSS) para DesktopGIF.

Puedes modificar colores, fuentes y tamaños sin alterar la lógica.
"""

APP_STYLE = """
/* === Raíz === */
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", "Helvetica", "Arial", sans-serif;
    font-size: 10pt;
}

/* === Etiquetas === */
QLabel#titleLabel {
    font-size: 12pt;
    font-weight: 600;
}
QLabel#infoLabel {
    color: #c0c0c0;
}

/* === Botones === */
QPushButton {
    background-color: #2e7d32;           /* Verde principal */
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    color: #ffffff;
    font-weight: 600;
}
QPushButton:hover  { background-color: #389e3c; }
QPushButton:pressed{ background-color: #27682c; }
QPushButton:disabled {
    background-color: #444444;
    color: #aaaaaa;
}

/* === SpinBox === */
QSpinBox {
    background: #2b2b2b;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 2px 6px;
    min-width: 70px;
}
QSpinBox::up-button,
QSpinBox::down-button {
    width: 16px;
    background: #323232;
    border: none;
}
QSpinBox::up-button:hover,
QSpinBox::down-button:hover { background: #3d3d3d; }
"""
