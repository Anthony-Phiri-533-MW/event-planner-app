from database.db import get_db

class SettingsController:
    def __init__(self):
        self.conn = get_db()
        self.create_settings_table()

    def create_settings_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.conn.commit()

    def get_settings(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT key, value FROM settings')
        rows = cursor.fetchall()
        return {key: value for key, value in rows}

    def set_theme(self, theme):
        self._set_setting("theme", theme)

    def set_backup_frequency(self, minutes):
        self._set_setting("backup_frequency_minutes", str(minutes))

    def _set_setting(self, key, value):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        self.conn.commit()
