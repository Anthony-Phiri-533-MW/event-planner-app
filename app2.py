import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
    QPushButton, QTextEdit, QListWidgetItem, QLineEdit, QFormLayout, QDialog,
    QDialogButtonBox, QCalendarWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QTextCharFormat, QColor
import sys

# SQLite database helper
class EventDatabase:
    def __init__(self, db_name="events.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    date TEXT,
                    venue TEXT,
                    description TEXT
                )
            ''')

    def add_event(self, name, date, venue, description):
        with self.conn:
            self.conn.execute('''
                INSERT INTO events (name, date, venue, description)
                VALUES (?, ?, ?, ?)
            ''', (name, date, venue, description))

    def get_all_events(self):
        with self.conn:
            return self.conn.execute('SELECT * FROM events').fetchall()

    def search_events(self, query):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM events WHERE name LIKE ? OR venue LIKE ?
            ''', (f'%{query}%', f'%{query}%')).fetchall()

    def get_events_by_date(self, date):
        with self.conn:
            return self.conn.execute('SELECT * FROM events WHERE date = ?', (date,)).fetchall()

class EventDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Event")
        self.layout = QFormLayout(self)

        self.name_input = QLineEdit(self)
        self.date_input = QLineEdit(self)
        self.venue_input = QLineEdit(self)
        self.desc_input = QTextEdit(self)

        self.layout.addRow("Event Name:", self.name_input)
        self.layout.addRow("Date (YYYY-MM-DD):", self.date_input)
        self.layout.addRow("Venue:", self.venue_input)
        self.layout.addRow("Description:", self.desc_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "date": self.date_input.text(),
            "venue": self.venue_input.text(),
            "description": self.desc_input.toPlainText()
        }

class EventPlannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Planner")
        self.db = EventDatabase()

        main_layout = QHBoxLayout(self)

        self.sidebar = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search events...")
        self.search_input.textChanged.connect(self.search_events)

        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.calendar_date_selected)

        self.add_event_btn = QPushButton("Add Event")
        self.add_event_btn.clicked.connect(self.add_event)

        self.sidebar.addWidget(self.search_input)
        self.sidebar.addWidget(self.calendar)
        self.sidebar.addWidget(self.add_event_btn)

        self.event_list = QListWidget()
        self.details_panel = QTextEdit()
        self.details_panel.setReadOnly(True)

        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Events"))
        right_panel.addWidget(self.event_list)
        right_panel.addWidget(QLabel("Details"))
        right_panel.addWidget(self.details_panel)

        main_layout.addLayout(self.sidebar)
        main_layout.addLayout(right_panel)

        self.event_list.itemClicked.connect(self.display_event_details)
        self.load_events()

    def add_event(self):
        dialog = EventDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            event = dialog.get_data()
            self.db.add_event(event['name'], event['date'], event['venue'], event['description'])
            self.load_events()

    def load_events(self):
        self.event_list.clear()
        # Clear all existing date highlights
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Highlight dates with events
        event_dates = set()
        for event in self.db.get_all_events():
            date = QDate.fromString(event[2], "yyyy-MM-dd")
            event_dates.add(date)
            
            # Add to event list
            item = QListWidgetItem(f"{event[1]} - {event[2]}")
            item.setData(Qt.UserRole, event)
            self.event_list.addItem(item)
        
        # Apply highlight formatting
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("lightgreen"))
        for date in event_dates:
            self.calendar.setDateTextFormat(date, highlight_format)


    def display_event_details(self, item):
        event = item.data(Qt.UserRole)
        details = f"Name: {event[1]}\nDate: {event[2]}\nVenue: {event[3]}\n\n{event[4]}"
        self.details_panel.setPlainText(details)

    def search_events(self, text):
        self.event_list.clear()
        events = self.db.search_events(text) if text else self.db.get_all_events()
        for event in events:
            item = QListWidgetItem(f"{event[1]} - {event[2]}")
            item.setData(Qt.UserRole, event)
            self.event_list.addItem(item)

    def calendar_date_selected(self):
        date_str = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.event_list.clear()
        events = self.db.get_events_by_date(date_str)
        for event in events:
            item = QListWidgetItem(f"{event[1]} - {event[2]}")
            item.setData(Qt.UserRole, event)
            self.event_list.addItem(item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EventPlannerApp()
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec_())
