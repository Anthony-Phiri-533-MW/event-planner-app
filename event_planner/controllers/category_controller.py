from database.db import get_db

class CategoryController:
    def __init__(self):
        self.conn = get_db()
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        self.conn.commit()

    def add_category(self, name):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO categories (name)
            VALUES (?)
        ''', (name,))
        self.conn.commit()

    def get_all_categories(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name FROM categories')
        rows = cursor.fetchall()
        return [{"id": row[0], "name": row[1]} for row in rows]

    def update_category(self, category_id, new_name):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE categories
            SET name = ?
            WHERE id = ?
        ''', (new_name, category_id))
        self.conn.commit()

    def delete_category(self, category_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM categories
            WHERE id = ?
        ''', (category_id,))
        self.conn.commit()
