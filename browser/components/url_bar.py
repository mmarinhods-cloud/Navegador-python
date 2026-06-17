from PyQt6.QtWidgets import QLineEdit, QSizePolicy
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty

class AnimatedUrlBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.collapsed_width = 620
        self.expanded_width = 920
        
        # Variável interna para controlar a animação
        self._anim_width = self.collapsed_width
        
        # 1. GARANTE que a barra possa encolher para redimensionar a janela livremente
        self.setMinimumWidth(150) # Você pode ajustar esse valor mínimo se quiser
        
        # 2. "Maximum" avisa o layout: "Eu quero ter o tamanho do meu sizeHint, 
        # mas se a janela for menor, eu deixo me encolherem."
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        
        self.anim = QPropertyAnimation(self, b"anim_width")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    # 3. Criamos uma propriedade customizada para a animação reconhecer
    @pyqtProperty(int)
    def anim_width(self):
        return self._anim_width

    @anim_width.setter
    def anim_width(self, val):
        self._anim_width = val
        self.updateGeometry() # Avisa o layout a cada frame que o tamanho ideal mudou

    # 4. Sobrescrevemos o sizeHint para ditar o ritmo da expansão
    def sizeHint(self):
        size = super().sizeHint()
        size.setWidth(self._anim_width)
        return size

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.anim.stop()
        self.anim.setStartValue(self._anim_width)
        self.anim.setEndValue(self.expanded_width)
        self.anim.start()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.anim.stop()
        self.anim.setStartValue(self._anim_width)
        self.anim.setEndValue(self.collapsed_width)
        self.anim.start()