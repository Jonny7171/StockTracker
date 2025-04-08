# Default settings
USER_CONFIG = {
    "monthly_budget": 2000,
    "recommendation_frequency": "daily",
    "min_trade_amount": 50,
    "ticker": "VSP.TO"
}

SETTINGS_FILE = "user_settings.json"

import json
import os

def load_user_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return USER_CONFIG.copy()

def save_user_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)