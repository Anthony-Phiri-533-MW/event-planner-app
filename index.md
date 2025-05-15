# Event Planner Technical Documentation

## Overview

The **Event Planner** is a desktop application for managing events, tasks, and guest lists. Built with Python 3.8+ and PyQt5, it uses a SQLite database for persistent storage and supports user authentication, event management, and data export. The application is modularized in the `event_planner` package, with a clear separation of concerns across UI, database, and logic.

- **Source Location**: `/home/fantasma/projects/event-planner-app/event_planner`
- **Entry Point**: `event_planner/main.py`
- **Dependencies**: PyQt5, requests, SQLite (built-in)
- **Database**: `events.db` (SQLite, created in the project root)
- **Run Script**: `run.sh` (activates virtual environment, runs `python -m event_planner.main`)

## Architecture

The application follows a **Model-View-Controller (MVC)-like** architecture, with PyQt5 handling the view, SQLite managing the model, and custom logic in Python acting as the controller.

### Components

1. **UI Layer** (`app.py`, `dialogs.py`, `delegates.py`):

   - Built with PyQt5, providing a graphical interface.
   - Includes windows (`LoginWindow`, `MainWindow`) and dialogs (`SignupDialog`, `EventDialog`, `TaskDialog`, `GuestDialog`).
   - Uses custom delegates for table rendering.

2. **Data Layer** (`database.py`):

   - Manages SQLite database (`events.db`).
   - Handles user authentication, event storage, and task/guest management.

3. **Controller Layer** (`app.py`, `dialogs.py`):

   - Mediates between UI and database.
   - Implements business logic (e.g., validation, event creation).

4. **Entry Point** (`main.py`):

   - Initializes the PyQt5 application and launches the `LoginWindow`.

5. **Package** (`__init__.py`):

   - Makes `event_planner` a Python package, enabling modular imports.

### Directory Structure

```
/home/fantasma/projects/event-planner-app/
├── run.sh                # Script to run the app
├── .gitignore            # Excludes build/, dist/, events.db, etc.
├── requirements.txt      # Lists PyQt5, requests
├── event_planner/
│   ├── __init__.py       # Package marker
│   ├── main.py           # Application entry point
│   ├── app.py            # UI and controller logic
│   ├── database.py       # Database operations
│   ├── delegates.py      # Custom table delegates
│   ├── dialogs.py        # Dialog windows
└── events.db             # SQLite database (generated)
```

### Data Flow

1. User launches `run.sh`, which activates the virtual environment and runs `python -m event_planner.main`.
2. `main.py` creates a `QApplication` and shows `LoginWindow` (`app.py`).
3. User signs up/logs in, interacting with `EventDatabase` (`database.py`) for authentication.
4. Upon login, `MainWindow` (`app.py`) displays events, fetched from `events.db`.
5. User actions (e.g., add event, task) trigger dialogs (`dialogs.py`), which update the database via `EventDatabase`.
6. Custom delegates (`delegates.py`) enhance table displays in `MainWindow`.

## Module Breakdown

Below is a detailed explanation of each module, its classes/functions, and their roles.

### 1. `main.py`

**Purpose**: Entry point for the application. Initializes the PyQt5 app and launches the login window.

**Key Code**:

```python
import sys
from PyQt5.QtWidgets import QApplication
from event_planner.app import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
```

**Functions**:

- **Main Block**:
  - Creates a `QApplication` instance, required for PyQt5 apps.
  - Instantiates `LoginWindow` and shows it.
  - Runs the event loop with `app.exec_()`, handling UI interactions.

**Role**:

- Serves as the application’s starting point, ensuring proper initialization of the PyQt5 environment.

### 2. `app.py`

**Purpose**: Defines the main UI components (`LoginWindow`, `MainWindow`) and core controller logic. Manages user authentication and navigation.

**Key Classes**:

- `LoginWindow(QMainWindow)`:

  - **Purpose**: Displays the login/signup interface.
  - **Attributes**:
    - `db`: `EventDatabase` instance for authentication.
    - `ui`: PyQt5 widgets (e.g., `QLineEdit` for username/password, `QPushButton` for login/signup).
  - **Methods**:
    - `__init__()`: Sets up the UI (labels, inputs, buttons) and connects signals (e.g., button clicks).
    - `login()`: Validates credentials via `db.authenticate_user()`. Shows `MainWindow` on success or `QMessageBox` on failure.
    - `show_signup()`: Opens `SignupDialog` for new users.
  - **Role**: Handles user authentication and directs users to the main interface or signup.

- `MainWindow(QMainWindow)`:

  - **Purpose**: Displays the event list and provides controls for event/task/guest management.
  - **Attributes**:
    - `db`: `EventDatabase` for data operations.
    - `table`: `QTableView` for displaying events.
    - `model`: `QStandardItemModel` for table data.
  - **Methods**:
    - `__init__()`: Sets up the UI (menu bar, toolbar, table), connects actions (e.g., add event, fullscreen).
    - `load_events()`: Fetches events from `db.get_events()` and populates the table.
    - `add_event()`: Opens `EventDialog` to create a new event.
    - `edit_event()`: Opens `EventDialog` for editing an existing event.
    - `delete_event()`: Deletes the selected event via `db.delete_event()`.
    - `toggle_fullscreen()`: Toggles fullscreen mode using `showFullScreen()`/`showNormal()`.
    - `export_data()`: Exports events to CSV (placeholder, implementation incomplete).
    - `logout()`: Closes the window and shows `LoginWindow`.
  - **Role**: Central hub for event management, coordinating UI interactions and database updates.

