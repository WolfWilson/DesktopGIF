import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFrame, QLabel, QStackedWidget
)
# CORRECCIÓN 1: Se importa el objeto 'Qt' que faltaba
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSize, Qt
from PyQt6.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard con Menú Desplegable")
        self.setGeometry(100, 100, 900, 600)

        # Estado del menú: True = expandido, False = contraído
        self.menu_is_expanded = False

        # --- Layout Principal (horizontal) ---
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Panel del Menú Lateral (Izquierda) ---
        self.menu_frame = QFrame()
        self.menu_frame.setStyleSheet("background-color: #333;")
        self.menu_frame.setFixedWidth(60) # Ancho inicial (contraído)
        
        # Layout para los botones del menú (vertical)
        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(5, 5, 5, 5)
        menu_layout.setSpacing(10)
        # Se usa el objeto Qt importado
        menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Botones del Menú ---
        self.btn_toggle_menu = QPushButton("Menú")
        self.btn_home = QPushButton("Inicio")
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_settings = QPushButton("Ajustes")
        
        # Guardar los botones y sus textos originales
        self.menu_buttons = {
            self.btn_toggle_menu: "Menú",
            self.btn_home: "Inicio",
            self.btn_dashboard: "Dashboard",
            self.btn_settings: "Ajustes",
        }

        # Estilo y configuración de los botones
        for btn, text in self.menu_buttons.items():
            btn.setIcon(self.get_icon_for_button(text))
            btn.setIconSize(QSize(32, 32))
            btn.setText("") # Ocultar texto inicialmente
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: transparent;
                    border: none;
                    text-align: left;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
            """)
            menu_layout.addWidget(btn)

        self.menu_frame.setLayout(menu_layout)
        
        # --- Área de Contenido Principal (Derecha) ---
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #f0f0f0;")

        # Crear páginas de ejemplo
        # Se usa el objeto Qt importado
        self.page_home = QLabel("<h1>Página de Inicio</h1>", alignment=Qt.AlignmentFlag.AlignCenter)
        self.page_dashboard = QLabel("<h1>Página del Dashboard</h1>", alignment=Qt.AlignmentFlag.AlignCenter)
        self.page_settings = QLabel("<h1>Página de Ajustes</h1>", alignment=Qt.AlignmentFlag.AlignCenter)

        self.content_area.addWidget(self.page_home)
        self.content_area.addWidget(self.page_dashboard)
        self.content_area.addWidget(self.page_settings)

        # --- Ensamblar Layout Principal ---
        main_layout.addWidget(self.menu_frame)
        main_layout.addWidget(self.content_area)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # --- Conexiones ---
        self.btn_toggle_menu.clicked.connect(self.toggle_menu)
        self.btn_home.clicked.connect(lambda: self.content_area.setCurrentWidget(self.page_home))
        self.btn_dashboard.clicked.connect(lambda: self.content_area.setCurrentWidget(self.page_dashboard))
        self.btn_settings.clicked.connect(lambda: self.content_area.setCurrentWidget(self.page_settings))

    # CORRECCIÓN 2: Se añade una comprobación para evitar el error con self.style()
    def get_icon_for_button(self, text):
        style = self.style()
        if not style:
            return QIcon() # Devuelve un ícono vacío si el estilo no está disponible

        if text == "Menú":
            return style.standardIcon(style.StandardPixmap.SP_FileDialogListView)
        elif text == "Inicio":
            return style.standardIcon(style.StandardPixmap.SP_ComputerIcon)
        elif text == "Dashboard":
            return style.standardIcon(style.StandardPixmap.SP_DesktopIcon)
        elif text == "Ajustes":
            return style.standardIcon(style.StandardPixmap.SP_BrowserReload)
        return QIcon()

    def toggle_menu(self):
        collapsed_width = 60
        expanded_width = 200

        # Crear la animación
        self.animation = QPropertyAnimation(self.menu_frame, b"minimumWidth")
        self.animation.setDuration(300) # Duración en milisegundos
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        if self.menu_is_expanded:
            # --- Contraer Menú ---
            self.animation.setStartValue(expanded_width)
            self.animation.setEndValue(collapsed_width)
            # Ocultar texto de los botones
            for btn in self.menu_buttons:
                btn.setText("")
        else:
            # --- Expandir Menú ---
            self.animation.setStartValue(collapsed_width)
            self.animation.setEndValue(expanded_width)
            # Mostrar texto de los botones
            for btn, text in self.menu_buttons.items():
                btn.setText(text)

        self.animation.start()
        self.menu_is_expanded = not self.menu_is_expanded

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())