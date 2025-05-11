import sqlite3
import csv
import json
import hashlib
from datetime import datetime

class EventDatabase:
    def __init__(self, db_name="events.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT,
                    venue TEXT,
                    description TEXT,
                    is_archived INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS archived_events (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT,
                    venue TEXT,
                    description TEXT,
                    archived_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    event_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    is_completed INTEGER DEFAULT 0,
                    FOREIGN KEY (event_id) REFERENCES events(id)
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS guests (
                    id INTEGER PRIMARY KEY,
                    event_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT,
                    FOREIGN KEY (event_id) REFERENCES events(id)
                )
            ''')

    def create_user(self, username, password, email=None):
        with self.conn:
            password_hash = self._hash_password(password)
            try:
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email)
                    VALUES (?, ?, ?)
                ''', (username, password_hash, email))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None

    def authenticate_user(self, username, password):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, password_hash FROM users WHERE username = ?
            ''', (username,))
            result = cursor.fetchone()
            if result:
                user_id, stored_hash = result
                if self._check_password(password, stored_hash):
                    return user_id
            return None

    def update_user(self, user_id, password=None, email=None):
        with self.conn:
            cursor = self.conn.cursor()
            if password:
                password_hash = self._hash_password(password)
                cursor.execute('''
                    UPDATE users 
                    SET password_hash = ?
                    WHERE id = ?
                ''', (password_hash, user_id))
            if email is not None:
                cursor.execute('''
                    UPDATE users 
                    SET email = ?
                    WHERE id = ?
                ''', (email, user_id))

    def get_user_by_id(self, user_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, username, password_hash, email 
                FROM users WHERE id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "username": result[1],
                    "password_hash": result[2],
                    "email": result[3]
                }
            return None

    def get_user_email(self, user_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def _check_password(self, password, stored_hash):
        return self._hash_password(password) == stored_hash

    def add_event(self, user_id, name, date, time, venue, description):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO events (user_id, name, date, time, venue, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, name, date, time, venue, description))
            return cursor.lastrowid

    def update_event(self, event_id, name, date, time, venue, description):
        with self.conn:
            self.conn.execute('''
                UPDATE events 
                SET name = ?, date = ?, time = ?, venue = ?, description = ?
                WHERE id = ?
            ''', (name, date, time, venue, description, event_id))

    def delete_event(self, event_id):
        with self.conn:
            self.conn.execute('DELETE FROM guests WHERE event_id = ?', (event_id,))
            self.conn.execute('DELETE FROM tasks WHERE event_id = ?', (event_id,))
            self.conn.execute('DELETE FROM events WHERE id = ?', (event_id,))

    def get_all_events(self, user_id):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM events 
                WHERE user_id = ? AND is_archived = 0
                ORDER BY date, time
            ''', (user_id,)).fetchall()

    def get_archived_events(self, user_id):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM archived_events 
                WHERE user_id = ?
                ORDER BY archived_date DESC
            ''', (user_id,)).fetchall()

    def search_events(self, user_id, query):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM events 
                WHERE user_id = ? AND is_archived = 0 AND 
                (name LIKE ? OR venue LIKE ? OR description LIKE ?)
                ORDER BY date, time
            ''', (user_id, f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()

    def get_events_by_date(self, user_id, date):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM events 
                WHERE user_id = ? AND date = ? AND is_archived = 0
                ORDER BY time, name
            ''', (user_id, date)).fetchall()

    def get_event_by_id(self, event_id):
        with self.conn:
            return self.conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()

    def add_task(self, event_id, description):
        with self.conn:
            self.conn.execute('''
                INSERT INTO tasks (event_id, description)
                VALUES (?, ?)
            ''', (event_id, description))

    def get_tasks_for_event(self, event_id):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM tasks 
                WHERE event_id = ?
                ORDER BY id
            ''', (event_id,)).fetchall()

    def update_task_status(self, task_id, is_completed):
        with self.conn:
            self.conn.execute('''
                UPDATE tasks 
                SET is_completed = ?
                WHERE id = ?
            ''', (1 if is_completed else 0, task_id))

    def delete_task(self, task_id):
        with self.conn:
            self.conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))

    def add_guest(self, event_id, name, email):
        with self.conn:
            self.conn.execute('''
                INSERT INTO guests (event_id, name, email)
                VALUES (?, ?, ?)
            ''', (event_id, name, email))

    def get_guests_for_event(self, event_id):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM guests 
                WHERE event_id = ?
                ORDER BY name
            ''', (event_id,)).fetchall()

    def delete_guest(self, guest_id):
        with self.conn:
            self.conn.execute('DELETE FROM guests WHERE id = ?', (guest_id,))

    def archive_event(self, event_id):
        with self.conn:
            cursor = self.conn.cursor()
            event = self.get_event_by_id(event_id)
            if not event:
                return False
            tasks = self.get_tasks_for_event(event_id)
            if tasks and not all(task[3] for task in tasks):
                return False
            try:
                cursor.execute('''
                    INSERT INTO archived_events (
                        id, user_id, name, date, time, venue, description, archived_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event[0], event[1], event[2], event[3], event[4], event[5], event[6],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                cursor.execute('DELETE FROM tasks WHERE event_id = ?', (event_id,))
                cursor.execute('DELETE FROM guests WHERE event_id = ?', (event_id,))
                cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
                return True
            except sqlite3.Error:
                return False

    def export_to_csv(self, user_id, filename):
        with self.conn:
            events = self.conn.execute('SELECT * FROM events WHERE user_id = ?', (user_id,)).fetchall()
            with open(f'{filename}_events.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'User ID', 'Name', 'Date', 'Time', 'Venue', 'Description', 'Is Archived'])
                writer.writerows(events)
            archived = self.conn.execute('SELECT * FROM archived_events WHERE user_id = ?', (user_id,)).fetchall()
            with open(f'{filename}_archived.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'User ID', 'Name', 'Date', 'Time', 'Venue', 'Description', 'Archived Date'])
                writer.writerows(archived)
            tasks = self.conn.execute('''
                SELECT t.* FROM tasks t
                JOIN events e ON t.event_id = e.id
                WHERE e.user_id = ?
            ''', (user_id,)).fetchall()
            with open(f'{filename}_tasks.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Event ID', 'Description', 'Is Completed'])
                writer.writerows(tasks)
            guests = self.conn.execute('''
                SELECT g.* FROM guests g
                JOIN events e ON g.event_id = e.id
                WHERE e.user_id = ?
            ''', (user_id,)).fetchall()
            with open(f'{filename}_guests.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Event ID', 'Name', 'Email'])
                writer.writerows(guests)

    def export_to_json(self, user_id, filename):
        data = {
            'events': [],
            'archived_events': [],
            'tasks': [],
            'guests': []
        }
        with self.conn:
            for row in self.conn.execute('SELECT * FROM events WHERE user_id = ?', (user_id,)):
                data['events'].append({
                    'id': row[0],
                    'user_id': row[1],
                    'name': row[2],
                    'date': row[3],
                    'time': row[4],
                    'venue': row[5],
                    'description': row[6],
                    'is_archived': bool(row[7])
                })
            for row in self.conn.execute('SELECT * FROM archived_events WHERE user_id = ?', (user_id,)):
                data['archived_events'].append({
                    'id': row[0],
                    'user_id': row[1],
                    'name': row[2],
                    'date': row[3],
                    'time': row[4],
                    'venue': row[5],
                    'description': row[6],
                    'archived_date': row[7]
                })
            for row in self.conn.execute('''
                SELECT t.* FROM tasks t
                JOIN events e ON t.event_id = e.id
                WHERE e.user_id = ?
            ''', (user_id,)):
                data['tasks'].append({
                    'id': row[0],
                    'event_id': row[1],
                    'description': row[2],
                    'is_completed': bool(row[3])
                })
            for row in self.conn.execute('''
                SELECT g.* FROM guests g
                JOIN events e ON g.event_id = e.id
                WHERE e.user_id = ?
            ''', (user_id,)):
                data['guests'].append({
                    'id': row[0],
                    'event_id': row[1],
                    'name': row[2],
                    'email': row[3]
                })
        with open(f'{filename}.json', 'w') as f:
            json.dump(data, f, indent=4)

    def get_backup_data(self, user_id):
        data = {
            "user_id": user_id,
            "user": self.get_user_by_id(user_id),
            "events": [],
            "archived_events": [],
            "tasks": [],
            "guests": [],
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        with self.conn:
            for row in self.conn.execute('SELECT * FROM events WHERE user_id = ?', (user_id,)):
                data['events'].append({
                    'id': row[0],
                    'user_id': row[1],
                    'name': row[2],
                    'date': row[3],
                    'time': row[4],
                    'venue': row[5],
                    'description': row[6],
                    'is_archived': bool(row[7])
                })
            for row in self.conn.execute('SELECT * FROM archived_events WHERE user_id = ?', (user_id,)):
                data['archived_events'].append({
                    'id': row[0],
                    'user_id': row[1],
                    'name': row[2],
                    'date': row[3],
                    'time': row[4],
                    'venue': row[5],
                    'description': row[6],
                    'archived_date': row[7]
                })
            for row in self.conn.execute('SELECT * FROM tasks WHERE event_id IN (SELECT id FROM events WHERE user_id = ?)', (user_id,)):
                data['tasks'].append({
                    'id': row[0],
                    'event_id': row[1],
                    'description': row[2],
                    'is_completed': bool(row[3])
                })
            for row in self.conn.execute('SELECT * FROM guests WHERE event_id IN (SELECT id FROM events WHERE user_id = ?)', (user_id,)):
                data['guests'].append({
                    'id': row[0],
                    'event_id': row[1],
                    'name': row[2],
                    'email': row[3]
                })
        return data

    def restore_backup_data(self, backup_data):
        user_id = backup_data['user_id']
        with self.conn:
            # Clear existing data for the user
            self.conn.execute('DELETE FROM guests WHERE event_id IN (SELECT id FROM events WHERE user_id = ?)', (user_id,))
            self.conn.execute('DELETE FROM tasks WHERE event_id IN (SELECT id FROM events WHERE user_id = ?)', (user_id,))
            self.conn.execute('DELETE FROM events WHERE user_id = ?', (user_id,))
            self.conn.execute('DELETE FROM archived_events WHERE user_id = ?', (user_id,))
            # Restore user
            user = backup_data['user']
            self.conn.execute('''
                INSERT OR REPLACE INTO users (id, username, password_hash, email)
                VALUES (?, ?, ?, ?)
            ''', (user['id'], user['username'], user['password_hash'], user['email']))
            # Restore events
            for event in backup_data['events']:
                self.conn.execute('''
                    INSERT INTO events (id, user_id, name, date, time, venue, description, is_archived)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event['id'], event['user_id'], event['name'], event['date'],
                    event['time'], event['venue'], event['description'], 1 if event['is_archived'] else 0
                ))
            # Restore archived events
            for archived_event in backup_data['archived_events']:
                self.conn.execute('''
                    INSERT INTO archived_events (id, user_id, name, date, time, venue, description, archived_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    archived_event['id'], archived_event['user_id'], archived_event['name'],
                    archived_event['date'], archived_event['time'], archived_event['venue'],
                    archived_event['description'], archived_event['archived_date']
                ))
            # Restore tasks
            for task in backup_data['tasks']:
                self.conn.execute('''
                    INSERT INTO tasks (id, event_id, description, is_completed)
                    VALUES (?, ?, ?, ?)
                ''', (
                    task['id'], task['event_id'], task['description'], 1 if task['is_completed'] else 0
                ))
            # Restore guests
            for guest in backup_data['guests']:
                self.conn.execute('''
                    INSERT INTO guests (id, event_id, name, email)
                    VALUES (?, ?, ?, ?)
                ''', (
                    guest['id'], guest['event_id'], guest['name'], guest['email']
                ))