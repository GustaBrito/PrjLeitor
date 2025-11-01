import os
import sys
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon
from app import run_flask  # Importa a função para rodar o Flask

sys.dont_write_bytecode = True # Desativa o __pycache__

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class FlaskThread(threading.Thread):
    """Thread para rodar o Flask sem bloquear a UI."""
    def run(self):
        run_flask()

def resource_path(relative_path):
    """Retorna o caminho absoluto para recursos, mesmo quando empacotado."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Leitor - Desktop")
        self.resize(1920, 1080)
        self.center_window()
        icon_path = "./src/utils/icons/Leitor.ico" 
        self.setWindowIcon(QIcon(icon_path)) 

    def center_window(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        
        self.move(x, y)

        # Criar um widget de navegador embutido
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://127.0.0.1:5000"))   # Carrega a interface Flask

        # Layout da interface
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

# Iniciar o Flask em uma thread separada
flask_thread = FlaskThread()
flask_thread.daemon = True
flask_thread.start()

# Iniciar a aplicação Qt
app = QApplication(sys.argv)
window = MainWindow()
window.showMaximized()
sys.exit(app.exec())
