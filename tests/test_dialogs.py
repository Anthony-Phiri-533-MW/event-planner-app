import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QLineEdit, QDateEdit, QTimeEdit, QCheckBox
from PyQt5.QtCore import QDate, QTime
from event_planner.dialogs import (
    TaskDialog, GuestDialog, EventDialog, LoginDialog, SignupDialog, SettingsDialog
)
from event_planner.database import EventDatabase

@pytest.fixture
def task_dialog():
    with patch('PyQt5.QtWidgets.QDialog.__init__', return_value=None):
        dialog = TaskDialog()
        dialog.desc_input = MagicMock(spec=QLineEdit)
        dialog.completed_check = MagicMock(spec=QCheckBox)
        dialog.accepted = False
        yield dialog

def test_task_dialog_validate_valid_input(task_dialog):
    task_dialog.desc_input.text.return_value = "Task 1"
    task_dialog.validate()
    assert task_dialog.accepted

def test_task_dialog_validate_empty_description(task_dialog):
    task_dialog.desc_input.text.return_value = ""
    task_dialog.validate()
    assert not task_dialog.accepted

def test_task_dialog_get_data(task_dialog):
    task_dialog.desc_input.text.return_value = "Task 1"
    task_dialog.completed_check.isChecked.return_value = True
    data = task_dialog.get_data()
    assert data == {"description": "Task 1", "completed": True}

@pytest.fixture
def guest_dialog():
    with patch('PyQt5.QtWidgets.QDialog.__init__', return_value=None):
        dialog = GuestDialog()
        dialog.name_input = MagicMock(spec=QLineEdit)
        dialog.email_input = MagicMock(spec=QLineEdit)
        dialog.accepted = False
        yield dialog

def test_guest_dialog_validate_valid_input(guest_dialog):
    guest_dialog.name_input.text.return_value = "Guest 1"
    guest_dialog.validate()
    assert guest_dialog.accepted

def test_guest_dialog_validate_empty_name(guest_dialog):
    guest_dialog.name_input.text.return_value = ""
    guest_dialog.validate()
    assert not guest_dialog.accepted

def test_guest_dialog_get_data(guest_dialog):
    guest_dialog.name_input.text.return_value = "Guest 1"
    guest_dialog.email_input.text.return_value = "guest@example.com"
    data = guest_dialog.get_data()
    assert data == {"name": "Guest 1", "email": "guest@example.com"}

@pytest.fixture
def event_dialog():
    with patch('PyQt5.QtWidgets.QDialog.__init__', return_value=None):
        dialog = EventDialog()
        dialog.name_input = MagicMock(spec=QLineEdit)
        dialog.date_input = MagicMock(spec=QDateEdit)
        dialog.time_input = MagicMock(spec=QTimeEdit)
        dialog.venue_input = MagicMock(spec=QLineEdit)
        dialog.desc_input = MagicMock()
        dialog.accepted = False
        yield dialog

def test_event_dialog_validate_valid_input(event_dialog):
    event_dialog.name_input.text.return_value = "Event 1"
    event_dialog.validate()
    assert event_dialog.accepted

def test_event_dialog_validate_empty_name(event_dialog):
    event_dialog.name_input.text.return_value = ""
    event_dialog.validate()
    assert not event_dialog.accepted

def test_event_dialog_get_data(event_dialog):
    event_dialog.name_input.text.return_value = "Event 1"
    event_dialog.date_input.date.return_value.toString.return_value = "2025-06-01"
    event_dialog.time_input.time.return_value.toString.return_value = "12:00"
    event_dialog.venue_input.text.return_value = "Venue"
    event_dialog.desc_input.toPlainText.return_value = "Desc"
    data = event_dialog.get_data()
    assert data == {
        "name": "Event 1",
        "date": "2025-06-01",
        "time": "12:00",
        "venue": "Venue",
        "description": "Desc"
    }

@pytest.fixture
def login_dialog():
    with patch('PyQt5.QtWidgets.QDialog.__init__', return_value=None):
        dialog = LoginDialog()
        dialog.username_input = MagicMock(spec=QLineEdit)
        dialog.password_input = MagicMock(spec=QLineEdit)
        dialog.accepted = False
        yield dialog

def test_login_dialog_validate_valid_input(login_dialog):
    login_dialog.username_input.text.return_value = "test_user"
    login_dialog.password_input.text.return_value = "password"
    login_dialog.validate()
    assert login_dialog.accepted

def test_login_dialog_validate_empty_input(login_dialog):
    login_dialog.username_input.text.return_value = ""
    login_dialog.password_input.text.return_value = ""
    login_dialog.validate()
    assert not login_dialog.accepted

