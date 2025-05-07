import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
    QPushButton, QTextEdit, QListWidgetItem, QLineEdit, QFormLayout, QDialog,
    QDialogButtonBox, QCalendarWidget, QDateEdit, QMessageBox, QTextBrowser,
    QStatusBar, QMenu, QAction, QTimeEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QInputDialog
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QTextCharFormat, QColor, QFont
import sys

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
                    description TEXT
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
            # First delete guests associated with the event
            self.conn.execute('DELETE FROM guests WHERE event_id = ?', (event_id,))
            # Then delete the event
            self.conn.execute('DELETE FROM events WHERE id = ?', (event_id,))

    def get_all_events(self):
        with self.conn:
            return self.conn.execute('SELECT * FROM events ORDER BY date, time').fetchall()

    def search_events(self, query):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM events 
                WHERE name LIKE ? OR venue LIKE ? OR description LIKE ?
                ORDER BY date, time
            ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()

    def get_events_by_date(self, date):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM events 
                WHERE date = ? 
                ORDER BY time, name
            ''', (date,)).fetchall()

    def get_event_by_id(self, event_id):
        with self.conn:
            return self.conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()

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

        # Event fields
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
        
        # Disable buttons initially
        self.toggle_event_buttons(False)
        self.toggle_guest_buttons(False)
        
        button_layout.addWidget(self.add_event_btn)
        button_layout.addWidget(self.edit_event_btn)
        button_layout.addWidget(self.delete_event_btn)
        button_layout.addLayout(self.guest_buttons_layout)
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
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Arial", 9))
        
        right_panel.addWidget(QLabel("Events"))
        right_panel.addWidget(self.event_list)
        right_panel.addWidget(QLabel("Details"))
        right_panel.addWidget(self.details_panel)
        right_panel.addWidget(self.guests_label)
        right_panel.addWidget(self.guests_table)
        right_panel.addWidget(self.status_bar)

        main_layout.addLayout(self.sidebar, 1)
        main_layout.addLayout(right_panel, 2)

        self.event_list.itemClicked.connect(self.display_event_details)
        self.load_events()
        self.go_to_today()

    def toggle_event_buttons(self, enabled):
        """Enable/disable event-related buttons"""
        self.edit_event_btn.setEnabled(enabled)
        self.delete_event_btn.setEnabled(enabled)
        self.add_guest_btn.setEnabled(enabled)

    def toggle_guest_buttons(self, enabled):
        """Enable/disable guest-related buttons"""
        self.edit_guest_btn.setEnabled(enabled)
        self.delete_guest_btn.setEnabled(enabled)

    def on_event_selection_changed(self):
        """Handle event selection changes"""
        has_selection = bool(self.event_list.currentItem())
        self.toggle_event_buttons(has_selection)
        if has_selection:
            self.display_event_details(self.event_list.currentItem())
            self.load_guests()

    def on_guest_selection_changed(self):
        """Handle guest selection changes"""
        self.toggle_guest_buttons(bool(self.guests_table.currentItem()))

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
            f"Are you sure you want to delete '{event[1]}' and all its guests?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_event(event[0])
                self.status_bar.showMessage("Event deleted successfully", 3000)
                self.load_events()
                self.details_panel.clear()
                self.guests_table.setRowCount(0)
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def load_events(self):
        self.event_list.clear()
        # Clear all existing date highlights
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Highlight dates with events
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("lightgreen"))
        
        for event in self.db.get_all_events():
            date = QDate.fromString(event[2], "yyyy-MM-dd")
            self.calendar.setDateTextFormat(date, highlight_format)
            
            # Add to event list
            time_str = f" at {event[3]}" if event[3] else ""
            item = QListWidgetItem(f"{event[1]} - {date.toString('MMM d, yyyy')}{time_str}")
            item.setData(Qt.UserRole, event)
            self.event_list.addItem(item)

    def display_event_details(self, item):
        event = item.data(Qt.UserRole)
        time_str = f"<b>Time:</b> {event[3]}<br>" if event[3] else ""
        details = (
            f"<h2>{event[1]}</h2>"
            f"<p><b>Date:</b> {event[2]}<br>"
            f"{time_str}"
            f"<b>Venue:</b> {event[4]}</p>"
            f"<p>{event[5].replace('\n', '<br>')}</p>"
        )
        self.details_panel.setHtml(details)
        self.current_event_id = event[0]
        self.load_guests()

    def load_guests(self):
        """Load guests for the currently selected event"""
        if not self.current_event_id:
            return
        
        guests = self.db.get_guests_for_event(self.current_event_id)
        self.guests_table.setRowCount(len(guests))
    
        for row, guest in enumerate(guests):
            self.guests_table.setItem(row, 0, QTableWidgetItem(str(guest[0])))
            self.guests_table.setItem(row, 1, QTableWidgetItem(guest[2]))
            self.guests_table.setItem(row, 2, QTableWidgetItem(guest[3] or ""))
        
        self.guests_label.setText(f"Guests ({len(guests)})")

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
        self.current_event_id = None
        self.toggle_event_buttons(False)
        self.toggle_guest_buttons(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    window = EventPlannerApp()
    window.show()
    sys.exit(app.exec_())