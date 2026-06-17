from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEnginePage
from ..utils.helpers import MALICIOUS_DOMAINS

class AdvancedWebPage(QWebEnginePage):
    def __init__(self, profile, main_window, parent=None):
        super().__init__(profile, parent)
        self.main_window = main_window

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        url_str = url.toString()
        host = url.host()

        if url_str.startswith("bypass://"):
            real_url = url_str.replace("bypass://", "")
            self.main_window.bypassed_sites.add(QUrl(real_url).host())
            self.setUrl(QUrl(real_url))
            return False

        if isMainFrame and host in MALICIOUS_DOMAINS:
            if host not in self.main_window.bypassed_sites:
                self.show_malware_warning(url_str)
                return False
                
        return super().acceptNavigationRequest(url, _type, isMainFrame)

    def show_malware_warning(self, target_url):
        warning_html = f"""
        <html>
        <head>
            <style>
                body {{ background-color: #1e1e1e; color: #ffffff; font-family: -apple-system, sans-serif; text-align: center; padding-top: 15%; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #2d2d2d; padding: 40px; border-radius: 12px; border: 1px solid #444; }}
                h1 {{ color: #ff5f56; font-size: 28px; }}
                .btn {{ display: inline-block; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: 25px; }}
                .btn-safe {{ background-color: #007aff; color: white; margin-right: 15px; }}
                .btn-danger {{ background-color: transparent; color: #ff5f56; border: 1px solid #ff5f56; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚠️ Alerta de Segurança</h1>
                <p>O site <strong>{target_url}</strong> foi detectado como potencialmente malicioso.</p>
                <a href="bypass://https://google.com" class="btn btn-safe">Voltar para a Segurança</a>
                <a href="bypass://{target_url}" class="btn btn-danger">Quero continuar assim mesmo</a>
            </div>
        </body>
        </html>
        """
        self.setHtml(warning_html, QUrl("about:blank"))
