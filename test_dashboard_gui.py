import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QFileDialog, QLabel
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView

# --- Lógica de PDF (simulada para pruebas de GUI) ---
def merge_pdfs(base_pdf_path, files_to_annex, output_path):
    """Función de marcador de posición."""
    print("--- SIMULACIÓN ---")
    print(f"Llamado a 'merge_pdfs' con el archivo base: {base_pdf_path}")
    print(f"Archivos a anexar: {files_to_annex}")
    print(f"El archivo de salida sería: {output_path}")
    print("--------------------")

def sign_pdf(pdf_path, signature_image_path, output_path, position):
    """Función de marcador de posición."""
    print("--- SIMULACIÓN ---")
    print(f"Llamado a 'sign_pdf' para el archivo: {pdf_path}")
    print(f"Usando la firma: {signature_image_path}")
    print(f"La posición de la firma sería: {position}")
    print(f"El archivo de salida sería: {output_path}")
    print("--------------------")

# --- Widget del Visor de PDF ---
class PdfViewer(QWebEngineView):
    """Un widget para mostrar archivos PDF usando el motor web de Qt."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings().setAttribute(self.settings().WebAttribute.PluginsEnabled, True)
        self.settings().setAttribute(self.settings().WebAttribute.PdfViewerEnabled, True)

    def load_pdf(self, file_path):
        if os.path.exists(file_path):
            url = QUrl.fromLocalFile(file_path)
            self.load(url)
        else:
            self.setHtml(f"<h1>Error: Archivo no encontrado</h1><p>{file_path}</p>")

# --- Ventana Principal del Dashboard ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard de Gestión de Expedientes (Prueba GUI)")
        self.setGeometry(100, 100, 1200, 800)
        self.current_pdf_path = None

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Panel de menú a la izquierda
        menu_panel = QWidget()
        menu_panel.setStyleSheet("background-color: #2c3e50; color: white;")
        menu_panel.setFixedWidth(220)
        
        menu_layout = QVBoxLayout()
        menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Área de contenido a la derecha
        self.content_area = QStackedWidget()

        # Botones del Menú
        self.btn_open_pdf = QPushButton("Abrir Expediente")
        self.btn_annex = QPushButton("Anexar Archivos")
        self.btn_sign = QPushButton("Firmar Documento")
        
        for btn in [self.btn_open_pdf, self.btn_annex, self.btn_sign]:
            btn.setStyleSheet("""
                QPushButton { 
                    text-align: left; 
                    padding: 12px; 
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover { background-color: #34495e; }
            """)
        
        menu_layout.addWidget(self.btn_open_pdf)
        menu_layout.addWidget(self.btn_annex)
        menu_layout.addWidget(self.btn_sign)
        menu_panel.setLayout(menu_layout)
        
        # Contenido de las Páginas
        self.pdf_viewer_widget = PdfViewer()
        self.placeholder_page = QLabel("<h1>Seleccione un expediente para comenzar</h1>", alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_area.addWidget(self.placeholder_page)
        self.content_area.addWidget(self.pdf_viewer_widget)

        # Ensamblado final
        main_layout.addWidget(menu_panel)
        main_layout.addWidget(self.content_area)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Conectar Señales
        self.btn_open_pdf.clicked.connect(self.open_pdf_file)
        self.btn_annex.clicked.connect(self.annex_files_to_pdf)
        self.btn_sign.clicked.connect(self.sign_current_pdf)
    
    def open_pdf_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Expediente PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.current_pdf_path = file_path
            self.pdf_viewer_widget.load_pdf(file_path)
            self.content_area.setCurrentWidget(self.pdf_viewer_widget)

    def annex_files_to_pdf(self):
        if not self.current_pdf_path:
            print("UI Test: Se necesita un PDF base para anexar.")
            return
            
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar PDFs para Anexar", "", "PDF Files (*.pdf)")
        if files:
            output_path, _ = QFileDialog.getSaveFileName(self, "Guardar Expediente Unificado", "", "PDF Files (*.pdf)")
            if output_path:
                merge_pdfs(self.current_pdf_path, files, output_path)

    def sign_current_pdf(self):
        if not self.current_pdf_path:
            print("UI Test: Se necesita un PDF para firmar.")
            return

        sig_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen de Firma", "", "Image Files (*.png *.jpg)")
        if sig_path:
            output_path, _ = QFileDialog.getSaveFileName(self, "Guardar Expediente Firmado", "", "PDF Files (*.pdf)")
            if output_path:
                position = (400, 650, 550, 750)
                sign_pdf(self.current_pdf_path, sig_path, output_path, position)

# --- Punto de Entrada de la Aplicación ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())