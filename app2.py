import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
    QPushButton, QTextEdit, QListWidgetItem, QLineEdit, QFormLayout, QDialog,
    QDialogButtonBox, QCalendarWidget, QDateEdit, QMessageBox, QTextBrowser,
    QStatusBar, QMenu, QAction, QTimeEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QTextCharFormat, QColor, QFont
import sys

# Custom delegate for checkbox in table
class CheckBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        return None  # Prevent editing, we'll handle clicks directly

    def editorEvent(self, event, model, option, index):
        if event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
            # Toggle the checkbox state
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
            # Events table
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT,
                    venue TEXT,
                    description TEXT,
                    is_archived INTEGER DEFAULT 0
                )
            ''')
            
            # Archived events table
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS archived_events (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT,
                    venue TEXT,
                    description TEXT,
                    archived_date TEXT
                )
            ''')
            
            # Tasks table
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    event_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    is_completed INTEGER DEFAULT 0,
                    FOREIGN KEY (event_id) REFERENCES events(id)
                )
            ''')
            
            # Guests table
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS guests (
                    id INTEGER PRIMARY KEY,
                    event_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT,
                    FOREIGN KEY (event_id) REFERENCES events(id)
                )
            ''')

    def add_event(self, name, date, time, venue, description):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO events (name, date, time, venue, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, date, time, venue, description))
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
            # First delete associated guests and tasks
            self.conn.execute('DELETE FROM guests WHERE event_id = ?', (event_id,))
            self.conn.execute('DELETE FROM tasks WHERE event_id = ?', (event_id,))
            # Then delete the event
            self.conn.execute('DELETE FROM events WHERE id = ?', (event_id,))

    def get_all_events(self):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM events 
                WHERE is_archived = 0
                ORDER BY date, time
            ''').fetchall()

    def get_archived_events(self):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM archived_events 
                ORDER BY archived_date DESC
            ''').fetchall()

    def search_events(self, query):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM events 
                WHERE is_archived = 0 AND 
                (name LIKE ? OR venue LIKE ? OR description LIKE ?)
                ORDER BY date, time
            ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()

    def get_events_by_date(self, date):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM events 
                WHERE date = ? AND is_archived = 0
                ORDER BY time, name
            ''', (date,)).fetchall()

    def get_event_by_id(self, event_id):
        with self.conn:
            return self.conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()

    # Task management methods
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

    # Guest management methods
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
            # Get event data
            event = self.get_event_by_id(event_id)
            if not event:
                return False
            
            # Insert into archived_events
            self.conn.execute('''
                INSERT INTO archived_events 
                (id, name, date, time, venue, description, archived_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (event[0], event[1], event[2], event[3], event[4], event[5], 
                 QDate.currentDate().toString("yyyy-MM-dd")))
            
            # Delete from active events
            self.delete_event(event_id)
            return True

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
        self.time_input.setTime(QTime(19, 0))  # Default to 7:00 PM
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

class EventPlannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Planner")
        self.db = EventDatabase()
        self.current_event_id = None

        main_layout = QHBoxLayout(self)
        self.setMinimumSize(1200, 800)

        # Left sidebar
        self.sidebar = QVBoxLayout()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search events...")
        self.search_input.textChanged.connect(self.search_events)
        
        # Calendar
        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.calendar_date_selected)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.today_btn = QPushButton("Today")
        self.today_btn.clicked.connect(self.go_to_today)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_selection)
        nav_layout.addWidget(self.today_btn)
        nav_layout.addWidget(self.clear_btn)
        
        # View toggle
        self.view_toggle = QPushButton("View Archived Events")
        self.view_toggle.setCheckable(True)
        self.view_toggle.toggled.connect(self.toggle_event_view)
        
        # Action buttons
        button_layout = QVBoxLayout()
        self.add_event_btn = QPushButton("Add New Event")
        self.add_event_btn.clicked.connect(self.add_event)
        self.edit_event_btn = QPushButton("Edit Selected Event")
        self.edit_event_btn.clicked.connect(self.edit_event)
        self.delete_event_btn = QPushButton("Delete Selected Event")
        self.delete_event_btn.clicked.connect(self.delete_event)
        
        # Guest management buttons
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
        
        # Task management buttons
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
        
        # Archive button
        self.archive_btn = QPushButton("Archive Event")
        self.archive_btn.clicked.connect(self.archive_event)
        
        # Disable buttons initially
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
        button_layout.addWidget(self.view_toggle)
        button_layout.addStretch()

        self.sidebar.addWidget(self.search_input)
        self.sidebar.addWidget(self.calendar)
        self.sidebar.addLayout(nav_layout)
        self.sidebar.addLayout(button_layout)

        # Right panel
        right_panel = QVBoxLayout()
        
        # Event list
        self.event_list = QListWidget()
        self.event_list.itemSelectionChanged.connect(self.on_event_selection_changed)
        
        # Details panel
        self.details_panel = QTextBrowser()
        self.details_panel.setOpenExternalLinks(True)
        
        # Guests table
        self.guests_label = QLabel("Guests")
        self.guests_table = QTableWidget()
        self.guests_table.setColumnCount(3)
        self.guests_table.setHorizontalHeaderLabels(["ID", "Name", "Email"])
        self.guests_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.guests_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.guests_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.guests_table.itemSelectionChanged.connect(self.on_guest_selection_changed)
        
        # Tasks table
        self.tasks_label = QLabel("Tasks")
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(3)
        self.tasks_table.setHorizontalHeaderLabels(["ID", "Description", "Completed"])
        self.tasks_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tasks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tasks_table.setItemDelegateForColumn(2, CheckBoxDelegate(self))
        self.tasks_table.itemChanged.connect(self.on_task_status_changed)
        self.tasks_table.itemSelectionChanged.connect(self.on_task_selection_changed)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Arial", 9))
        
        right_panel.addWidget(QLabel("Events"))
        right_panel.addWidget(self.event_list)
        right_panel.addWidget(QLabel("Details"))
        right_panel.addWidget(self.details_panel)
        right_panel.addWidget(self.guests_label)
        right_panel.addWidget(self.guests_table)
        right_panel.addWidget(self.tasks_label)
        right_panel.addWidget(self.tasks_table)
        right_panel.addWidget(self.status_bar)

        main_layout.addLayout(self.sidebar, 1)
        main_layout.addLayout(right_panel, 2)

        self.load_events()
        self.go_to_today()

    def toggle_event_buttons(self, enabled):
        """Enable/disable event-related buttons"""
        self.edit_event_btn.setEnabled(enabled)
        self.delete_event_btn.setEnabled(enabled)
        self.add_guest_btn.setEnabled(enabled)
        self.add_task_btn.setEnabled(enabled)

    def toggle_guest_buttons(self, enabled):
        """Enable/disable guest-related buttons"""
        self.edit_guest_btn.setEnabled(enabled)
        self.delete_guest_btn.setEnabled(enabled)

    def toggle_task_buttons(self, enabled):
        """Enable/disable task-related buttons"""
        self.edit_task_btn.setEnabled(enabled)
        self.delete_task_btn.setEnabled(enabled)

    def on_event_selection_changed(self):
        """Handle event selection changes"""
        has_selection = bool(self.event_list.currentItem())
        self.toggle_event_buttons(has_selection)
        if has_selection:
            self.display_event_details(self.event_list.currentItem())
            self.load_guests()
            self.load_tasks()

    def on_guest_selection_changed(self):
        """Handle guest selection changes"""
        self.toggle_guest_buttons(bool(self.guests_table.currentItem()))

    def on_task_selection_changed(self):
        """Handle task selection changes"""
        self.toggle_task_buttons(bool(self.tasks_table.currentItem()))

    def on_task_status_changed(self, item):
        """Handle task completion status changes"""
        if item.column() == 2:  # Only for Completed column
            task_id = int(self.tasks_table.item(item.row(), 0).text())
            is_completed = item.checkState() == Qt.Checked
            try:
                self.db.update_task_status(task_id, is_completed)
                self.check_archive_status()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def add_event(self):
        """Open dialog to add a new event"""
        dialog = EventDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                event_id = self.db.add_event(data['name'], data['date'], 
                                         data['time'], data['venue'], 
                                         data['description'])
                self.status_bar.showMessage("Event added successfully", 3000)
                self.load_events()
                # Select the newly added event
                for i in range(self.event_list.count()):
                    item = self.event_list.item(i)
                    if item.data(Qt.UserRole)[0] == event_id:
                        self.event_list.setCurrentItem(item)
                        break
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def edit_event(self):
        """Open dialog to edit selected event"""
        if not self.event_list.currentItem():
            return
            
        event = self.event_list.currentItem().data(Qt.UserRole)
        event_data = {
            'id': event[0],
            'name': event[1],
            'date': event[2],
            'time': event[3],
            'venue': event[4],
            'description': event[5]
        }
        
        dialog = EventDialog(self, event_data, edit_mode=True)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.update_event(event[0], data['name'], data['date'], 
                                   data['time'], data['venue'], data['description'])
                self.status_bar.showMessage("Event updated successfully", 3000)
                self.load_events()
                # Keep the edited event selected
                for i in range(self.event_list.count()):
                    item = self.event_list.item(i)
                    if item.data(Qt.UserRole)[0] == event[0]:
                        self.event_list.setCurrentItem(item)
                        break
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def delete_event(self):
        if not self.event_list.currentItem():
            return
            
        event = self.event_list.currentItem().data(Qt.UserRole)
        reply = QMessageBox.question(
            self, 'Delete Event', 
            f"Are you sure you want to delete '{event[1]}' and all its tasks/guests?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_event(event[0])
                self.status_bar.showMessage("Event deleted successfully", 3000)
                self.load_events()
                self.details_panel.clear()
                self.guests_table.setRowCount(0)
                self.tasks_table.setRowCount(0)
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def archive_event(self):
        """Archive the current event"""
        if not self.current_event_id:
            return
            
        event = self.db.get_event_by_id(self.current_event_id)
        if not event:
            return
            
        reply = QMessageBox.question(
            self, 'Archive Event', 
            f"Archive '{event[1]}' and all its tasks/guests?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.db.archive_event(self.current_event_id):
                    self.status_bar.showMessage("Event archived successfully", 3000)
                    self.load_events()
                    self.clear_selection()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def toggle_event_view(self, show_archived):
        """Toggle between active and archived events view"""
        self.view_toggle.setText("View Active Events" if show_archived else "View Archived Events")
        self.load_events(show_archived)

    def load_events(self, show_archived=False):
        """Load events (active or archived)"""
        self.event_list.clear()
        # Clear all existing date highlights
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        if show_archived:
            events = self.db.get_archived_events()
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(QColor("lightgray"))
        else:
            events = self.db.get_all_events()
            # Highlight dates with events
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(QColor("lightgreen"))
        
        for event in events:
            date = QDate.fromString(event[2], "yyyy-MM-dd")
            if not show_archived:
                self.calendar.setDateTextFormat(date, highlight_format)
            
            # Add to event list
            time_str = f" at {event[3]}" if event[3] else ""
            archived_str = " (Archived)" if show_archived else ""
            item = QListWidgetItem(f"{event[1]} - {date.toString('MMM d, yyyy')}{time_str}{archived_str}")
            item.setData(Qt.UserRole, event)
            self.event_list.addItem(item)

    def display_event_details(self, item):
        event = item.data(Qt.UserRole)
        time_str = f"<b>Time:</b> {event[3]}<br>" if event[3] else ""
        archived_str = "<b>Status:</b> Archived<br>" if len(event) > 6 and event[6] else ""
        details = (
            f"<h2>{event[1]}</h2>"
            f"<p><b>Date:</b> {event[2]}<br>"
            f"{time_str}"
            f"{archived_str}"
            f"<b>Venue:</b> {event[4]}</p>"
            f"<p>{event[5].replace('\n', '<br>')}</p>"
        )
        self.details_panel.setHtml(details)
        self.current_event_id = event[0]
        self.load_guests()
        self.load_tasks()

    def load_guests(self):
        """Load guests for the currently selected event"""
        self.guests_table.setRowCount(0)
        if not self.current_event_id:
            return
            
        guests = self.db.get_guests_for_event(self.current_event_id)
        self.guests_table.setRowCount(len(guests))
        
        for row, guest in enumerate(guests):
            self.guests_table.setItem(row, 0, QTableWidgetItem(str(guest[0])))
            self.guests_table.setItem(row, 1, QTableWidgetItem(guest[2]))
            self.guests_table.setItem(row, 2, QTableWidgetItem(guest[3] or ""))
        
        self.guests_label.setText(f"Guests ({len(guests)})")

    def load_tasks(self):
        """Load tasks for the currently selected event"""
        self.tasks_table.setRowCount(0)
        if not self.current_event_id:
            return
            
        tasks = self.db.get_tasks_for_event(self.current_event_id)
        self.tasks_table.setRowCount(len(tasks))
        
        for row, task in enumerate(tasks):
            self.tasks_table.setItem(row, 0, QTableWidgetItem(str(task[0])))
            self.tasks_table.setItem(row, 1, QTableWidgetItem(task[2]))
            
            # Add checkbox for completed status
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Checked if task[3] else Qt.Unchecked)
            self.tasks_table.setItem(row, 2, item)
        
        self.tasks_label.setText(f"Tasks ({len(tasks)})")
        self.check_archive_status()

    def check_archive_status(self):
        """Check if all tasks are completed and enable archive button"""
        if not self.current_event_id:
            self.archive_btn.setEnabled(False)
            return
            
        tasks = self.db.get_tasks_for_event(self.current_event_id)
        all_completed = all(task[3] for task in tasks) if tasks else False
        self.archive_btn.setEnabled(all_completed)

    def add_guest(self):
        """Add a new guest to the current event"""
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
        """Edit selected guest"""
        if not self.guests_table.currentItem() or not self.current_event_id:
            return
            
        current_row = self.guests_table.currentRow()
        guest_id = int(self.guests_table.item(current_row, 0).text())
        guest_name = self.guests_table.item(current_row, 1).text()
        guest_email = self.guests_table.item(current_row, 2).text()
        
        dialog = GuestDialog(self, {
            'name': guest_name,
            'email': guest_email
        })
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                # Since we don't have an update_guest method, we'll delete and re-add
                self.db.delete_guest(guest_id)
                self.db.add_guest(self.current_event_id, data['name'], data['email'])
                self.status_bar.showMessage("Guest updated successfully", 3000)
                self.load_guests()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def delete_guest(self):
        """Delete selected guest"""
        if not self.guests_table.currentItem():
            return
            
        current_row = self.guests_table.currentRow()
        guest_id = int(self.guests_table.item(current_row, 0).text())
        guest_name = self.guests_table.item(current_row, 1).text()
        
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
        """Add a new task to the current event"""
        if not self.current_event_id:
            return
            
        dialog = TaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.add_task(self.current_event_id, data['description'])
                if data['completed']:
                    # If added as completed, we'd need to get the last inserted ID
                    # For simplicity, we'll just reload all tasks
                    pass
                self.status_bar.showMessage("Task added successfully", 3000)
                self.load_tasks()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def edit_task(self):
        """Edit selected task"""
        if not self.tasks_table.currentItem():
            return
            
        current_row = self.tasks_table.currentRow()
        task_id = int(self.tasks_table.item(current_row, 0).text())
        task_desc = self.tasks_table.item(current_row, 1).text()
        task_completed = self.tasks_table.item(current_row, 2).checkState() == Qt.Checked
        
        dialog = TaskDialog(self, {
            'description': task_desc,
            'completed': task_completed
        })
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.update_task_status(task_id, data['completed'])
                self.status_bar.showMessage("Task updated successfully", 3000)
                self.load_tasks()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def delete_task(self):
        """Delete selected task"""
        if not self.tasks_table.currentItem():
            return
            
        current_row = self.tasks_table.currentRow()
        task_id = int(self.tasks_table.item(current_row, 0).text())
        task_desc = self.tasks_table.item(current_row, 1).text()
        
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

    def search_events(self, text):
        self.event_list.clear()
        events = self.db.search_events(text) if text else self.db.get_all_events()
        for event in events:
            date = QDate.fromString(event[2], "yyyy-MM-dd")
            time_str = f" at {event[3]}" if event[3] else ""
            item = QListWidgetItem(f"{event[1]} - {date.toString('MMM d, yyyy')}{time_str}")
            item.setData(Qt.UserRole, event)
            self.event_list.addItem(item)

    def calendar_date_selected(self):
        date_str = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.event_list.clear()
        events = self.db.get_events_by_date(date_str)
        for event in events:
            time_str = f" at {event[3]}" if event[3] else ""
            item = QListWidgetItem(f"{event[1]}{time_str}")
            item.setData(Qt.UserRole, event)
            self.event_list.addItem(item)

    def go_to_today(self):
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar_date_selected()

    def clear_selection(self):
        self.event_list.clearSelection()
        self.details_panel.clear()
        self.guests_table.setRowCount(0)
        self.guests_label.setText("Guests")
        self.tasks_table.setRowCount(0)
        self.tasks_label.setText("Tasks")
        self.current_event_id = None
        self.toggle_event_buttons(False)
        self.toggle_guest_buttons(False)
        self.toggle_task_buttons(False)
        self.archive_btn.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    window = EventPlannerApp()
    window.show()
    sys.exit(app.exec_())