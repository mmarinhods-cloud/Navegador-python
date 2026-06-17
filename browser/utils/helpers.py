import os
import json

FAVORITES_FILE = "favorites.json"
SETTINGS_FILE = "settings.json"
FAVICONS_DIR = "favicons"

MALICIOUS_DOMAINS = {
    "malware-test.com", 
    "phishing-fake-site.org", 
    "unsafe-download.net"
}

BLOCKED_DOMAINS = {
    "doubleclick.net", "googleads.g.doubleclick.net", "pagead2.googlesyndication.com",
    "analytics.google.com", "adservice.google.com", "adnxs.com", "popads.net",
    "scorecardresearch.com", "hotjar.com", "outbrain.com", "taboola.com"
}

def ensure_directories():
    if not os.path.exists(FAVICONS_DIR):
        os.makedirs(FAVICONS_DIR)

def get_favorites():
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=4)

def get_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)
