from database.db import get_db

class LogController:
    def __init__(self):
        self.conn = get_db()
        self.create_logs_table()

    def create_logs_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                message TEXT
            )
        ''')
        self.conn.commit()

    def add_log(self, level, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO logs (timestamp, level, message)
            VALUES (?, ?, ?)
        ''', (timestamp, level, message))
        self.conn.commit()

    def get_logs(self, limit=100):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        return [{"id": row[0], "timestamp": row[1], "level": row[2], "message": row[3]} for row in rows]

    def clear_logs(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM logs')
        self.conn.commit()