def test_login_dialog_get_credentials(login_dialog):
    login_dialog.username_input.text.return_value = "test_user"
    login_dialog.password_input.text.return_value = "password"
    credentials = login_dialog.get_credentials()
    assert credentials == {"username": "test_user", "password": "password"}

@pytest.fixture
def signup_dialog():
    with patch('PyQt5.QtWidgets.QDialog.__init__', return_value=None):
        dialog = SignupDialog()
        dialog.username_input = MagicMock(spec=QLineEdit)
        dialog.password_input = MagicMock(spec=QLineEdit)
        dialog.confirm_password_input = MagicMock(spec=QLineEdit)
        dialog.email_input = MagicMock(spec=QLineEdit)
        dialog.accepted = False
        yield dialog

def test_signup_dialog_validate_valid_input(signup_dialog):
    signup_dialog.username_input.text.return_value = "test_user"
    signup_dialog.password_input.text.return_value = "password123"
    signup_dialog.confirm_password_input.text.return_value = "password123"
    signup_dialog.email_input.text.return_value = "test@example.com"
    signup_dialog.validate()
    assert signup_dialog.accepted

def test_signup_dialog_validate_password_mismatch(signup_dialog):
    signup_dialog.username_input.text.return_value = "test_user"
    signup_dialog.password_input.text.return_value = "password123"
    signup_dialog.confirm_password_input.text.return_value = "different"
    signup_dialog.validate()
    assert not signup_dialog.accepted

def test_signup_dialog_validate_short_password(signup_dialog):
    signup_dialog.username_input.text.return_value = "test_user"
    signup_dialog.password_input.text.return_value = "short"
    signup_dialog.confirm_password_input.text.return_value = "short"
    signup_dialog.validate()
    assert not signup_dialog.accepted

def test_signup_dialog_get_user_data(signup_dialog):
    signup_dialog.username_input.text.return_value = "test_user"
    signup_dialog.password_input.text.return_value = "password123"
    signup_dialog.email_input.text.return_value = "test@example.com"
    data = signup_dialog.get_user_data()
    assert data == {
        "username": "test_user",
        "password": "password123",
        "email": "test@example.com"
    }

@pytest.fixture
def settings_dialog():
    with patch('PyQt5.QtWidgets.QDialog.__init__', return_value=None):
        with patch('event_planner.database.EventDatabase') as mock_db:
            dialog = SettingsDialog(current_email="test@example.com")
            dialog.password_input = MagicMock(spec=QLineEdit)
            dialog.confirm_password_input = MagicMock(spec=QLineEdit)
            dialog.email_input = MagicMock(spec=QLineEdit)
            dialog.api_url_input = MagicMock(spec=QLineEdit)
            dialog.accepted = False
            yield dialog, mock_db.return_value

def test_settings_dialog_validate_valid_input(settings_dialog):
    dialog, _ = settings_dialog
    dialog.password_input.text.return_value = "newpassword123"
    dialog.confirm_password_input.text.return_value = "newpassword123"
    dialog.email_input.text.return_value = "new@example.com"
    dialog.validate()
    assert dialog.accepted

def test_settings_dialog_validate_password_mismatch(settings_dialog):
    dialog, _ = settings_dialog
    dialog.password_input.text.return_value = "newpassword123"
    dialog.confirm_password_input.text.return_value = "different"
    dialog.validate()
    assert not dialog.accepted

def test_settings_dialog_validate_short_password(settings_dialog):
    dialog, _ = settings_dialog
    dialog.password_input.text.return_value = "short"
    dialog.confirm_password_input.text.return_value = "short"
    dialog.validate()
    assert not dialog.accepted

def test_settings_dialog_get_user_data(settings_dialog):
    dialog, _ = settings_dialog
    dialog.password_input.text.return_value = "newpassword123"
    dialog.email_input.text.return_value = "new@example.com"
    data = dialog.get_user_data()
    assert data == {"password": "newpassword123", "email": "new@example.com"}

def test_settings_dialog_perform_backup(settings_dialog):
    dialog, mock_db = settings_dialog
    dialog.api_url_input.text.return_value = "https://example.com"
    parent = MagicMock()
    parent.current_user_id = 1
    parent.db.get_backup_data.return_value = {"user_id": 1, "data": "test"}
    dialog.setParent(parent)
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {"message": "Backup successful"}
        dialog.perform_backup()
    
        mock_post.assert_called_with(
            "https://example.com/backup",
            json={"user_id": 1, "data": "test"},
            timeout=10
        )
        parent.status_bar.showMessage.assert_called_with("Backup completed: Backup successful", 5000)