**Key Code**:

```python
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QPushButton, QMessageBox, QTableView
from event_planner.database import EventDatabase
from event_planner.dialogs import SignupDialog, EventDialog

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = EventDatabase()
        self.setWindowTitle("Event Planner - Login")
        # Setup UI (username, password inputs, login/signup buttons)
        self.login_button.clicked.connect(self.login)
        self.signup_button.clicked.connect(self.show_signup)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.db.authenticate_user(username, password):
            self.main_window = MainWindow(self.db, username)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")

    def show_signup(self):
        dialog = SignupDialog(self.db, self)
        dialog.exec_()

class MainWindow(QMainWindow):
    def __init__(self, db, username):
        super().__init__()
        self.db = db
        self.username = username
        self.setWindowTitle(f"Event Planner - {username}")
        self.table = QTableView()
        self.load_events()
        # Setup menu, toolbar, and connect actions
        self.add_event_action.triggered.connect(self.add_event)
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)

    def load_events(self):
        events = self.db.get_events(self.username)
        # Populate table with event data
```

**Role**:

- `LoginWindow` ensures secure access and user registration.
- `MainWindow` provides the primary interface for event management, integrating with dialogs and the database.

### 3. `database.py`

**Purpose**: Manages the SQLite database (`events.db`), handling user accounts, events, tasks, and guests.

**Key Class**:

- `EventDatabase`:
  - **Purpose**: Encapsulates database operations.
  - **Attributes**:
    - `conn`: SQLite connection to `events.db`.
    - `cursor`: SQLite cursor for executing queries.
  - **Methods**:
    - `__init__()`: Initializes the database, creates tables (`users`, `events`, `tasks`, `guests`).
    - `create_tables()`: Defines schema for users (username, password hash), events (name, date, location), tasks (name, due date, status), and guests (name, contact, status).
    - `add_user(username, password)`: Hashes password and inserts a new user.
    - `authenticate_user(username, password)`: Verifies credentials by comparing hashed passwords.
    - `add_event(username, name, date, time, location, description)`: Inserts an event for a user.
    - `get_events(username)`: Retrieves all events for a user.
    - `update_event(event_id, ...)`: Updates an event’s details.
    - `delete_event(event_id)`: Deletes an event and its tasks/guests.
    - `add_task(event_id, name, due_date, status)`: Adds a task to an event.
    - `get_tasks(event_id)`: Retrieves tasks for an event.
    - `update_task(task_id, ...)`: Updates a task.
    - `delete_task(task_id)`: Deletes a task.
    - `add_guest(event_id, name, contact, status)`: Adds a guest.
    - `get_guests(event_id)`: Retrieves guests.
    - `update_guest(guest_id, ...)`: Updates a guest.
    - `delete_guest(guest_id)`: Deletes a guest.

**Key Code**:

```python
import sqlite3
import hashlib

class EventDatabase:
    def __init__(self):
        self.conn = sqlite3.connect("events.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                name TEXT,
                date TEXT,
                time TEXT,
                location TEXT,
                description TEXT,
                FOREIGN KEY(username) REFERENCES users(username)
            )
        """)
        # Similar tables for tasks, guests
        self.conn.commit()

    def add_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                          (username, hashed_password))
        self.conn.commit()

    def authenticate_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        return result and result[0] == hashed_password
```

**Role**:

- Provides a robust data layer, ensuring data persistence and integrity.
- Uses parameterized queries to prevent SQL injection.
- Hashes passwords for security.

### 4. `dialogs.py`

**Purpose**: Defines dialog windows for user input (signup, event creation, task/guest management).

**Key Classes**:

- `SignupDialog(QDialog)`:

  - **Purpose**: Collects username and password for new users.
  - **Methods**:
    - `__init__(db, parent)`: Sets up inputs for username, password, and confirmation.
    - `accept()`: Validates input (password match, unique username) and calls `db.add_user()`.
  - **Role**: Facilitates user registration.

- `EventDialog(QDialog)`:

  - **Purpose**: Collects event details and manages tasks/guests.
  - **Methods**:
    - `__init__(db, username, event_id=None)`: Sets up inputs (name, date, time, location, description) and tabs for tasks/guests.
    - `save_event()`: Inserts or updates an event via `db.add_event()` or `db.update_event()`.
    - `add_task()`: Opens `TaskDialog` to add a task.
    - `add_guest()`: Opens `GuestDialog` to add a guest.
  - **Role**: Central dialog for event management.

