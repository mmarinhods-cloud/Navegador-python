import os
import sys
import uuid
import ctypes
from PyQt6.QtCore import QUrl, QSize, Qt, QPoint, QTimer, QRect
from PyQt6.QtGui import QIcon, QColor, QCursor, QScreen
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QStackedWidget,
                             QMenu, QSizePolicy)
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView

from .components.url_bar import URLBar
from .components.tabs import CustomTabBar
from .components.dialogs import MacInputDialog
from .core.interceptor import AdBlockerInterceptor
from .core.web_page import AdvancedWebPage
from .utils.helpers import get_favorites, save_favorites, get_settings, save_settings, MALICIOUS_DOMAINS

class AdvancedMacBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matheus browser")
        self.setMinimumSize(400, 300)
        
        # Carregar configurações
        self.settings = get_settings()
        self.first_restore_done = self.settings.get("first_restore_done", False)

        if os.path.exists("image.png"):
            self.setWindowIcon(QIcon("image.png"))

        # Configurações de janela Frameless
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.BORDER_MARGIN = 8
        self.drag_position = None
        self.resize_direction = None
        self.setMouseTracking(True) 

        self.malicious_domains = MALICIOUS_DOMAINS
        self.bypassed_sites = set()
        self.tabs_map = {} 
        self.current_theme = self.settings.get("theme", "light")

        self.ad_blocker = AdBlockerInterceptor()
        QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(self.ad_blocker)

        self.main_widget = QWidget()
        self.main_widget.setObjectName("MainWidget")
        self.main_widget.setMouseTracking(True) 
        self.setCentralWidget(self.main_widget)
        
        self.central_layout = QVBoxLayout(self.main_widget)
        self.central_layout.setContentsMargins(10, 10, 10, 10) 
        self.central_layout.setSpacing(0)

        self.window_container = QWidget()
        self.window_container.setObjectName("WindowContainer")
        self.central_layout.addWidget(self.window_container)

        self.main_layout = QVBoxLayout(self.window_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Timer para debounce do resize
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.handle_resize_finished)

        self.init_ui_components()
        self.apply_theme_stylesheet()
        self.render_favorites_bar()

        # Restaurar geometria
        self.restore_window_state()

        self.add_new_tab(QUrl("https://mthsantos.vercel.app/"), "Home")
        
        # Aplicar sombra nativa do Windows (com pequeno atraso para garantir que a janela esteja pronta)
        QTimer.singleShot(100, self.set_native_shadow)

    def set_native_shadow(self):
        if sys.platform == "win32":
            try:
                class MARGINS(ctypes.Structure):
                    _fields_ = [("cxLeftWidth", ctypes.c_int),
                                ("cxRightWidth", ctypes.c_int),
                                ("cyTopHeight", ctypes.c_int),
                                ("cyBottomHeight", ctypes.c_int)]
                
                # -1 em todos os lados habilita a sombra DWM completa
                margins = MARGINS(-1, -1, -1, -1)
                hwnd = int(self.winId())
                ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))
            except Exception as e:
                print(f"Erro ao aplicar sombra nativa: {e}")

    def restore_window_state(self):
        geom = self.settings.get("geometry")
        maximized = self.settings.get("maximized", True)

        on_screen = False
        if geom:
            rect = QRect(geom[0], geom[1], geom[2], geom[3])
            title_rect = QRect(rect.x(), rect.y(), 100, 50)
            
            for screen in QApplication.screens():
                if screen.geometry().intersects(title_rect):
                    on_screen = True
                    break
            
            if on_screen:
                if maximized:
                    # Para janelas que vão maximizar, apenas pre-setamos o tamanho/posição de restauração
                    # sem chamar setGeometry completo para evitar avisos no Windows
                    self.resize(rect.size())
                    self.move(rect.topLeft())
                else:
                    self.setGeometry(rect)
            else:
                self.resize(1280, 850)
        else:
            self.resize(1280, 850)

        # Aplicar tema ANTES de mostrar para evitar flickering, mas sem margens ainda
        self.apply_theme_stylesheet()

        if maximized:
            self.btn_win_max.setText("⤡")
            self.central_layout.setContentsMargins(0, 0, 0, 0)
            self.showMaximized()
        else:
            self.btn_win_max.setText("⤢")
            self.central_layout.setContentsMargins(10, 10, 10, 10)
            self.show()
            if not on_screen:
                self.center_on_screen()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        geo = self.geometry()
        x = (screen.width() - geo.width()) // 2
        y = (screen.height() - geo.height()) // 2
        self.move(x, y)

    def save_window_state(self):
        # Apenas salvar geometria se a janela não estiver maximizada
        if not self.isMaximized():
            geom = self.geometry()
            self.settings["geometry"] = [geom.x(), geom.y(), geom.width(), geom.height()]
        
        self.settings["maximized"] = self.isMaximized()
        self.settings["theme"] = self.current_theme
        self.settings["first_restore_done"] = self.first_restore_done
        save_settings(self.settings)

    def init_ui_components(self):
        self.top_tabs_widget = QWidget()
        self.top_tabs_widget.setObjectName("TopTitleBar")
        self.top_tabs_widget.setMouseTracking(True)
        self.top_tabs_layout = QHBoxLayout(self.top_tabs_widget)
        self.top_tabs_layout.setContentsMargins(12, 0, 0, 0)
        self.top_tabs_layout.setSpacing(0) 

        self.tabs_container_widget = QWidget()
        self.tabs_container_layout = QHBoxLayout(self.tabs_container_widget)
        self.tabs_container_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs_container_layout.setSpacing(0)

        self.tab_bar = CustomTabBar(self.tabs_container_widget)
        self.tabs_container_layout.addWidget(self.tab_bar)
        
        self.btn_new_tab = QPushButton("＋")
        self.btn_new_tab.setFixedSize(28, 28)
        self.btn_new_tab.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_new_tab.setObjectName("btn_add_tab_top")
        self.btn_new_tab.clicked.connect(lambda: self.add_new_tab(QUrl("https://www.google.com"), "Nova Aba"))
        
        self.tabs_container_layout.addWidget(self.btn_new_tab, 0, Qt.AlignmentFlag.AlignVCenter)
        self.tabs_container_layout.addStretch(1)
        
        self.btn_list_tabs = QPushButton("⌃") 
        self.btn_list_tabs.setFixedSize(28, 28)
        self.btn_list_tabs.setObjectName("btn_list_tabs")
        self.btn_list_tabs.clicked.connect(self.show_all_tabs_menu)

        self.top_tabs_layout.addWidget(self.tabs_container_widget, 1, Qt.AlignmentFlag.AlignBottom)
        self.top_tabs_layout.addWidget(self.btn_list_tabs, 0, Qt.AlignmentFlag.AlignVCenter)
        self.top_tabs_layout.addSpacing(10)

        self.tab_bar.layoutUpdated.connect(self.adjust_plus_button_position)

        self.window_controls_widget = QWidget()
        self.window_controls_layout = QHBoxLayout(self.window_controls_widget)
        self.window_controls_layout.setContentsMargins(0, 0, 0, 0)
        self.window_controls_layout.setSpacing(0)

        self.btn_win_min = QPushButton("─")
        self.btn_win_max = QPushButton("⤢")
        self.btn_win_close = QPushButton("✕")

        for btn in [self.btn_win_min, self.btn_win_max, self.btn_win_close]:
            btn.setFixedSize(45, 38)
            btn.setObjectName("WindowControlButton")

        self.btn_win_close.setObjectName("WindowControlClose")
        self.btn_win_min.clicked.connect(self.showMinimized)
        self.btn_win_max.clicked.connect(self.toggle_maximize_restore)
        self.btn_win_close.clicked.connect(self.close)

        self.window_controls_layout.addWidget(self.btn_win_min)
        self.window_controls_layout.addWidget(self.btn_win_max)
        self.window_controls_layout.addWidget(self.btn_win_close)

        self.top_tabs_layout.addWidget(self.window_controls_widget, 0, Qt.AlignmentFlag.AlignTop)
        self.main_layout.addWidget(self.top_tabs_widget)

        self.nav_bar_widget = QWidget()
        self.nav_bar_widget.setObjectName("NavBarWidget")
        self.nav_bar = QHBoxLayout(self.nav_bar_widget)
        self.nav_bar.setContentsMargins(12, 6, 12, 6)
        self.nav_bar.setSpacing(6)

        self.btn_back = QPushButton("‹")
        self.btn_forward = QPushButton("›")
        self.btn_reload = QPushButton("↻")
        self.btn_add_fav = QPushButton("☆")
        self.btn_settings = QPushButton("≡") 

        for btn in [self.btn_back, self.btn_forward, self.btn_reload, self.btn_add_fav, self.btn_settings]:
            btn.setFixedSize(32, 32)
            btn.setObjectName("btn_nav")

        self.url_bar = URLBar()
        self.url_bar.setPlaceholderText("Busque ou digite uma URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.nav_bar.addWidget(self.btn_back)
        self.nav_bar.addWidget(self.btn_forward)
        self.nav_bar.addWidget(self.btn_reload)
        self.nav_bar.addStretch(1)
        self.nav_bar.addWidget(self.url_bar)
        self.nav_bar.addStretch(1)
        self.nav_bar.addWidget(self.btn_add_fav)
        self.nav_bar.addWidget(self.btn_settings)

        self.main_layout.addWidget(self.nav_bar_widget)

        self.fav_bar_widget = QWidget()
        self.fav_bar_widget.setObjectName("FavBar")
        self.fav_bar_layout = QHBoxLayout(self.fav_bar_widget)
        self.fav_bar_layout.setContentsMargins(12, 4, 12, 6)
        self.fav_bar_layout.setSpacing(8)
        self.fav_bar_layout.addStretch() 

        self.main_layout.addWidget(self.fav_bar_widget)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("StackedWidget")
        self.main_layout.addWidget(self.stacked_widget)

        self.tab_bar.currentChanged.connect(self.tab_changed)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.btn_back.clicked.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        self.btn_forward.clicked.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        self.btn_reload.clicked.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        self.btn_add_fav.clicked.connect(self.add_current_to_favorites)
        self.btn_settings.clicked.connect(self.show_settings_menu)

    def adjust_plus_button_position(self):
        max_allowed_width = self.width() - 240
        if max_allowed_width > 0:
            self.tabs_container_widget.setMaximumWidth(max_allowed_width)
            self.tabs_container_widget.setMinimumWidth(0)

    def check_border_position(self, pos):
        if self.isMaximized():
            return None
            
        w, h = self.width(), self.height()
        x, y = pos.x(), pos.y()
        margin = self.BORDER_MARGIN

        top = y < margin
        bottom = y > h - margin
        left = x < margin
        right = x > w - margin

        if top and left: return "top_left"
        if top and right: return "top_right"
        if bottom and left: return "bottom_left"
        if bottom and right: return "bottom_right"
        if top: return "top"
        if bottom: return "bottom"
        if left: return "left"
        if right: return "right"
        return None

    def update_cursor_shape(self, direction):
        if direction in ["top", "bottom"]:
            self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        elif direction in ["left", "right"]:
            self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        elif direction in ["top_left", "bottom_right"]:
            self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        elif direction in ["top_right", "bottom_left"]:
            self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            direction = self.check_border_position(pos)
            
            if direction:
                self.resize_direction = direction
                self.drag_position = event.globalPosition().toPoint()
                self.initial_geometry = self.geometry()
                event.accept()
            elif pos.y() < 52: 
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self.resize_direction = None
                event.accept()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        global_pos = event.globalPosition().toPoint()

        if event.buttons() == Qt.MouseButton.NoButton:
            direction = self.check_border_position(pos)
            self.update_cursor_shape(direction)
            
        elif event.buttons() == Qt.MouseButton.LeftButton:
            if self.resize_direction:
                diff = global_pos - self.drag_position
                geo = self.initial_geometry
                
                x, y, w, h = geo.x(), geo.y(), geo.width(), geo.height()
                min_w = self.minimumSize().width()
                min_h = self.minimumSize().height()

                if "left" in self.resize_direction:
                    nw = w - diff.x()
                    if nw >= min_w:
                        x = geo.x() + diff.x()
                        w = nw
                elif "right" in self.resize_direction:
                    nw = w + diff.x()
                    if nw >= min_w: w = nw

                if "top" in self.resize_direction:
                    nh = h - diff.y()
                    if nh >= min_h:
                        y = geo.y() + diff.y()
                        h = nh
                elif "bottom" in self.resize_direction:
                    nh = h + diff.y()
                    if nh >= min_h: h = nh

                self.setGeometry(x, y, w, h)
                event.accept()
                
            elif self.drag_position is not None:
                if self.isMaximized():
                    local_x = self.drag_position.x()
                    width_before = self.width()
                    ratio = local_x / width_before if width_before > 0 else 0.5
                    
                    self.toggle_maximize_restore()
                    
                    new_local_x = int(ratio * self.width())
                    self.drag_position = QPoint(new_local_x, self.drag_position.y())
                    
                self.move(global_pos - self.drag_position)
                event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        self.resize_direction = None
        self.update_cursor_shape(None)
        self.save_window_state()
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Iniciar timer de debounce para operações pesadas
        self.resize_timer.start(10)

    def handle_resize_finished(self):
        if hasattr(self, 'tab_bar'):
            self.tab_bar.recalculate_tab_sizes()
            self.adjust_plus_button_position()

    def show_all_tabs_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(self.styleSheet())
        
        search_action = menu.addAction("🔍 Procurar abas")
        search_action.setEnabled(False)
        menu.addSeparator()
        
        for i in range(self.tab_bar.count()):
            tab_id = self.tab_bar.tabData(i)
            if not tab_id: continue
            browser = self.tabs_map.get(tab_id)
            if not browser: continue
            title = browser.title() if browser else "Nova Aba"
            icon = browser.icon() if browser else QIcon()
            
            action = menu.addAction(icon, title)
            action.triggered.connect(lambda checked, idx=i: self.tab_bar.setCurrentIndex(idx))
            
        menu.exec(self.btn_list_tabs.mapToGlobal(self.btn_list_tabs.rect().bottomLeft()))

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            if not self.check_border_position(pos) and pos.y() < 52:
                self.toggle_maximize_restore()
                event.accept()

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_win_max.setText("⤢")
            self.central_layout.setContentsMargins(10, 10, 10, 10) 
            
            if not self.first_restore_done:
                self.center_on_screen()
                self.first_restore_done = True
        else:
            self.showMaximized()
            self.btn_win_max.setText("⤡")
            self.central_layout.setContentsMargins(0, 0, 0, 0) 
            
        self.apply_theme_stylesheet()
        self.save_window_state()

    def show_settings_menu(self):
        menu = QMenu(self)
        
        theme_menu = menu.addMenu("Escolher Tema")
        action_light = theme_menu.addAction("Modo Claro")
        action_dark = theme_menu.addAction("Modo Escuro")
        
        action_light.triggered.connect(lambda: self.change_theme("light"))
        action_dark.triggered.connect(lambda: self.change_theme("dark"))
        
        menu.addSeparator()
        
        status_ad = "Ativo" if self.ad_blocker.active else "Inativo"
        action_toggle_ad = menu.addAction(f"Bloqueador de Anúncios: [ {status_ad} ]")
        action_toggle_ad.triggered.connect(self.toggle_ad_blocker)

        menu.exec(self.btn_settings.mapToGlobal(self.btn_settings.rect().bottomLeft()))

    def toggle_ad_blocker(self):
        self.ad_blocker.active = not self.ad_blocker.active
        if self.current_browser():
            self.current_browser().reload()

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.tab_bar.set_theme(theme_name)
        self.apply_theme_stylesheet()
        self.save_window_state()
        
        dark_mode_active = (theme_name == "dark")
        QWebEngineProfile.defaultProfile().settings().setAttribute(
            QWebEngineSettings.WebAttribute.ForceDarkMode, dark_mode_active
        )
        for browser in self.tabs_map.values():
            browser.settings().setAttribute(
                QWebEngineSettings.WebAttribute.ForceDarkMode, dark_mode_active
            )

    def apply_theme_stylesheet(self):
        radius = "0px" if self.isMaximized() else "12px"
        
        if self.current_theme == "light":
            self.setStyleSheet(f"""
                QMainWindow, QWidget#MainWidget {{ background: transparent; }}
                QWidget#WindowContainer {{ background-color: #eef1f6; color: #222222; border-radius: {radius}; }}
                QWidget#TopTitleBar {{ background-color: #eef1f6; border-top-left-radius: {radius}; border-top-right-radius: {radius}; border-bottom: 1px solid #d0d4dc; }}
                QWidget#NavBarWidget {{ background-color: #ffffff; border-bottom: 1px solid #e0e0e0; }}
                QWidget#FavBar {{ border-bottom: 1px solid #e5e5e5; background-color: #ffffff; }}
                QStackedWidget#StackedWidget {{ border-bottom-left-radius: {radius}; border-bottom-right-radius: {radius}; }}
                
                QLineEdit {{ padding: 5px 14px; border-radius: 6px; border: 1px solid #d0d0d0; background-color: #f0f2f5; color: #000000; font-size: 13px; }}
                QLineEdit:focus {{ border: 2px solid #007aff; background-color: #ffffff; }}
                
                QPushButton {{ border: none; border-radius: 4px; background-color: transparent; color: #333333; }}
                QPushButton:hover {{ background-color: #e5e5e5; }}
                
                QPushButton#btn_add_tab_top {{ font-size: 14px; color: #444444; background-color: transparent; border-radius: 6px; font-weight: bold; }}
                QPushButton#btn_add_tab_top:hover {{ background-color: rgba(0,0,0,0.08); color: #000000; }}
                
                QPushButton#btn_list_tabs {{ font-size: 14px; color: #444444; border-radius: 6px; background-color: transparent; }}
                QPushButton#btn_list_tabs:hover {{ background-color: #dbdbdb; }}
                
                QPushButton#btn_nav {{ font-size: 20px; color: #444444; border-radius: 6px; }}
                QPushButton#btn_nav:hover {{ background-color: #ededed; }}
                
                QPushButton#btn_fav_item {{ font-size: 12px; color: #444444; padding: 5px 10px; font-family: -apple-system, sans-serif; }}
                QPushButton#btn_fav_item:hover {{ background-color: #f0f0f0; border-radius: 6px; color: #000000; }}
                
                QPushButton#WindowControlButton {{ font-size: 11px; color: #555555; border-radius: 0px; background-color: transparent; }}
                QPushButton#WindowControlButton:hover {{ background-color: #e0e0e0; }}
                QPushButton#WindowControlClose:hover {{ background-color: #e11d48; color: white; }}
                
                QMenu {{ 
                    background-color: #ffffff; 
                    border: 1px solid #d2d2d7; 
                    padding: 6px; 
                    border-radius: 10px; 
                    color: #1d1d1f;
                    font-family: '.AppleSystemUIFont', 'SF Pro', 'Segoe UI';
                    font-size: 13px;
                }}
                QMenu::item {{ padding: 6px 28px 6px 14px; border-radius: 6px; margin: 2px 0px; }}
                QMenu::item:selected {{ background-color: #007aff; color: white; }}
                QMenu::separator {{ height: 1px; background: #e5e5e5; margin: 6px 4px; }}
            """)
        else: 
            self.setStyleSheet(f"""
                QMainWindow, QWidget#MainWidget {{ background: transparent; }}
                QWidget#WindowContainer {{ background-color: #1e1f22; color: #e0e0e0; border-radius: {radius}; }}
                QWidget#TopTitleBar {{ background-color: #1e1f22; border-top-left-radius: {radius}; border-top-right-radius: {radius}; border-bottom: 1px solid #2b2d31; }}
                QWidget#NavBarWidget {{ background-color: #2b2d31; border-bottom: 1px solid #232428; }}
                QWidget#FavBar {{ border-bottom: 1px solid #232428; background-color: #2b2d31; }}
                QStackedWidget#StackedWidget {{ border-bottom-left-radius: {radius}; border-bottom-right-radius: {radius}; }}
                
                QLineEdit {{ padding: 5px 14px; border-radius: 6px; border: 1px solid #3c3c3c; background-color: #1e1f22; color: #ffffff; font-size: 13px; }}
                QLineEdit:focus {{ border: 2px solid #0a84ff; background-color: #141414; }}
                
                QPushButton {{ border: none; border-radius: 4px; background-color: transparent; color: #cccccc; }}
                QPushButton:hover {{ background-color: #2d2d2d; }}
                
                QPushButton#btn_add_tab_top {{ font-size: 14px; color: #aaaaaa; background-color: transparent; border-radius: 6px; font-weight: bold; }}
                QPushButton#btn_add_tab_top:hover {{ background-color: rgba(255,255,255,0.1); color: #ffffff; }}
                
                QPushButton#btn_list_tabs {{ font-size: 14px; color: #aaaaaa; border-radius: 6px; background-color: transparent; }}
                QPushButton#btn_list_tabs:hover {{ background-color: #333333; }}
                
                QPushButton#btn_nav {{ font-size: 20px; color: #cccccc; border-radius: 6px; }}
                QPushButton#btn_nav:hover {{ background-color: #333333; }}
                
                QPushButton#btn_fav_item {{ font-size: 12px; color: #cccccc; padding: 5px 10px; font-family: -apple-system, sans-serif; }}
                QPushButton#btn_fav_item:hover {{ background-color: #2d2d2d; border-radius: 6px; color: #ffffff; }}
                
                QPushButton#WindowControlButton {{ font-size: 11px; color: #aaaaaa; border-radius: 0px; background-color: transparent; }}
                QPushButton#WindowControlButton:hover {{ background-color: #2d2d2d; }}
                QPushButton#WindowControlClose:hover {{ background-color: #e11d48; color: white; }}
                
                QMenu {{ 
                    background-color: #2c2c2c; 
                    color: #f5f5f7; 
                    border: 1px solid #454545; 
                    padding: 6px; 
                    border-radius: 10px; 
                    font-family: '.AppleSystemUIFont', 'SF Pro', 'Segoe UI';
                    font-size: 13px;
                }}
                QMenu::item {{ padding: 6px 28px 6px 14px; border-radius: 6px; margin: 2px 0px; }}
                QMenu::item:selected {{ background-color: #0a84ff; color: white; }}
                QMenu::separator {{ height: 1px; background: #454545; margin: 6px 4px; }}
            """)
            
        for tab in self.tab_bar.tabs_list:
            tab.update_style()

    def add_new_tab(self, qurl, title):
        browser = QWebEngineView()
        custom_page = AdvancedWebPage(QWebEngineProfile.defaultProfile(), self, parent=browser)
        browser.setPage(custom_page)
        
        dark_mode_active = (self.current_theme == "dark")
        browser.settings().setAttribute(QWebEngineSettings.WebAttribute.ForceDarkMode, dark_mode_active)
        
        browser.setUrl(qurl)
        
        browser.urlChanged.connect(lambda q: self.update_url_bar(q, browser))
        browser.titleChanged.connect(lambda t: self.update_tab_title(t, browser))
        browser.iconChanged.connect(lambda: self.handle_icon_changed(browser)) 
        
        tab_id = str(uuid.uuid4())
        self.tabs_map[tab_id] = browser
        self.stacked_widget.addWidget(browser)
        
        tab_index = self.tab_bar.addTab(tab_id, title)
        self.tab_bar.setCurrentIndex(tab_index)
        
        self.tab_bar.recalculate_tab_sizes()
        self.adjust_plus_button_position()

    def current_browser(self):
        if self.tab_bar.currentIndex() >= 0:
            tab_id = self.tab_bar.tabData(self.tab_bar.currentIndex())
            return self.tabs_map.get(tab_id)
        return None

    def tab_changed(self, index):
        if index >= 0:
            tab_id = self.tab_bar.tabData(index)
            browser = self.tabs_map.get(tab_id)
            if browser:
                self.stacked_widget.setCurrentWidget(browser)
                self.update_url_bar(browser.url(), browser)

    def close_tab(self, index):
        if self.tab_bar.count() > 1:
            tab_id = self.tab_bar.tabData(index)
            browser = self.tabs_map.get(tab_id)
            if browser:
                self.stacked_widget.removeWidget(browser)
                browser.deleteLater()
                del self.tabs_map[tab_id]
            self.tab_bar.removeTab(index)
        else:
            self.close()
        self.tab_bar.recalculate_tab_sizes()
        self.adjust_plus_button_position()

    def update_tab_title(self, title, browser):
        for i in range(self.tab_bar.count()):
            if self.tabs_map.get(self.tab_bar.tabData(i)) == browser:
                self.tab_bar.setTabText(i, title)
                break

    def handle_icon_changed(self, browser):
        icon = browser.icon()
        if icon.isNull(): return

        for i in range(self.tab_bar.count()):
            if self.tabs_map.get(self.tab_bar.tabData(i)) == browser:
                self.tab_bar.setTabIcon(i, icon)
                break

        url_str = browser.url().toString()
        domain = browser.url().host()
        favorites = get_favorites()
        
        if url_str in favorites and domain:
            icon_path = f"favicons/{domain}.png"
            icon.pixmap(16, 16).save(icon_path)
            if favorites[url_str].get("icon_path") != icon_path:
                favorites[url_str]["icon_path"] = icon_path
                save_favorites(favorites)
                self.render_favorites_bar()

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url: return
        if not (url.startswith("http://") or url.startswith("https://")):
            if "." not in url or " " in url:
                url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
            else:
                url = "https://" + url
        self.current_browser().setUrl(QUrl(url))
        self.stacked_widget.currentWidget().setFocus() 

    def update_url_bar(self, q, browser):
        if browser == self.current_browser() and "about:blank" not in q.toString():
            self.url_bar.setText(q.toString())

    def add_current_to_favorites(self):
        browser = self.current_browser()
        if not browser: return
        url = browser.url().toString()
        domain = browser.url().host()
        default_title = browser.title() or domain

        if url and url != "about:blank":
            dialog = MacInputDialog("Adicionar favorito", "Escolha o nome para exibir nos favoritos:", default_title, theme=self.current_theme, parent=self)
            ok = dialog.exec()
            title = dialog.textValue()

            if ok and title.strip():
                favorites = get_favorites()
                
                icon_path = ""
                if domain and not browser.icon().isNull():
                    icon_path = f"favicons/{domain}.png"
                    browser.icon().pixmap(16, 16).save(icon_path)

                favorites[url] = {"title": title.strip(), "icon_path": icon_path}
                save_favorites(favorites)
                self.render_favorites_bar()

    def show_favorite_context_menu(self, pos, url):
        sender_button = self.sender()
        context_menu = QMenu(self)
        delete_action = context_menu.addAction("❌ Remover dos Favoritos")
        
        action = context_menu.exec(sender_button.mapToGlobal(pos))
        if action == delete_action:
            favorites = get_favorites()
            if url in favorites:
                del favorites[url]
                save_favorites(favorites)
                self.render_favorites_bar()

    def render_favorites_bar(self):
        for i in reversed(range(self.fav_bar_layout.count() - 1)): 
            w = self.fav_bar_layout.itemAt(i).widget()
            if w: w.deleteLater()

        favorites = get_favorites()
        for url, data in favorites.items():
            title = data.get("title", "Favorito")
            icon_path = data.get("icon_path", "")

            display_title = title[:12] + ".." if len(title) > 12 else title
            display_title = f"  {display_title}" 
            
            btn = QPushButton(display_title)
            btn.setObjectName("btn_fav_item")
            
            if icon_path and os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(16, 16))

            btn.clicked.connect(lambda checked, u=url, t=title: self.add_new_tab(QUrl(u), t))
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, u=url: self.show_favorite_context_menu(pos, u))

            self.fav_bar_layout.insertWidget(self.fav_bar_layout.count() - 1, btn)

    def closeEvent(self, event):
        self.save_window_state()
        super().closeEvent(event)

    def show_settings_menu(self):
        menu = QMenu(self)
        
        theme_menu = menu.addMenu("Escolher Tema")
        action_light = theme_menu.addAction("Modo Claro")
        action_dark = theme_menu.addAction("Modo Escuro")
        
        action_light.triggered.connect(lambda: self.change_theme("light"))
        action_dark.triggered.connect(lambda: self.change_theme("dark"))
        
        menu.addSeparator()
        
        status_ad = "Ativo" if self.ad_blocker.active else "Inativo"
        action_toggle_ad = menu.addAction(f"Bloqueador de Anúncios: [ {status_ad} ]")
        action_toggle_ad.triggered.connect(self.toggle_ad_blocker)

        menu.exec(self.btn_settings.mapToGlobal(self.btn_settings.rect().bottomLeft()))

    def toggle_ad_blocker(self):
        self.ad_blocker.active = not self.ad_blocker.active
        if self.current_browser():
            self.current_browser().reload()

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.tab_bar.set_theme(theme_name)
        self.apply_theme_stylesheet()
        
        dark_mode_active = (theme_name == "dark")
        QWebEngineProfile.defaultProfile().settings().setAttribute(
            QWebEngineSettings.WebAttribute.ForceDarkMode, dark_mode_active
        )
        for browser in self.tabs_map.values():
            browser.settings().setAttribute(
                QWebEngineSettings.WebAttribute.ForceDarkMode, dark_mode_active
            )

    def apply_theme_stylesheet(self):
        radius = "0px" if self.isMaximized() else "12px"
        
        if self.current_theme == "light":
            self.setStyleSheet(f"""
                QMainWindow, QWidget#MainWidget {{ background: transparent; }}
                QWidget#WindowContainer {{ background-color: #eef1f6; color: #222222; border-radius: {radius}; }}
                QWidget#TopTitleBar {{ background-color: #eef1f6; border-top-left-radius: {radius}; border-top-right-radius: {radius}; border-bottom: 1px solid #d0d4dc; }}
                QWidget#NavBarWidget {{ background-color: #ffffff; border-bottom: 1px solid #e0e0e0; }}
                QWidget#FavBar {{ border-bottom: 1px solid #e5e5e5; background-color: #ffffff; }}
                QStackedWidget#StackedWidget {{ border-bottom-left-radius: {radius}; border-bottom-right-radius: {radius}; }}
                
                QLineEdit {{ padding: 5px 14px; border-radius: 6px; border: 1px solid #d0d0d0; background-color: #f0f2f5; color: #000000; font-size: 13px; }}
                QLineEdit:focus {{ border: 2px solid #007aff; background-color: #ffffff; }}
                
                QPushButton {{ border: none; border-radius: 4px; background-color: transparent; color: #333333; }}
                QPushButton:hover {{ background-color: #e5e5e5; }}
                
                QPushButton#btn_add_tab_top {{ font-size: 14px; color: #444444; background-color: transparent; border-radius: 6px; font-weight: bold; }}
                QPushButton#btn_add_tab_top:hover {{ background-color: rgba(0,0,0,0.08); color: #000000; }}
                
                QPushButton#btn_list_tabs {{ font-size: 14px; color: #444444; border-radius: 6px; background-color: transparent; }}
                QPushButton#btn_list_tabs:hover {{ background-color: #dbdbdb; }}
                
                QPushButton#btn_nav {{ font-size: 20px; color: #444444; border-radius: 6px; }}
                QPushButton#btn_nav:hover {{ background-color: #ededed; }}
                
                QPushButton#btn_fav_item {{ font-size: 12px; color: #444444; padding: 5px 10px; font-family: -apple-system, sans-serif; }}
                QPushButton#btn_fav_item:hover {{ background-color: #f0f0f0; border-radius: 6px; color: #000000; }}
                
                QPushButton#WindowControlButton {{ font-size: 11px; color: #555555; border-radius: 0px; background-color: transparent; }}
                QPushButton#WindowControlButton:hover {{ background-color: #e0e0e0; }}
                QPushButton#WindowControlClose:hover {{ background-color: #e11d48; color: white; }}
                
                QMenu {{ 
                    background-color: #ffffff; 
                    border: 1px solid #d2d2d7; 
                    padding: 6px; 
                    border-radius: 10px; 
                    color: #1d1d1f;
                    font-family: '.AppleSystemUIFont', 'SF Pro', 'Segoe UI';
                    font-size: 13px;
                }}
                QMenu::item {{ padding: 6px 28px 6px 14px; border-radius: 6px; margin: 2px 0px; }}
                QMenu::item:selected {{ background-color: #007aff; color: white; }}
                QMenu::separator {{ height: 1px; background: #e5e5e5; margin: 6px 4px; }}
            """)
        else: 
            self.setStyleSheet(f"""
                QMainWindow, QWidget#MainWidget {{ background: transparent; }}
                QWidget#WindowContainer {{ background-color: #1e1f22; color: #e0e0e0; border-radius: {radius}; }}
                QWidget#TopTitleBar {{ background-color: #1e1f22; border-top-left-radius: {radius}; border-top-right-radius: {radius}; border-bottom: 1px solid #2b2d31; }}
                QWidget#NavBarWidget {{ background-color: #2b2d31; border-bottom: 1px solid #232428; }}
                QWidget#FavBar {{ border-bottom: 1px solid #232428; background-color: #2b2d31; }}
                QStackedWidget#StackedWidget {{ border-bottom-left-radius: {radius}; border-bottom-right-radius: {radius}; }}
                
                QLineEdit {{ padding: 5px 14px; border-radius: 6px; border: 1px solid #3c3c3c; background-color: #1e1f22; color: #ffffff; font-size: 13px; }}
                QLineEdit:focus {{ border: 2px solid #0a84ff; background-color: #141414; }}
                
                QPushButton {{ border: none; border-radius: 4px; background-color: transparent; color: #cccccc; }}
                QPushButton:hover {{ background-color: #2d2d2d; }}
                
                QPushButton#btn_add_tab_top {{ font-size: 14px; color: #aaaaaa; background-color: transparent; border-radius: 6px; font-weight: bold; }}
                QPushButton#btn_add_tab_top:hover {{ background-color: rgba(255,255,255,0.1); color: #ffffff; }}
                
                QPushButton#btn_list_tabs {{ font-size: 14px; color: #aaaaaa; border-radius: 6px; background-color: transparent; }}
                QPushButton#btn_list_tabs:hover {{ background-color: #333333; }}
                
                QPushButton#btn_nav {{ font-size: 20px; color: #cccccc; border-radius: 6px; }}
                QPushButton#btn_nav:hover {{ background-color: #333333; }}
                
                QPushButton#btn_fav_item {{ font-size: 12px; color: #cccccc; padding: 5px 10px; font-family: -apple-system, sans-serif; }}
                QPushButton#btn_fav_item:hover {{ background-color: #2d2d2d; border-radius: 6px; color: #ffffff; }}
                
                QPushButton#WindowControlButton {{ font-size: 11px; color: #aaaaaa; border-radius: 0px; background-color: transparent; }}
                QPushButton#WindowControlButton:hover {{ background-color: #2d2d2d; }}
                QPushButton#WindowControlClose:hover {{ background-color: #e11d48; color: white; }}
                
                QMenu {{ 
                    background-color: #2c2c2c; 
                    color: #f5f5f7; 
                    border: 1px solid #454545; 
                    padding: 6px; 
                    border-radius: 10px; 
                    font-family: '.AppleSystemUIFont', 'SF Pro', 'Segoe UI';
                    font-size: 13px;
                }}
                QMenu::item {{ padding: 6px 28px 6px 14px; border-radius: 6px; margin: 2px 0px; }}
                QMenu::item:selected {{ background-color: #0a84ff; color: white; }}
                QMenu::separator {{ height: 1px; background: #454545; margin: 6px 4px; }}
            """)
            
        for tab in self.tab_bar.tabs_list:
            tab.update_style()

    def add_new_tab(self, qurl, title):
        browser = QWebEngineView()
        custom_page = AdvancedWebPage(QWebEngineProfile.defaultProfile(), self, parent=browser)
        browser.setPage(custom_page)
        
        dark_mode_active = (self.current_theme == "dark")
        browser.settings().setAttribute(QWebEngineSettings.WebAttribute.ForceDarkMode, dark_mode_active)
        
        browser.setUrl(qurl)
        
        browser.urlChanged.connect(lambda q: self.update_url_bar(q, browser))
        browser.titleChanged.connect(lambda t: self.update_tab_title(t, browser))
        browser.iconChanged.connect(lambda: self.handle_icon_changed(browser)) 
        
        tab_id = str(uuid.uuid4())
        self.tabs_map[tab_id] = browser
        self.stacked_widget.addWidget(browser)
        
        tab_index = self.tab_bar.addTab(tab_id, title)
        self.tab_bar.setCurrentIndex(tab_index)
        
        self.tab_bar.recalculate_tab_sizes()
        self.adjust_plus_button_position()

    def current_browser(self):
        if self.tab_bar.currentIndex() >= 0:
            tab_id = self.tab_bar.tabData(self.tab_bar.currentIndex())
            return self.tabs_map.get(tab_id)
        return None

    def tab_changed(self, index):
        if index >= 0:
            tab_id = self.tab_bar.tabData(index)
            browser = self.tabs_map.get(tab_id)
            if browser:
                self.stacked_widget.setCurrentWidget(browser)
                self.update_url_bar(browser.url(), browser)

    def close_tab(self, index):
        if self.tab_bar.count() > 1:
            tab_id = self.tab_bar.tabData(index)
            browser = self.tabs_map.get(tab_id)
            if browser:
                self.stacked_widget.removeWidget(browser)
                browser.deleteLater()
                del self.tabs_map[tab_id]
            self.tab_bar.removeTab(index)
        else:
            self.close()
        self.tab_bar.recalculate_tab_sizes()
        self.adjust_plus_button_position()

    def update_tab_title(self, title, browser):
        for i in range(self.tab_bar.count()):
            if self.tabs_map.get(self.tab_bar.tabData(i)) == browser:
                self.tab_bar.setTabText(i, title)
                break

    def handle_icon_changed(self, browser):
        icon = browser.icon()
        if icon.isNull(): return

        for i in range(self.tab_bar.count()):
            if self.tabs_map.get(self.tab_bar.tabData(i)) == browser:
                self.tab_bar.setTabIcon(i, icon)
                break

        url_str = browser.url().toString()
        domain = browser.url().host()
        favorites = get_favorites()
        
        if url_str in favorites and domain:
            icon_path = f"favicons/{domain}.png"
            icon.pixmap(16, 16).save(icon_path)
            if favorites[url_str].get("icon_path") != icon_path:
                favorites[url_str]["icon_path"] = icon_path
                save_favorites(favorites)
                self.render_favorites_bar()

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url: return
        if not (url.startswith("http://") or url.startswith("https://")):
            if "." not in url or " " in url:
                url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
            else:
                url = "https://" + url
        self.current_browser().setUrl(QUrl(url))
        self.stacked_widget.currentWidget().setFocus() 

    def update_url_bar(self, q, browser):
        if browser == self.current_browser() and "about:blank" not in q.toString():
            self.url_bar.setText(q.toString())

    def add_current_to_favorites(self):
        browser = self.current_browser()
        if not browser: return
        url = browser.url().toString()
        domain = browser.url().host()
        default_title = browser.title() or domain

        if url and url != "about:blank":
            dialog = MacInputDialog("Adicionar favorito", "Escolha o nome para exibir nos favoritos:", default_title, theme=self.current_theme, parent=self)
            ok = dialog.exec()
            title = dialog.textValue()

            if ok and title.strip():
                favorites = get_favorites()
                
                icon_path = ""
                if domain and not browser.icon().isNull():
                    icon_path = f"favicons/{domain}.png"
                    browser.icon().pixmap(16, 16).save(icon_path)

                favorites[url] = {"title": title.strip(), "icon_path": icon_path}
                save_favorites(favorites)
                self.render_favorites_bar()

    def show_favorite_context_menu(self, pos, url):
        sender_button = self.sender()
        context_menu = QMenu(self)
        delete_action = context_menu.addAction("❌ Remover dos Favoritos")
        
        action = context_menu.exec(sender_button.mapToGlobal(pos))
        if action == delete_action:
            favorites = get_favorites()
            if url in favorites:
                del favorites[url]
                save_favorites(favorites)
                self.render_favorites_bar()

    def render_favorites_bar(self):
        for i in reversed(range(self.fav_bar_layout.count() - 1)): 
            w = self.fav_bar_layout.itemAt(i).widget()
            if w: w.deleteLater()

        favorites = get_favorites()
        for url, data in favorites.items():
            title = data.get("title", "Favorito")
            icon_path = data.get("icon_path", "")

            display_title = title[:12] + ".." if len(title) > 12 else title
            display_title = f"  {display_title}" 
            
            btn = QPushButton(display_title)
            btn.setObjectName("btn_fav_item")
            
            if icon_path and os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(16, 16))

            btn.clicked.connect(lambda checked, u=url, t=title: self.add_new_tab(QUrl(u), t))
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, u=url: self.show_favorite_context_menu(pos, u))

            self.fav_bar_layout.insertWidget(self.fav_bar_layout.count() - 1, btn)
