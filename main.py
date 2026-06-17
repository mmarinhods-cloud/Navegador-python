import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from browser.window import AdvancedMacBrowser
from browser.utils.helpers import ensure_directories

def main():
    # Identificador para barra de tarefas do Windows
    try:
        myappid = 'matheus.browser.v2'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    ensure_directories()

    app = QApplication(sys.argv)
    app.setApplicationName("Matheus browser")
    
    window = AdvancedMacBrowser()
    
    # window.show()  <- Removido pois a janela já decide como abrir (maximizado ou normal) no seu __init__
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
