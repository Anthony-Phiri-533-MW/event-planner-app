from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QMessageBox, QSpinBox
from controllers.settings_controller import SettingsController
from core.theme_manager import ThemeManager
from workers.backup_worker import BackupWorker

class SettingsView(QWidget):
    def __init__(self, theme_manager: ThemeManager, refresh_theme_callback):
        super().__init__()

        self.theme_manager = theme_manager
        self.refresh_theme_callback = refresh_theme_callback
        self.settings_controller = SettingsController()

        self.layout = QVBoxLayout(self)

        # Theme Section
        self.layout.addWidget(QLabel("Theme Selection:"))
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["Light", "Dark"])
        self.layout.addWidget(self.theme_dropdown)

        # Backup Frequency
        self.layout.addWidget(QLabel("Backup Frequency (Minutes):"))
        self.backup_spinbox = QSpinBox()
        self.backup_spinbox.setRange(5, 1440)  # From 5 min to 1 day
        self.layout.addWidget(self.backup_spinbox)

        # Backup Status Label
        self.backup_status_label = QLabel("Backup status: Waiting...")
        self.layout.addWidget(self.backup_status_label)

        # Save Button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button)

        self.load_current_settings()

    def load_current_settings(self):
        settings = self.settings_controller.get_settings()

        # Theme
        current_theme = settings.get("theme", "Light")
        idx = self.theme_dropdown.findText(current_theme)
        if idx != -1:
            self.theme_dropdown.setCurrentIndex(idx)

        # Backup frequency
        backup_frequency = settings.get("backup_frequency_minutes", 60)
        self.backup_spinbox.setValue(backup_frequency)

    def save_settings(self):
        selected_theme = self.theme_dropdown.currentText()
        backup_frequency = self.backup_spinbox.value()

        self.settings_controller.set_theme(selected_theme)
        self.settings_controller.set_backup_frequency(backup_frequency)

        self.theme_manager.set_theme(selected_theme)
        self.refresh_theme_callback()

        # Start Backup Worker
        self.start_backup_worker()

        QMessageBox.information(self, "Settings Saved", "Settings updated successfully!")

    def start_backup_worker(self):
        # Start the backup worker
        self.backup_worker = BackupWorker(api_url="https://your-api-url.com", parent=self)
        self.backup_worker.backup_signal.connect(self.update_backup_status)
        self.backup_worker.start()

    def update_backup_status(self, status_message):
        # Update the UI with backup status
        self.backup_status_label.setText(f"Backup status: {status_message}")
