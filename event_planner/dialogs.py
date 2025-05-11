from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QDateEdit,
    QMessageBox, QTimeEdit, QCheckBox, QTextEdit, QTextBrowser, QPushButton
)
from PyQt5.QtCore import Qt, QDate, QTime
import requests

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