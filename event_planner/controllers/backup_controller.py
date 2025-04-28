import requests
import threading
from core.database import Database
from core.settings_manager import load_settings

class BackupController:
    def __init__(self):
        self.settings = load_settings()
        self.db = Database()
        self.api_url = self.settings.get("api_url")

    def backup_now(self):
        """Push local database entries to the backup API."""
        data = self.collect_data()
        try:
            response = requests.post(self.api_url, json=data)
            if response.status_code == 200:
                print("Backup successful.")
            else:
                print(f"Backup failed with status {response.status_code}.")
        except Exception as e:
            print(f"Backup error: {e}")

    def collect_data(self):
        """Collect all data to backup."""
        tables = ["events", "event_types", "categories", "guests", "reminders"]
        data = {}
        for table in tables:
            rows = self.db.fetch_all(f"SELECT * FROM {table}")
            data[table] = rows
        return data

    def schedule_auto_backup(self):
        """Set up backup based on the backup frequency setting."""
        import time

        def auto_backup_loop():
            while True:
                frequency = self.settings.get("backup_frequency", "daily")
                seconds = self.frequency_to_seconds(frequency)
                time.sleep(seconds)
                self.backup_now()

        threading.Thread(target=auto_backup_loop, daemon=True).start()

    def frequency_to_seconds(self, frequency: str) -> int:
        if frequency == "hourly":
            return 3600
        elif frequency == "daily":
            return 86400
        elif frequency == "weekly":
            return 604800
        else:
            return 86400  # default daily
