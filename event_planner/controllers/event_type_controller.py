from database.db import get_db

class EventTypeController:
    def __init__(self):
        self.conn = get_db()
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        self.conn.commit()

    def add_event_type(self, name):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO event_types (name)
            VALUES (?)
        ''', (name,))
        self.conn.commit()

    def get_all_event_types(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name FROM event_types')
        rows = cursor.fetchall()
        return [{"id": row[0], "name": row[1]} for row in rows]

    def update_event_type(self, event_type_id, new_name):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE event_types
            SET name = ?
            WHERE id = ?
        ''', (new_name, event_type_id))
        self.conn.commit()

    def delete_event_type(self, event_type_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM event_types
            WHERE id = ?
        ''', (event_type_id,))
        self.conn.commit()
