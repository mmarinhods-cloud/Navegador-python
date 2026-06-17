from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from ..utils.helpers import BLOCKED_DOMAINS

class AdBlockerInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        self.active = True
        self.blocked_domains = BLOCKED_DOMAINS

    def interceptRequest(self, info):
        if not self.active:
            return
        host = info.requestUrl().host()
        if any(domain in host for domain in self.blocked_domains):
            info.block(True)
