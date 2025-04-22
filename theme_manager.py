import json
import os

THEME_FILE = "theme.json"

def save_theme(theme):
    """Save the selected theme to a JSON file."""
    with open(THEME_FILE, "w") as file:
        json.dump({"theme": theme}, file)

def load_theme():
    """Load the saved theme preference from the JSON file."""
    if os.path.exists(THEME_FILE):
        with open(THEME_FILE, "r") as file:
            data = json.load(file)
            return data.get("theme", "light")  # Default to light mode
    return "light"