- `TaskDialog(QDialog)`:

  - **Purpose**: Collects task details (name, due date, status).
  - **Methods**:
    - `__init__(db, event_id, task_id=None)`: Sets up inputs and saves via `db.add_task()` or `db.update_task()`.
  - **Role**: Manages task creation/editing.

- `GuestDialog(QDialog)`:

  - **Purpose**: Collects guest details (name, contact, status).
  - **Methods**:
    - `__init__(db, event_id, guest_id=None)`: Sets up inputs and saves via `db.add_guest()` or `db.update_guest()`.
  - **Role**: Manages guest creation/editing.

**Key Code**:

```python
from PyQt5.QtWidgets import QDialog, QLineEdit, QDateEdit, QPushButton, QMessageBox

class SignupDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Signup")
        # Setup username, password, confirm password inputs
        self.signup_button.clicked.connect(self.accept)

    def accept(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        try:
            self.db.add_user(username, password)
            QMessageBox.information(self, "Success", "Account created")
            super().accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username already exists")
```

**Role**:

- Provides reusable dialogs for data entry, ensuring consistent UI and validation.

### 5. `delegates.py`

**Purpose**: Defines custom delegates for rendering and editing table cells in `MainWindow`.

**Key Class**:

- `EventDelegate(QStyledItemDelegate)`:
  - **Purpose**: Customizes display and editing of event table cells.
  - **Methods**:
    - `paint(painter, option, index)`: Renders cells with custom formatting (e.g., bold event names).
    - `createEditor(parent, option, index)`: Provides editors (e.g., `QDateEdit` for dates).
    - `setEditorData(editor, index)`: Populates editors with existing data.
    - `setModelData(editor, model, index)`: Saves edited data to the model.
  - **Role**: Enhances table usability with formatted display and inline editing.

**Key Code**:

```python
from PyQt5.QtWidgets import QStyledItemDelegate, QDateEdit

class EventDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        if index.column() == 2:  # Date column
            return QDateEdit(parent)
        return super().createEditor(parent, option, index)
```

**Role**:

- Improves the visual and interactive quality of the event table.

### 6. `__init__.py`

**Purpose**: Marks `event_planner` as a Python package, enabling imports like `from event_planner.app import LoginWindow`.

**Key Code**:

```python
# Empty file
```

**Role**:

- Facilitates modularization and clean imports.

## Code Explanation

The application’s code is organized to be modular, maintainable, and extensible. Below are key design choices and explanations:

### Modularity

- **Package Structure**: The `event_planner` package groups related modules, reducing namespace pollution and enabling `python -m event_planner.main`.
- **Separation of Concerns**:
  - `app.py`: UI and controller logic.
  - `database.py`: Data management.
  - `dialogs.py`: Input handling.
  - `delegates.py`: Table customization.
  - `main.py`: Application bootstrap.

### Security

- **Password Hashing**: `database.py` uses SHA-256 to hash passwords, ensuring secure storage.
- **SQL Injection Prevention**: Parameterized queries in `EventDatabase` prevent injection attacks.

### UI Design

- **PyQt5**: Chosen for cross-platform compatibility and rich widget set.
- **Dialogs**: Reusable `QDialog` subclasses streamline user input.
- **Delegates**: Custom `QStyledItemDelegate` enhances table interactivity.

### Database

- **SQLite**: Lightweight, serverless database suitable for a desktop app.
- **Schema**:
  - `users`: Stores username and hashed password.
  - `events`: Links events to users via `username`.
  - `tasks`/`guests`: Linked to events via `event_id`.
- **Atomic Operations**: `conn.commit()` ensures data integrity.

### Error Handling

- **Validation**: `SignupDialog` checks for password match and unique usernames.
- **Feedback**: `QMessageBox` provides user-friendly error messages.

### Extensibility

- **Export Feature**: `MainWindow.export_data()` is a placeholder for CSV/JSON export, easily extensible.
- **Custom Delegates**: `EventDelegate` can be extended for additional formatting.

## Deployment

### Running from Source

```bash
cd /event-planner-app
source bin/activate
./run.sh
```

### Building with PyInstaller

```bash
pyinstaller --name EventPlanner --onefile event_planner/main.py
```

- Output: `dist/EventPlanner` (Linux/macOS) or `dist/EventPlanner.exe` (Windows).
- Includes PyQt5 plugins and dependencies.

### Notes

- **Database Path**: `events.db` is created in the running directory. Ensure write permissions.
- **QStandardPaths Warning**: Suppressed by `run.sh` setting `XDG_RUNTIME_DIR=/run/user/1000`.

## Future Improvements

- **Export Functionality**: Complete CSV/JSON export for events, tasks, and guests.
- **Multi-User Support**: Add role-based access (e.g., admin, viewer).
- **Cloud Sync**: Integrate `requests` for syncing with a remote server.
- **Unit Tests**: Add tests for `EventDatabase` and UI interactions.
- **Styling**: Apply custom Qt stylesheets for a modern look.

## Conclusion

The Event Planner is a robust, user-friendly application with a clear architecture and modular codebase. Its SQLite backend ensures reliable data storage, while PyQt5 provides a responsive UI. Developers can extend it by adding features like export or cloud integration, leveraging the existing structure.
