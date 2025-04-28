import os

# Folder and file structure
structure = {
    "event_planner": {
        "core": {
            "database.py": "",
            "api_sync.py": "",
            "logger.py": "",
            "theme_manager.py": '''from PyQt6.QtWidgets import QWidget

def apply_theme(widget: QWidget, theme_name: str):
    if theme_name == "light":
        with open("assets/styles/light_theme.qss", "r") as f:
            widget.setStyleSheet(f.read())
    elif theme_name == "dark":
        with open("assets/styles/dark_theme.qss", "r") as f:
            widget.setStyleSheet(f.read())
''',
            "settings_manager.py": '''import json

SETTINGS_FILE = "data/settings.json"

def load_settings():
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)
'''
        },
        "models": {
            "event.py": "",
            "event_type.py": "",
            "guest.py": "",
            "category.py": "",
            "reminder.py": ""
        },
        "views": {
            "dashboard.py": '''from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        welcome_label = QLabel("Welcome to Event Planner Dashboard")
        layout.addWidget(welcome_label)

        self.setLayout(layout)
'''
        },
        "controllers": {
            "event_controller.py": "",
            "calendar_controller.py": "",
            "settings_controller.py": "",
            "backup_controller.py": ""
        },
        "assets": {
            "icons": {},
            "styles": {
                "light_theme.qss": '''QWidget {
    background-color: #FFFFFF;
    color: #250034;
}

QPushButton {
    background-color: #BE87D5;
    color: #FFFFFF;
    border-radius: 8px;
    padding: 8px;
}

QPushButton:hover {
    background-color: #A66CC1;
}
''',
                "dark_theme.qss": '''QWidget {
    background-color: #250034;
    color: #FFFFFF;
}

QPushButton {
    background-color: #BE87D5;
    color: #250034;
    border-radius: 8px;
    padding: 8px;
}

QPushButton:hover {
    background-color: #A66CC1;
}
'''
            }
        },
        "data": {
            "settings.json": '''{
    "theme": "light",
    "backup_frequency": "daily",
    "api_url": "https://your-backup-api.com/endpoint"
}
'''
        },
        "utils": {
            "validators.py": "",
            "decorators.py": "",
            "helpers.py": ""
        },
        "main.py": '''import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from views.dashboard import Dashboard

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Planner")
        self.resize(1200, 800)

        self.dashboard = Dashboard()
        self.setCentralWidget(self.dashboard)

        from core.theme_manager import apply_theme
        apply_theme(self, theme_name='light')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
'''
    }
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

if __name__ == "__main__":
    base_path = os.getcwd()  # or choose where you want to create
    project_name = "event_planner"

    full_path = os.path.join(base_path, project_name)
    if os.path.exists(full_path):
        print(f"Folder '{project_name}' already exists. Aborting.")
    else:
        create_structure(base_path, structure)
        print(f"Project '{project_name}' created successfully!")
