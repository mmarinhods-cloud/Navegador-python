from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (QHBoxLayout, QWidget, QPushButton, QLabel, 
                             QGraphicsDropShadowEffect)

class CustomTabButton(QWidget):
    clicked = pyqtSignal(str)
    close_requested = pyqtSignal(str)

    def __init__(self, tab_id, title, theme="light", parent=None):
        super().__init__(parent)
        self.tab_id = tab_id
        self.is_selected = False
        self.theme = theme
        self.raw_title = title
        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(32)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(6)
        
        self.label_icon = QLabel()
        self.label_icon.setFixedSize(16, 16)
        self.label_icon.setScaledContents(True)
        self.label_icon.setVisible(False)
        
        self.label_title = QLabel(title)
        self.label_title.setStyleSheet("background: transparent; font-size: 12px;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(16, 16)
        self.btn_close.clicked.connect(lambda: self.close_requested.emit(self.tab_id))
        
        self.layout.addWidget(self.label_icon, 0, Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_title, 1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.btn_close, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.update_style()

    def set_theme(self, theme):
        self.theme = theme
        self.update_style()

    def set_text(self, text):
        self.raw_title = text
        self.adjust_content_visibility()

    def set_icon(self, icon):
        if icon and not icon.isNull():
            pixmap = icon.pixmap(16, 16)
            self.label_icon.setPixmap(pixmap)
            self.label_icon.setVisible(True)
        else:
            self.label_icon.setVisible(False)
        self.adjust_content_visibility()

    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()

    def adjust_content_visibility(self):
        try:
            if self.width() < 65:
                self.label_title.setVisible(False)
                self.btn_close.setVisible(False)
            else:
                self.label_title.setVisible(True)
                self.btn_close.setVisible(True)
                
                max_chars = max(3, int((self.width() - 50) / 7))
                if len(self.raw_title) > max_chars:
                    self.label_title.setText(self.raw_title[:max_chars] + "...")
                else:
                    self.label_title.setText(self.raw_title)
        except RuntimeError:
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_content_visibility()

    def update_style(self):
        try:
            if self.theme == "light":
                self.btn_close.setStyleSheet("""
                    QPushButton { border: none; border-radius: 8px; background: transparent; color: #555555; font-size: 8px; font-weight: bold; }
                    QPushButton:hover { background-color: rgba(0, 0, 0, 0.1); color: #000000; }
                """)
                if self.is_selected:
                    self.setStyleSheet("""
                        CustomTabButton { background-color: #ffffff; border: 1px solid #d0d0d0; border-bottom: 2px solid #007aff; border-radius: 8px; }
                        QLabel { color: #111111; font-weight: bold; background: transparent; }
                    """)
                else:
                    self.setStyleSheet("""
                        CustomTabButton { background-color: transparent; border: 1px solid transparent; border-radius: 8px; }
                        CustomTabButton:hover { background-color: rgba(0, 0, 0, 0.06); }
                        QLabel { color: #5f6368; background: transparent; }
                        CustomTabButton:hover QLabel { color: #111111; font-weight: normal; }
                    """)
            else:
                self.btn_close.setStyleSheet("""
                    QPushButton { border: none; border-radius: 8px; background: transparent; color: #aaaaaa; font-size: 8px; font-weight: bold; }
                    QPushButton:hover { background-color: rgba(255, 255, 255, 0.15); color: #ffffff; }
                """)
                if self.is_selected:
                    self.setStyleSheet("""
                        CustomTabButton { background-color: #2b2d31; border: 1px solid #454545; border-bottom: 2px solid #0a84ff; border-radius: 8px; }
                        QLabel { color: #ffffff; font-weight: bold; background: transparent; }
                    """)
                else:
                    self.setStyleSheet("""
                        CustomTabButton { background-color: transparent; border: 1px solid transparent; border-radius: 8px; }
                        CustomTabButton:hover { background-color: rgba(255, 255, 255, 0.08); }
                        QLabel { color: #9aa0a6; background: transparent; }
                        CustomTabButton:hover QLabel { color: #ffffff; }
                    """)
        except RuntimeError:
            pass

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.tab_id)
        super().mousePressEvent(event)


class CustomTabBar(QWidget):
    currentChanged = pyqtSignal(int)
    tabCloseRequested = pyqtSignal(int)
    layoutUpdated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CustomTabBar")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 4, 8, 4)
        self.layout.setSpacing(6)
        
        self.tabs_list = []
        self.current_idx = -1
        self.theme = "light"

    def set_theme(self, theme):
        self.theme = theme
        for tab in self.tabs_list:
            tab.set_theme(theme)

    def addTab(self, tab_id, title):
        tab = CustomTabButton(tab_id, title, theme=self.theme)
        tab.clicked.connect(self.on_tab_clicked)
        tab.close_requested.connect(self.on_tab_close_requested)
        
        self.layout.addWidget(tab)
        self.tabs_list.append(tab)
        
        self.recalculate_tab_sizes()
        return len(self.tabs_list) - 1

    def on_tab_clicked(self, tab_id):
        idx = self.get_index_by_id(tab_id)
        if idx != -1:
            self.setCurrentIndex(idx)

    def on_tab_close_requested(self, tab_id):
        idx = self.get_index_by_id(tab_id)
        if idx != -1:
            self.tabCloseRequested.emit(idx)

    def get_index_by_id(self, tab_id):
        for i, tab in enumerate(self.tabs_list):
            try:
                if tab.tab_id == tab_id:
                    return i
            except RuntimeError:
                continue
        return -1

    def tabData(self, index):
        if 0 <= index < len(self.tabs_list):
            try:
                return self.tabs_list[index].tab_id
            except RuntimeError:
                return None
        return None

    def count(self):
        return len(self.tabs_list)

    def currentIndex(self):
        return self.current_idx

    def setCurrentIndex(self, index):
        if 0 <= index < len(self.tabs_list):
            self.current_idx = index
            for i, tab in enumerate(self.tabs_list):
                try:
                    tab.set_selected(i == index)
                except RuntimeError:
                    continue
            self.currentChanged.emit(index)

    def removeTab(self, index):
        if 0 <= index < len(self.tabs_list):
            tab = self.tabs_list.pop(index)
            try:
                tab.setGraphicsEffect(None)
                self.layout.removeWidget(tab)
                tab.deleteLater()
            except RuntimeError:
                pass
            
            if self.current_idx >= len(self.tabs_list):
                self.current_idx = len(self.tabs_list) - 1
            
            if self.current_idx >= 0:
                self.setCurrentIndex(self.current_idx)
                
            self.recalculate_tab_sizes()

    def setTabText(self, index, text):
        if 0 <= index < len(self.tabs_list):
            self.tabs_list[index].set_text(text)

    def setTabIcon(self, index, icon):
        if 0 <= index < len(self.tabs_list):
            self.tabs_list[index].set_icon(icon)

    def recalculate_tab_sizes(self):
        num_tabs = len(self.tabs_list)
        if num_tabs == 0: return

        main_win = self.window()
        if main_win and main_win.width() > 100:
            max_available_space = main_win.width() - 240
        else:
            max_available_space = 800

        max_tabs_space = max_available_space - 40
        target_width = int(max_tabs_space / num_tabs)
        target_width = max(45, min(180, target_width))
        
        total_needed_width = 0
        for tab in self.tabs_list:
            try:
                tab.setFixedWidth(target_width)
                total_needed_width += target_width + 6
            except RuntimeError:
                continue

        if total_needed_width > max_tabs_space:
            self.setFixedWidth(max_tabs_space)
        else:
            self.setFixedWidth(total_needed_width)
            
        self.layoutUpdated.emit()
