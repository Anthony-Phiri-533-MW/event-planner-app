import time
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from controllers.settings_controller import SettingsController
from controllers.event_controller import EventController
from controllers.log_controller import LogController
import requests

class BackupWorker(QThread):
    backup_signal = pyqtSignal(str)  # Signal to update status UI with backup result

    def __init__(self, api_url: str, parent=None):
        super().__init__(parent)
        self.api_url = api_url
        self.settings_controller = SettingsController()
        self.event_controller = EventController()
        self.log_controller = LogController()  # Add LogController
        self.timer = QTimer(self)

    def run(self):
        # Initial delay based on user settings
        self.load_backup_frequency()
        self.timer.timeout.connect(self.perform_backup)
        self.timer.start(self.backup_frequency * 1000 * 60)  # Convert to milliseconds
        self.exec_()  # Start the event loop for this thread

    def load_backup_frequency(self):
        # Load the backup frequency from settings
        settings = self.settings_controller.get_settings()
        self.backup_frequency = int(settings.get("backup_frequency_minutes", 60))  # Default to 60 minutes

    def perform_backup(self):
        events = self.event_controller.get_all_events()
        if not events:
            self.log_controller.add_log("INFO", "No events to back up.")
            self.backup_signal.emit("No events to back up.")
            return

        backup_successful = self.send_data_to_api(events)
        if backup_successful:
            self.log_controller.add_log("INFO", f"Backup successful at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.backup_signal.emit(f"Backup completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            self.log_controller.add_log("ERROR", "Backup failed.")
            self.backup_signal.emit("Backup failed. Please check your connection.")

    def send_data_to_api(self, events):
        try:
            # Construct the payload with event data
            payload = {"events": events}
            response = requests.post(self.api_url + "/backup", json=payload)
            if response.status_code == 200:
                return True
            return False
        except Exception as e:
            print(f"Error while backing up: {e}")
            return False
