from PyQt6.QtWidgets import QLineEdit, QSizePolicy

class URLBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Tamanho fixo base similar ao Firefox/Chrome
        # Usamos setMinimumWidth e setMaximumWidth para evitar que a animação anterior cause bugs
        self.setMinimumWidth(150)
        self.setMaximumWidth(800)
        
        # Policy para tentar ocupar o espaço disponível mas respeitando os limites acima
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
    def sizeHint(self):
        size = super().sizeHint()
        # Sugestão de tamanho padrão "ideal"
        size.setWidth(600)
        return size
