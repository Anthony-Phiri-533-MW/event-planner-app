import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QDialog
from event_planner.app import EventPlannerApp
from event_planner.database import EventDatabase

@pytest.fixture
def mock_db():
    with patch('event_planner.database.EventDatabase') as mock:
        yield mock.return_value

@pytest.fixture
def app(mock_db):
    with patch('event_planner.app.QWidget.__init__', return_value=None):
        app = EventPlannerApp()
        app.stacked_widget = MagicMock()
        app.search_input = MagicMock()
        app.events_table = MagicMock()
        app.guests_table = MagicMock()
        app.tasks_table = MagicMock()
        app.details_panel = MagicMock()
        app.status_bar = MagicMock()
        app.fullscreen_btn = MagicMock()
        app.current_user_id = 1
        app.current_username = "test_user"
        app.event_id_map = {}
        app.guest_id_map = {}
        app.task_id_map = {}
        app.is_fullscreen = False
        app.current_event_id = None
        yield app

def test_show_login_dialog_success(app, mock_db):
    with patch('event_planner.dialogs.LoginDialog') as mock_login_dialog:
        mock_dialog = mock_login_dialog.return_value
        mock_dialog.exec_.return_value = QDialog.Accepted
        mock_dialog.get_credentials.return_value = {'username': 'test_user', 'password': 'password'}
        mock_db.authenticate_user.return_value = 1

        app.show_login_dialog()

        mock_login_dialog.assert_called_with(app)
        mock_db.authenticate_user.assert_called_with('test_user', 'password')
        app.stacked_widget.setCurrentIndex.assert_called_with(1)
        assert app.current_user_id == 1
        assert app.current_username == 'test_user'
        app.load_events.assert_called_once()

def test_show_login_dialog_failure(app, mock_db):
    with patch('event_planner.dialogs.LoginDialog') as mock_login_dialog:
        mock_dialog = mock_login_dialog.return_value
        mock_dialog.exec_.return_value = QDialog.Accepted
        mock_dialog.get_credentials.return_value = {'username': 'test_user', 'password': 'wrong'}
        mock_db.authenticate_user.return_value = None

        app.show_login_dialog()

        mock_login_dialog.assert_called_with(app)
        mock_db.authenticate_user.assert_called_with('test_user', 'wrong')
        app.stacked_widget.setCurrentIndex.assert_not_called()
        assert app.current_user_id == 1  # Unchanged from fixture

def test_show_signup_dialog(app, mock_db):
    with patch('event_planner.dialogs.SignupDialog') as mock_signup_dialog:
        mock_dialog = mock_signup_dialog.return_value
        mock_dialog.exec_.return_value = QDialog.Accepted
        mock_dialog.get_user_data.return_value = {
            'username': 'new_user', 'password': 'password', 'email': 'new@example.com'
        }
        mock_db.create_user.return_value = 2

        app.show_signup_dialog()

        mock_signup_dialog.assert_called_with(app)
        mock_db.create_user.assert_called_with('new_user', 'password', 'new@example.com')
        app.status_bar.showMessage.assert_not_called()  # Message shown via QMessageBox

def test_load_events(app, mock_db):
    mock_db.get_all_events.return_value = [
        (1, 1, "Event 1", "2025-06-01", "12:00", "Venue", "Desc", 0)
    ]
    app.load_events()

    mock_db.get_all_events.assert_called_with(1)
    app.events_table.setRowCount.assert_called_with(1)
    assert app.event_id_map == {0: 1}

def test_add_event(app, mock_db):
    with patch('event_planner.dialogs.EventDialog') as mock_event_dialog:
        mock_dialog = mock_event_dialog.return_value
        mock_dialog.exec_.return_value = QDialog.Accepted
        mock_dialog.get_data.return_value = {
            'name': 'Event 2', 'date': '2025-06-02', 'time': '14:00',
            'venue': 'New Venue', 'description': 'New Desc'
        }
        mock_db.add_event.return_value = 2

        app.add_event()

        mock_event_dialog.assert_called_with(app)
        mock_db.add_event.assert_called_with(
            1, 'Event 2', '2025-06-02', '14:00', 'New Venue', 'New Desc'
        )
        app.status_bar.showMessage.assert_called_with("Event added successfully", 3000)
        app.load_events.assert_called_once()

def test_toggle_fullscreen(app):
    app.is_fullscreen = False
    app.toggle_fullscreen()
    app.showFullScreen.assert_called_once()
    assert app.is_fullscreen
    app.fullscreen_btn.setText.assert_called_with("Exit Full Screen")

    app.is_fullscreen = True
    app.toggle_fullscreen()
    app.showNormal.assert_called_once()
    assert not app.is_fullscreen
    app.fullscreen_btn.setText.assert_called_with("Toggle Full Screen")

def test_logout(app):
    app.logout()
    assert app.current_user_id is None
    assert app.current_username is None
    app.stacked_widget.setCurrentIndex.assert_called_with(0)
    app.clear_selection.assert_called_once()

def test_add_guest(app, mock_db):
    app.current_event_id = 1
    with patch('event_planner.dialogs.GuestDialog') as mock_guest_dialog:
        mock_dialog = mock_guest_dialog.return_value
        mock_dialog.exec_.return_value = QDialog.Accepted
        mock_dialog.get_data.return_value = {'name': 'Guest 1', 'email': 'guest@example.com'}

        app.add_guest()

        mock_guest_dialog.assert_called_with(app)
        mock_db.add_guest.assert_called_with(1, 'Guest 1', 'guest@example.com')
        app.load_guests.assert_called_once()

def test_add_task(app, mock_db):
    app.current_event_id = 1
    with patch('event_planner.dialogs.TaskDialog') as mock_task_dialog:
        mock_dialog = mock_task_dialog.return_value
        mock_dialog.exec_.return_value = QDialog.Accepted
        mock_dialog.get_data.return_value = {'description': 'Task 1', 'completed': True}
        mock_db.conn.cursor.return_value.fetchone.return_value = [1]

        app.add_task()

        mock_task_dialog.assert_called_with(app)
        mock_db.add_task.assert_called_with(1, 'Task 1')
        mock_db.update_task_status.assert_called_with(1, True)
        app.load_tasks.assert_called_once()