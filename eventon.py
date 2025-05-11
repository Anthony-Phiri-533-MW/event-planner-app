import sqlite3
import csv
import json
import hashlib
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFormLayout, QDialog,
    QDialogButtonBox, QCalendarWidget, QDateEdit, QMessageBox, QTextBrowser,
    QStatusBar, QTimeEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QStyledItemDelegate, QScrollArea, QFileDialog,
    QStackedWidget, QTextEdit
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QTextCharFormat, QColor, QFont
import sys
from datetime import datetime

# Custom delegate for checkbox in table
class CheckBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        return None  # Prevent editing, we'll handle clicks directly

    def editorEvent(self, event, model, option, index):
        if event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
            current_value = index.data(Qt.CheckStateRole)
            new_value = Qt.Unchecked if current_value == Qt.Checked else Qt.Checked
            model.setData(index, new_value, Qt.CheckStateRole)
            return True
        return False

# SQLite database helper
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

class TaskDialog(QDialog):
    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Task" if task_data else "Add Task")
        self.layout = QFormLayout(self)
        self.desc_input = QLineEdit(self)
        self.completed_check = QCheckBox("Completed", self)
        if task_data:
            self.desc_input.setText(task_data['description'])
            self.completed_check.setChecked(task_data['completed'])
        self.layout.addRow("Task Description:", self.desc_input)
        self.layout.addRow(self.completed_check)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.validate)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def validate(self):
        if not self.desc_input.text().strip():
            QMessageBox.warning(self, "Error", "Task description is required")
            return
        self.accept()

    def get_data(self):
        return {
            "description": self.desc_input.text(),
            "completed": self.completed_check.isChecked()
        }

class GuestDialog(QDialog):
    def __init__(self, parent=None, guest_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Guest" if guest_data else "Add Guest")
        self.layout = QFormLayout(self)
        self.name_input = QLineEdit(self)
        self.email_input = QLineEdit(self)
        if guest_data:
            self.name_input.setText(guest_data['name'])
            self.email_input.setText(guest_data['email'])
        self.layout.addRow("Guest Name:", self.name_input)
        self.layout.addRow("Email:", self.email_input)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.validate)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def validate(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "Guest name is required")
            return
        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "email": self.email_input.text()
        }

class EventDialog(QDialog):
    def __init__(self, parent=None, event_data=None, edit_mode=False):
        super().__init__(parent)
        self.setWindowTitle("Edit Event" if edit_mode else "Create New Event")
        self.layout = QFormLayout(self)
        self.name_input = QLineEdit(self)
        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.time_input = QTimeEdit(self)
        self.time_input.setTime(QTime(19, 0))
        self.venue_input = QLineEdit(self)
        self.desc_input = QTextEdit(self)
        if event_data:
            self.name_input.setText(event_data['name'])
            self.date_input.setDate(QDate.fromString(event_data['date'], "yyyy-MM-dd"))
            if event_data['time']:
                self.time_input.setTime(QTime.fromString(event_data['time'], "HH:mm"))
            self.venue_input.setText(event_data['venue'])
            self.desc_input.setPlainText(event_data['description'])
        self.layout.addRow("Event Name:", self.name_input)
        self.layout.addRow("Date:", self.date_input)
        self.layout.addRow("Time:", self.time_input)
        self.layout.addRow("Venue:", self.venue_input)
        self.layout.addRow("Description:", self.desc_input)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.validate)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def validate(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "Event name is required")
            return
        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "time": self.time_input.time().toString("HH:mm"),
            "venue": self.venue_input.text(),
            "description": self.desc_input.toPlainText()
        }

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.layout = QFormLayout(self)
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addRow("Username:", self.username_input)
        self.layout.addRow("Password:", self.password_input)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.validate)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def validate(self):
        if not self.username_input.text().strip() or not self.password_input.text().strip():
            QMessageBox.warning(self, "Error", "Username and password are required")
            return
        self.accept()

    def get_credentials(self):
        return {
            "username": self.username_input.text(),
            "password": self.password_input.text()
        }

class SignupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sign Up")
        self.layout = QFormLayout(self)
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.email_input = QLineEdit(self)
        self.layout.addRow("Username:", self.username_input)
        self.layout.addRow("Password:", self.password_input)
        self.layout.addRow("Confirm Password:", self.confirm_password_input)
        self.layout.addRow("Email (optional):", self.email_input)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.validate)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def validate(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        email = self.email_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required")
            return
        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return
        self.accept()

    def get_user_data(self):
        return {
            "username": self.username_input.text(),
            "password": self.password_input.text(),
            "email": self.email_input.text() or None
        }

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_email=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.layout = QFormLayout(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.email_input = QLineEdit(self)
        self.api_url_input = QLineEdit(self)
        self.api_url_input.setText("https://event-planner-application-backup-api.onrender.com")
        if current_email:
            self.email_input.setText(current_email)
        self.layout.addRow("New Password (optional):", self.password_input)
        self.layout.addRow("Confirm New Password:", self.confirm_password_input)
        self.layout.addRow("Email (optional):", self.email_input)
        self.layout.addRow("API URL:", self.api_url_input)
        self.backup_btn = QPushButton("Backup Data")
        self.backup_btn.clicked.connect(self.perform_backup)
        self.layout.addWidget(self.backup_btn)
        self.recover_btn = QPushButton("Recover Data")
        self.recover_btn.clicked.connect(self.perform_recovery)
        self.layout.addWidget(self.recover_btn)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.validate)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def validate(self):
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        if password or confirm_password:
            if password != confirm_password:
                QMessageBox.warning(self, "Error", "Passwords do not match")
                return
            if len(password) < 6:
                QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
                return
        self.accept()

    def get_user_data(self):
        return {
            "password": self.password_input.text() or None,
            "email": self.email_input.text() or None
        }

    def perform_backup(self):
        api_url = self.api_url_input.text().strip()
        if not api_url:
            QMessageBox.warning(self, "Error", "API URL is required")
            return
        reply = QMessageBox.question(
            self, 'Backup Data',
            "Are you sure you want to backup your data to the specified API?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        parent = self.parent()
        if not hasattr(parent, 'current_user_id') or not parent.current_user_id:
            QMessageBox.warning(self, "Error", "No user is logged in")
            return
        try:
            data = parent.db.get_backup_data(parent.current_user_id)
            response = requests.post(f"{api_url}/backup", json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            parent.status_bar.showMessage(f"Backup completed: {result['message']}", 5000)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to connect to API: {str(e)}")
        except ValueError as e:
            QMessageBox.critical(self, "Backup Error", f"Invalid API response: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Backup failed: {str(e)}")

    def perform_recovery(self):
        api_url = self.api_url_input.text().strip()
        if not api_url:
            QMessageBox.warning(self, "Error", "API URL is required")
            return
        reply = QMessageBox.question(
            self, 'Recover Data',
            "This will overwrite your current data with the backup from the API. Are you sure you want to proceed?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        parent = self.parent()
        if not hasattr(parent, 'current_user_id') or not parent.current_user_id:
            QMessageBox.warning(self, "Error", "No user is logged in")
            return
        try:
            response = requests.get(f"{api_url}/recover/{parent.current_user_id}", timeout=10)
            response.raise_for_status()
            backup_data = response.json()
            parent.db.restore_backup_data(backup_data)
            parent.load_events()
            parent.status_bar.showMessage("Data recovered successfully", 5000)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                QMessageBox.critical(self, "Recovery Error", "No backup found for this user")
            else:
                QMessageBox.critical(self, "Recovery Error", f"API error: {str(e)}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Recovery Error", f"Failed to connect to API: {str(e)}")
        except ValueError as e:
            QMessageBox.critical(self, "Recovery Error", f"Invalid API response: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Recovery Error", f"Recovery failed: {str(e)}")

class EventPlannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db = EventDatabase()
        self.current_user_id = None
        self.current_username = None
        self.is_fullscreen = False
        self.is_dark_theme = True
        self.event_id_map = {}  # Map row to event ID
        self.task_id_map = {}   # Map row to task ID
        self.guest_id_map = {}  # Map row to guest ID
        self.stacked_widget = QStackedWidget()
        self.login_widget = QWidget()
        self.setup_login_ui()
        self.main_widget = QWidget()
        self.setup_main_ui()
        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.main_widget)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        self.stacked_widget.setCurrentIndex(0)
        self.setWindowTitle("Event Planner - Login")
        self.setMinimumSize(800, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.set_color_palette()

    def set_color_palette(self):
        if self.is_dark_theme:
            stylesheet = """
                QWidget {
                    background-color: #1E1E2F;
                    color: #FFFFFF;
                }
                QPushButton {
                    background-color: #3E4351;
                    color: #FFFFFF;
                    border: 1px solid #2C2F3A;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #575C66;
                }
                QPushButton.primary {
                    background-color: #FF6584;
                    font-weight: bold;
                }
                QPushButton.primary:hover {
                    background-color: #FF4B5C;
                }
                QPushButton.logout {
                    background-color: #FF4B5C;
                    font-weight: bold;
                }
                QPushButton.logout:hover {
                    background-color: #FF2D3D;
                }
                QPushButton.accent {
                    background-color: #FFCC00;
                    color: #000000;
                    font-weight: bold;
                }
                QPushButton.accent:hover {
                    background-color: #FFD633;
                }
                QPushButton.theme-toggle {
                    background-color: #42A5F5;
                    color: #FFFFFF;
                    font-weight: bold;
                }
                QPushButton.theme-toggle:hover {
                    background-color: #2196F3;
                }
                QTableWidget {
                    background-color: #2C2F3A;
                    alternate-background-color: #3E4351;
                    gridline-color: #2C2F3A;
                }
                QHeaderView::section {
                    background-color: #3E4351;
                    padding: 5px;
                    border: 1px solid #2C2F3A;
                }
                QCalendarWidget {
                    background-color: #2C2F3A;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    color: #FFFFFF;
                    selection-background-color: #42A5F5;
                    selection-color: #FFFFFF;
                }
                QLineEdit, QTextEdit, QTextBrowser {
                    background-color: #2C2F3A;
                    border: 1px solid #3E4351;
                    padding: 5px;
                    border-radius: 3px;
                    color: #FFFFFF;
                }
                QDialog {
                    background-color: #1E1E2F;
                }
                QLabel {
                    color: #FFFFFF;
                }
                QCheckBox {
                    color: #FFFFFF;
                }
                QScrollBar:vertical {
                    border: 1px solid #3E4351;
                    background: #2C2F3A;
                    width: 15px;
                    margin: 22px 0 22px 0;
                }
                QScrollBar::handle:vertical {
                    background: #3E4351;
                    min-height: 20px;
                }
                QScrollBar::add-line:vertical {
                    border: 1px solid #3E4351;
                    background: #2C2F3A;
                    height: 20px;
                    subcontrol-position: bottom;
                    subcontrol-origin: margin;
                }
                QScrollBar::sub-line:vertical {
                    border: 1px solid #3E4351;
                    background: #2C2F3A;
                    height: 20px;
                    subcontrol-position: top;
                    subcontrol-origin: margin;
                }
            """
        else:
            stylesheet = """
                QWidget {
                    background-color: #F5F5F5;
                    color: #333333;
                }
                QPushButton {
                    background-color: #E0E0E0;
                    color: #333333;
                    border: 1px solid #B0B0B0;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #D0D0D0;
                }
                QPushButton.primary {
                    background-color: #FF6584;
                    color: #FFFFFF;
                    font-weight: bold;
                }
                QPushButton.primary:hover {
                    background-color: #FF4B5C;
                }
                QPushButton.logout {
                    background-color: #FF4B5C;
                    color: #FFFFFF;
                    font-weight: bold;
                }
                QPushButton.logout:hover {
                    background-color: #FF2D3D;
                }
                QPushButton.accent {
                    background-color: #FFCC00;
                    color: #000000;
                    font-weight: bold;
                }
                QPushButton.accent:hover {
                    background-color: #FFD633;
                }
                QPushButton.theme-toggle {
                    background-color: #42A5F5;
                    color: #FFFFFF;
                    font-weight: bold;
                }
                QPushButton.theme-toggle:hover {
                    background-color: #2196F3;
                }
                QTableWidget {
                    background-color: #FFFFFF;
                    alternate-background-color: #F0F0F0;
                    gridline-color: #E0E0E0;
                }
                QHeaderView::section {
                    background-color: #E0E0E0;
                    padding: 5px;
                    border: 1px solid #B0B0B0;
                }
                QCalendarWidget {
                    background-color: #FFFFFF;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    color: #333333;
                    selection-background-color: #42A5F5;
                    selection-color: #FFFFFF;
                }
                QLineEdit, QTextEdit, QTextBrowser {
                    background-color: #FFFFFF;
                    border: 1px solid #B0B0B0;
                    padding: 5px;
                    border-radius: 3px;
                    color: #333333;
                }
                QDialog {
                    background-color: #F5F5F5;
                }
                QLabel {
                    color: #333333;
                }
                QCheckBox {
                    color: #333333;
                }
                QScrollBar:vertical {
                    border: 1px solid #B0B0B0;
                    background: #E0E0E0;
                    width: 15px;
                    margin: 22px 0 22px 0;
                }
                QScrollBar::handle:vertical {
                    background: #B0B0B0;
                    min-height: 20px;
                }
                QScrollBar::add-line:vertical {
                    border: 1px solid #B0B0B0;
                    background: #E0E0E0;
                    height: 20px;
                    subcontrol-position: bottom;
                    subcontrol-origin: margin;
                }
                QScrollBar::sub-line:vertical {
                    border: 1px solid #B0B0B0;
                    background: #E0E0E0;
                    height: 20px;
                    subcontrol-position: top;
                    subcontrol-origin: margin;
                }
            """
        self.setStyleSheet(stylesheet)

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.theme_toggle_btn.setText("Dark Theme" if self.is_dark_theme else "Light Theme")
        self.set_color_palette()

    def setup_login_ui(self):
        layout = QVBoxLayout(self.login_widget)
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel("Event Planner")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #FF6584;")
        layout.addWidget(title)
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(50, 20, 50, 20)
        button_container.setFixedWidth(300)
        login_btn = QPushButton("Login")
        login_btn.setFont(QFont("Arial", 12))
        login_btn.setStyleSheet("padding: 10px;")
        login_btn.setProperty("class", "primary")
        login_btn.clicked.connect(self.show_login_dialog)
        button_layout.addWidget(login_btn)
        signup_btn = QPushButton("Sign Up")
        signup_btn.setFont(QFont("Arial", 12))
        signup_btn.setStyleSheet("padding: 10px;")
        signup_btn.clicked.connect(self.show_signup_dialog)
        button_layout.addWidget(signup_btn)
        layout.addWidget(button_container)
        layout.addStretch()

    def setup_main_ui(self):
        layout = QHBoxLayout(self.main_widget)
        sidebar_widget = QWidget()
        self.sidebar = QVBoxLayout(sidebar_widget)
        self.sidebar.setContentsMargins(10, 10, 10, 10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search events...")
        self.search_input.textChanged.connect(self.search_events)
        self.sidebar.addWidget(self.search_input)
        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.calendar_date_selected)
        self.sidebar.addWidget(self.calendar)
        nav_layout = QHBoxLayout()
        self.today_btn = QPushButton("Today")
        self.today_btn.clicked.connect(self.go_to_today)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_selection)
        nav_layout.addWidget(self.today_btn)
        nav_layout.addWidget(self.clear_btn)
        self.sidebar.addLayout(nav_layout)
        self.view_toggle = QPushButton("View Archived Events")
        self.view_toggle.setCheckable(True)
        self.view_toggle.toggled.connect(self.toggle_event_view)
        self.sidebar.addWidget(self.view_toggle)
        button_layout = QVBoxLayout()
        self.add_event_btn = QPushButton("Add New Event")
        self.add_event_btn.setProperty("class", "primary")
        self.add_event_btn.clicked.connect(self.add_event)
        self.edit_event_btn = QPushButton("Edit Selected Event")
        self.edit_event_btn.clicked.connect(self.edit_event)
        self.delete_event_btn = QPushButton("Delete Selected Event")
        self.delete_event_btn.clicked.connect(self.delete_event)
        self.export_csv_btn = QPushButton("Export to CSV")
        self.export_csv_btn.setProperty("class", "accent")
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        self.export_json_btn = QPushButton("Export to JSON")
        self.export_json_btn.setProperty("class", "accent")
        self.export_json_btn.clicked.connect(self.export_to_json)
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setProperty("class", "accent")
        self.settings_btn.clicked.connect(self.show_settings_dialog)
        self.guest_buttons_layout = QHBoxLayout()
        self.add_guest_btn = QPushButton("Add Guest")
        self.add_guest_btn.clicked.connect(self.add_guest)
        self.edit_guest_btn = QPushButton("Edit Guest")
        self.edit_guest_btn.clicked.connect(self.edit_guest)
        self.delete_guest_btn = QPushButton("Delete Guest")
        self.delete_guest_btn.clicked.connect(self.delete_guest)
        self.guest_buttons_layout.addWidget(self.add_guest_btn)
        self.guest_buttons_layout.addWidget(self.edit_guest_btn)
        self.guest_buttons_layout.addWidget(self.delete_guest_btn)
        self.task_buttons_layout = QHBoxLayout()
        self.add_task_btn = QPushButton("Add Task")
        self.add_task_btn.clicked.connect(self.add_task)
        self.edit_task_btn = QPushButton("Edit Task")
        self.edit_task_btn.clicked.connect(self.edit_task)
        self.delete_task_btn = QPushButton("Delete Task")
        self.delete_task_btn.clicked.connect(self.delete_task)
        self.task_buttons_layout.addWidget(self.add_task_btn)
        self.task_buttons_layout.addWidget(self.edit_task_btn)
        self.task_buttons_layout.addWidget(self.delete_task_btn)
        self.archive_btn = QPushButton("Archive Event")
        self.archive_btn.setProperty("class", "accent")
        self.archive_btn.clicked.connect(self.archive_event)
        self.fullscreen_btn = QPushButton("Toggle Full Screen")
        self.fullscreen_btn.setProperty("class", "accent")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.theme_toggle_btn = QPushButton("Light Theme")
        self.theme_toggle_btn.setProperty("class", "theme-toggle")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setProperty("class", "logout")
        self.logout_btn.clicked.connect(self.logout)
        self.toggle_event_buttons(False)
        self.toggle_guest_buttons(False)
        self.toggle_task_buttons(False)
        self.archive_btn.setEnabled(False)
        button_layout.addWidget(self.add_event_btn)
        button_layout.addWidget(self.edit_event_btn)
        button_layout.addWidget(self.delete_event_btn)
        button_layout.addLayout(self.guest_buttons_layout)
        button_layout.addLayout(self.task_buttons_layout)
        button_layout.addWidget(self.archive_btn)
        button_layout.addWidget(self.export_csv_btn)
        button_layout.addWidget(self.export_json_btn)
        button_layout.addWidget(self.settings_btn)
        button_layout.addWidget(self.fullscreen_btn)
        button_layout.addWidget(self.theme_toggle_btn)
        button_layout.addWidget(self.logout_btn)
        button_layout.addStretch()
        self.sidebar.addLayout(button_layout)
        self.sidebar.addStretch()
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setWidget(sidebar_widget)
        sidebar_scroll.setFixedWidth(350)
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(10, 10, 10, 10)
        self.events_label = QLabel("Events")
        self.events_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(5)
        self.events_table.setHorizontalHeaderLabels(["Name", "Date", "Time", "Venue", "Description"])
        self.events_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.events_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.events_table.itemSelectionChanged.connect(self.on_event_selection_changed)
        right_panel.addWidget(self.events_label)
        right_panel.addWidget(self.events_table)
        self.details_label = QLabel("Details")
        self.details_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.details_panel = QTextBrowser()
        self.details_panel.setOpenExternalLinks(True)
        right_panel.addWidget(self.details_label)
        right_panel.addWidget(self.details_panel)
        self.guests_label = QLabel("Guests")
        self.guests_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.guests_table = QTableWidget()
        self.guests_table.setColumnCount(2)
        self.guests_table.setHorizontalHeaderLabels(["Name", "Email"])
        self.guests_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.guests_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.guests_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.guests_table.itemSelectionChanged.connect(self.on_guest_selection_changed)
        guests_scroll = QScrollArea()
        guests_scroll.setWidgetResizable(True)
        guests_scroll.setWidget(self.guests_table)
        right_panel.addWidget(self.guests_label)
        right_panel.addWidget(guests_scroll)
        self.tasks_label = QLabel("Tasks")
        self.tasks_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(2)
        self.tasks_table.setHorizontalHeaderLabels(["Description", "Completed"])
        self.tasks_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tasks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tasks_table.setItemDelegateForColumn(1, CheckBoxDelegate(self))
        self.tasks_table.itemChanged.connect(self.on_task_status_changed)
        self.tasks_table.itemSelectionChanged.connect(self.on_task_selection_changed)
        tasks_scroll = QScrollArea()
        tasks_scroll.setWidgetResizable(True)
        tasks_scroll.setWidget(self.tasks_table)
        right_panel.addWidget(self.tasks_label)
        right_panel.addWidget(tasks_scroll)
        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Arial", 9))
        right_panel.addWidget(self.status_bar)
        layout.addWidget(sidebar_scroll, 1)
        layout.addLayout(right_panel, 2)

    def toggle_event_buttons(self, enabled):
        self.edit_event_btn.setEnabled(enabled)
        self.delete_event_btn.setEnabled(enabled)
        self.add_guest_btn.setEnabled(enabled)
        self.add_task_btn.setEnabled(enabled)

    def toggle_guest_buttons(self, enabled):
        self.edit_guest_btn.setEnabled(enabled)
        self.delete_guest_btn.setEnabled(enabled)

    def toggle_task_buttons(self, enabled):
        self.edit_task_btn.setEnabled(enabled)
        self.delete_task_btn.setEnabled(enabled)

    def on_event_selection_changed(self):
        has_selection = bool(self.events_table.currentItem())
        self.toggle_event_buttons(has_selection)
        if has_selection:
            self.display_event_details()
        self.check_archive_status()

    def on_guest_selection_changed(self):
        self.toggle_guest_buttons(bool(self.guests_table.currentItem()))

    def on_task_selection_changed(self):
        self.toggle_task_buttons(bool(self.tasks_table.currentItem()))

    def on_task_status_changed(self, item):
        if item.column() == 1:
            row = item.row()
            task_id = self.task_id_map.get(row)
            if task_id is None:
                return
            is_completed = item.checkState() == Qt.Checked
            try:
                self.db.update_task_status(task_id, is_completed)
                self.check_archive_status()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def show_login_dialog(self):
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            credentials = dialog.get_credentials()
            user_id = self.db.authenticate_user(credentials['username'], credentials['password'])
            if user_id:
                self.current_user_id = user_id
                self.current_username = credentials['username']
                self.stacked_widget.setCurrentIndex(1)
                self.setWindowTitle(f"Event Planner - Welcome {self.current_username}")
                self.load_events()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password")

    def show_signup_dialog(self):
        dialog = SignupDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            user_data = dialog.get_user_data()
            user_id = self.db.create_user(
                user_data['username'],
                user_data['password'],
                user_data['email']
            )
            if user_id:
                QMessageBox.information(self, "Success", "Account created successfully! Please login.")
            else:
                QMessageBox.warning(self, "Error", "Username already exists")

    def show_settings_dialog(self):
        if not self.current_user_id:
            return
        current_email = self.db.get_user_email(self.current_user_id)
        dialog = SettingsDialog(self, current_email)
        if dialog.exec_() == QDialog.Accepted:
            user_data = dialog.get_user_data()
            try:
                self.db.update_user(
                    self.current_user_id,
                    password=user_data['password'],
                    email=user_data['email']
                )
                self.status_bar.showMessage("Settings updated successfully", 3000)
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def logout(self):
        self.current_user_id = None
        self.current_username = None
        self.stacked_widget.setCurrentIndex(0)
        self.setWindowTitle("Event Planner - Login")
        self.clear_selection()

    def add_event(self):
        if not self.current_user_id:
            return
        dialog = EventDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                event_id = self.db.add_event(
                    self.current_user_id,
                    data['name'],
                    data['date'],
                    data['time'],
                    data['venue'],
                    data['description']
                )
                self.status_bar.showMessage("Event added successfully", 3000)
                self.load_events()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def edit_event(self):
        if not self.events_table.currentItem() or not self.current_user_id:
            return
        current_row = self.events_table.currentRow()
        event_id = self.event_id_map.get(current_row)
        if event_id is None:
            return
        event = self.db.get_event_by_id(event_id)
        if not event or event[1] != self.current_user_id:
            QMessageBox.warning(self, "Error", "You can only edit your own events")
            return
        event_data = {
            'id': event[0],
            'name': event[2],
            'date': event[3],
            'time': event[4],
            'venue': event[5],
            'description': event[6]
        }
        dialog = EventDialog(self, event_data, edit_mode=True)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.update_event(event[0], data['name'], data['date'], 
                                   data['time'], data['venue'], data['description'])
                self.status_bar.showMessage("Event updated successfully", 3000)
                self.load_events()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def delete_event(self):
        if not self.events_table.currentItem() or not self.current_user_id:
            return
        current_row = self.events_table.currentRow()
        event_id = self.event_id_map.get(current_row)
        if event_id is None:
            return
        event_name = self.events_table.item(current_row, 0).text()
        event = self.db.get_event_by_id(event_id)
        if not event or event[1] != self.current_user_id:
            QMessageBox.warning(self, "Error", "You can only delete your own events")
            return
        reply = QMessageBox.question(
            self, 'Delete Event', 
            f"Are you sure you want to delete '{event_name}' and all its tasks/guests?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_event(event_id)
                self.status_bar.showMessage("Event deleted successfully", 3000)
                self.load_events()
                self.clear_selection()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def archive_event(self):
        if not self.current_user_id or not self.events_table.currentItem():
            return
        current_row = self.events_table.currentRow()
        event_id = self.event_id_map.get(current_row)
        if event_id is None:
            return
        event = self.db.get_event_by_id(event_id)
        if not event or event[1] != self.current_user_id:
            QMessageBox.warning(self, "Error", "You can only archive your own events")
            return
        tasks = self.db.get_tasks_for_event(event_id)
        if tasks and not all(task[3] for task in tasks):
            QMessageBox.warning(self, "Cannot Archive", 
                              "All tasks must be completed before archiving")
            return
        reply = QMessageBox.question(
            self, 'Archive Event', 
            f"Archive '{event[2]}' and all its tasks/guests?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                success = self.db.archive_event(event_id)
                if success:
                    self.status_bar.showMessage("Event archived successfully", 3000)
                    self.load_events(self.view_toggle.isChecked())
                    self.clear_selection()
                else:
                    QMessageBox.warning(self, "Error", "Failed to archive event")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def toggle_event_view(self, show_archived):
        self.view_toggle.setText("View Active Events" if show_archived else "View Archived Events")
        self.load_events(show_archived)

    def load_events(self, show_archived=False):
        if not self.current_user_id:
            return
        self.events_table.setRowCount(0)
        self.event_id_map.clear()
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        if show_archived:
            events = self.db.get_archived_events(self.current_user_id)
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(QColor("#3E4351" if self.is_dark_theme else "#E0E0E0"))
        else:
            events = self.db.get_all_events(self.current_user_id)
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(QColor("#FF6584"))
        self.events_table.setRowCount(len(events))
        for row, event in enumerate(events):
            date = QDate.fromString(event[3], "yyyy-MM-dd")
            if not show_archived:
                self.calendar.setDateTextFormat(date, highlight_format)
            self.event_id_map[row] = event[0]
            self.events_table.setItem(row, 0, QTableWidgetItem(event[2]))
            self.events_table.setItem(row, 1, QTableWidgetItem(event[3]))
            self.events_table.setItem(row, 2, QTableWidgetItem(event[4] if event[4] else ""))
            self.events_table.setItem(row, 3, QTableWidgetItem(event[5]))
            self.events_table.setItem(row, 4, QTableWidgetItem(event[6]))

    def display_event_details(self):
        if not self.events_table.currentItem() or not self.current_user_id:
            return
        current_row = self.events_table.currentRow()
        event_id = self.event_id_map.get(current_row)
        if event_id is None:
            return
        event = self.db.get_event_by_id(event_id)
        if not event or event[1] != self.current_user_id:
            return
        self.current_event_id = event_id
        time_str = f"<b>Time:</b> {event[4]}<br>" if event[4] else ""
        archived_str = "<b>Status:</b> Archived<br>" if len(event) > 7 and event[7] else ""
        details = (
            f"<h2>{event[2]}</h2>"
            f"<p><b>Date:</b> {event[3]}<br>"
            f"{time_str}"
            f"{archived_str}"
            f"<b>Venue:</b> {event[5]}</p>"
            f"<p>{event[6].replace('\n', '<br>')}</p>"
        )
        self.details_panel.setHtml(details)
        self.load_guests()
        self.load_tasks()

    def load_guests(self):
        self.guests_table.setRowCount(0)
        self.guest_id_map.clear()
        if not self.current_event_id:
            return
        guests = self.db.get_guests_for_event(self.current_event_id)
        self.guests_table.setRowCount(len(guests))
        for row, guest in enumerate(guests):
            self.guest_id_map[row] = guest[0]
            self.guests_table.setItem(row, 0, QTableWidgetItem(guest[2]))
            self.guests_table.setItem(row, 1, QTableWidgetItem(guest[3] or ""))
        self.guests_label.setText(f"Guests ({len(guests)})")

    def load_tasks(self):
        self.tasks_table.setRowCount(0)
        self.task_id_map.clear()
        if not self.current_event_id:
            return
        tasks = self.db.get_tasks_for_event(self.current_event_id)
        self.tasks_table.setRowCount(len(tasks))
        for row, task in enumerate(tasks):
            self.task_id_map[row] = task[0]
            self.tasks_table.setItem(row, 0, QTableWidgetItem(task[2]))
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Checked if task[3] else Qt.Unchecked)
            self.tasks_table.setItem(row, 1, item)
        self.tasks_label.setText(f"Tasks ({len(tasks)})")
        self.check_archive_status()

    def check_archive_status(self):
        if not self.current_event_id:
            self.archive_btn.setEnabled(False)
            return
        tasks = self.db.get_tasks_for_event(self.current_event_id)
        can_archive = not tasks or all(task[3] for task in tasks)
        self.archive_btn.setEnabled(can_archive and not self.view_toggle.isChecked())

    def add_guest(self):
        if not self.current_event_id:
            return
        dialog = GuestDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.add_guest(self.current_event_id, data['name'], data['email'])
                self.status_bar.showMessage("Guest added successfully", 3000)
                self.load_guests()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def edit_guest(self):
        if not self.guests_table.currentItem() or not self.current_event_id:
            return
        current_row = self.guests_table.currentRow()
        guest_id = self.guest_id_map.get(current_row)
        if guest_id is None:
            return
        guest_name = self.guests_table.item(current_row, 0).text()
        guest_email = self.guests_table.item(current_row, 1).text()
        dialog = GuestDialog(self, {
            'name': guest_name,
            'email': guest_email
        })
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.delete_guest(guest_id)
                self.db.add_guest(self.current_event_id, data['name'], data['email'])
                self.status_bar.showMessage("Guest updated successfully", 3000)
                self.load_guests()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def delete_guest(self):
        if not self.guests_table.currentItem():
            return
        current_row = self.guests_table.currentRow()
        guest_id = self.guest_id_map.get(current_row)
        if guest_id is None:
            return
        guest_name = self.guests_table.item(current_row, 0).text()
        reply = QMessageBox.question(
            self, 'Delete Guest', 
            f"Are you sure you want to delete guest '{guest_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_guest(guest_id)
                self.status_bar.showMessage("Guest deleted successfully", 3000)
                self.load_guests()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def add_task(self):
        if not self.current_event_id:
            return
        dialog = TaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.add_task(self.current_event_id, data['description'])
                if data['completed']:
                    cursor = self.db.conn.cursor()
                    cursor.execute('SELECT last_insert_rowid()')
                    new_task_id = cursor.fetchone()[0]
                    self.db.update_task_status(new_task_id, data['completed'])
                self.status_bar.showMessage("Task added successfully", 3000)
                self.load_tasks()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def edit_task(self):
        if not self.tasks_table.currentItem():
            return
        current_row = self.tasks_table.currentRow()
        task_id = self.task_id_map.get(current_row)
        if task_id is None:
            return
        task_desc = self.tasks_table.item(current_row, 0).text()
        task_completed = self.tasks_table.item(current_row, 1).checkState() == Qt.Checked
        dialog = TaskDialog(self, {
            'description': task_desc,
            'completed': task_completed
        })
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.delete_task(task_id)
                self.db.add_task(self.current_event_id, data['description'])
                if data['completed']:
                    cursor = self.db.conn.cursor()
                    cursor.execute('SELECT last_insert_rowid()')
                    new_task_id = cursor.fetchone()[0]
                    self.db.update_task_status(new_task_id, data['completed'])
                self.status_bar.showMessage("Task updated successfully", 3000)
                self.load_tasks()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def delete_task(self):
        if not self.tasks_table.currentItem():
            return
        current_row = self.tasks_table.currentRow()
        task_id = self.task_id_map.get(current_row)
        if task_id is None:
            return
        task_desc = self.tasks_table.item(current_row, 0).text()
        reply = QMessageBox.question(
            self, 'Delete Task', 
            f"Are you sure you want to delete task '{task_desc}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_task(task_id)
                self.status_bar.showMessage("Task deleted successfully", 3000)
                self.load_tasks()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def export_to_csv(self):
        if not self.current_user_id:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "", "CSV Files (*.csv)"
        )
        if filename:
            if not filename.endswith('.csv'):
                filename += '.csv'
            try:
                self.db.export_to_csv(self.current_user_id, filename[:-4])
                self.status_bar.showMessage("Data exported to CSV successfully", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def export_to_json(self):
        if not self.current_user_id:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export to JSON", "", "JSON Files (*.json)"
        )
        if filename:
            if not filename.endswith('.json'):
                filename += '.json'
            try:
                self.db.export_to_json(self.current_user_id, filename[:-5])
                self.status_bar.showMessage("Data exported to JSON successfully", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def search_events(self, text):
        if not self.current_user_id:
            return
        self.events_table.setRowCount(0)
        self.event_id_map.clear()
        events = self.db.search_events(self.current_user_id, text) if text else self.db.get_all_events(self.current_user_id)
        self.events_table.setRowCount(len(events))
        for row, event in enumerate(events):
            self.event_id_map[row] = event[0]
            self.events_table.setItem(row, 0, QTableWidgetItem(event[2]))
            self.events_table.setItem(row, 1, QTableWidgetItem(event[3]))
            self.events_table.setItem(row, 2, QTableWidgetItem(event[4] if event[4] else ""))
            self.events_table.setItem(row, 3, QTableWidgetItem(event[5]))
            self.events_table.setItem(row, 4, QTableWidgetItem(event[6]))

    def calendar_date_selected(self):
        if not self.current_user_id:
            return
        date_str = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.events_table.setRowCount(0)
        self.event_id_map.clear()
        events = self.db.get_events_by_date(self.current_user_id, date_str)
        self.events_table.setRowCount(len(events))
        for row, event in enumerate(events):
            self.event_id_map[row] = event[0]
            self.events_table.setItem(row, 0, QTableWidgetItem(event[2]))
            self.events_table.setItem(row, 1, QTableWidgetItem(event[3]))
            self.events_table.setItem(row, 2, QTableWidgetItem(event[4] if event[4] else ""))
            self.events_table.setItem(row, 3, QTableWidgetItem(event[5]))
            self.events_table.setItem(row, 4, QTableWidgetItem(event[6]))

    def go_to_today(self):
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar_date_selected()

    def clear_selection(self):
        self.events_table.clearSelection()
        self.details_panel.clear()
        self.guests_table.setRowCount(0)
        self.guests_label.setText("Guests")
        self.tasks_table.setRowCount(0)
        self.tasks_label.setText("Tasks")
        self.current_event_id = None
        self.event_id_map.clear()
        self.task_id_map.clear()
        self.guest_id_map.clear()
        self.toggle_event_buttons(False)
        self.toggle_guest_buttons(False)
        self.toggle_task_buttons(False)
        self.archive_btn.setEnabled(False)

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
            self.fullscreen_btn.setText("Toggle Full Screen")
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("Exit Full Screen")
            self.is_fullscreen = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = EventPlannerApp()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec_())