import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
    QPushButton, QTextEdit, QListWidgetItem, QLineEdit, QFormLayout, QDialog,
    QDialogButtonBox, QCalendarWidget, QDateEdit, QMessageBox, QTextBrowser,
    QStatusBar, QMenu, QAction
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QTextCharFormat, QColor, QFont
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
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO events (name, date, venue, description)
                VALUES (?, ?, ?, ?)
            ''', (name, date, venue, description))
            return cursor.lastrowid

    def update_event(self, event_id, name, date, venue, description):
        with self.conn:
            self.conn.execute('''
                UPDATE events 
                SET name = ?, date = ?, venue = ?, description = ?
                WHERE id = ?
            ''', (name, date, venue, description, event_id))

    def delete_event(self, event_id):
        with self.conn:
            self.conn.execute('DELETE FROM events WHERE id = ?', (event_id,))

    def get_all_events(self):
        with self.conn:
            return self.conn.execute('SELECT * FROM events ORDER BY date').fetchall()

    def search_events(self, query):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM events 
                WHERE name LIKE ? OR venue LIKE ? OR description LIKE ?
                ORDER BY date
            ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()

    def get_events_by_date(self, date):
        with self.conn:
            return self.conn.execute('''
                SELECT * FROM events 
                WHERE date = ? 
                ORDER BY name
            ''', (date,)).fetchall()

    def get_event_by_id(self, event_id):
        with self.conn:
            return self.conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()

class EventDialog(QDialog):
    def __init__(self, parent=None, event_data=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Event" if not event_data else "Edit Event")
        self.layout = QFormLayout(self)

        self.name_input = QLineEdit(self)
        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.venue_input = QLineEdit(self)
        self.desc_input = QTextEdit(self)

        if event_data:
            self.name_input.setText(event_data['name'])
            self.date_input.setDate(QDate.fromString(event_data['date'], "yyyy-MM-dd"))
            self.venue_input.setText(event_data['venue'])
            self.desc_input.setPlainText(event_data['description'])

        self.layout.addRow("Event Name:", self.name_input)
        self.layout.addRow("Date:", self.date_input)
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
        self.setMinimumSize(1000, 700)

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
        self.add_event_btn = QPushButton("Add Event")
        self.add_event_btn.clicked.connect(lambda: self.add_edit_event())
        self.delete_event_btn = QPushButton("Delete Event")
        self.delete_event_btn.clicked.connect(self.delete_event)
        self.delete_event_btn.setEnabled(False)

        self.sidebar.addWidget(self.search_input)
        self.sidebar.addWidget(self.calendar)
        self.sidebar.addLayout(nav_layout)
        self.sidebar.addWidget(self.add_event_btn)
        self.sidebar.addWidget(self.delete_event_btn)
        self.sidebar.addStretch()

        # Right panel
        right_panel = QVBoxLayout()
        
        # Event list
        self.event_list = QListWidget()
        self.event_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.event_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Details panel
        self.details_panel = QTextBrowser()
        self.details_panel.setOpenExternalLinks(True)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Arial", 9))
        
        right_panel.addWidget(QLabel("Events"))
        right_panel.addWidget(self.event_list)
        right_panel.addWidget(QLabel("Details"))
        right_panel.addWidget(self.details_panel)
        right_panel.addWidget(self.status_bar)

        main_layout.addLayout(self.sidebar, 1)
        main_layout.addLayout(right_panel, 2)

        self.event_list.itemClicked.connect(self.display_event_details)
        self.load_events()
        self.go_to_today()

    def show_context_menu(self, position):
        if not self.event_list.itemAt(position):
            return
            
        menu = QMenu()
        edit_action = QAction("Edit Event", self)
        edit_action.triggered.connect(self.edit_selected_event)
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete Event", self)
        delete_action.triggered.connect(self.delete_event)
        menu.addAction(delete_action)
        
        menu.exec_(self.event_list.mapToGlobal(position))

    def add_edit_event(self, event_data=None):
        dialog = EventDialog(self, event_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                if event_data and 'id' in event_data:
                    self.db.update_event(event_data['id'], data['name'], data['date'], 
                                         data['venue'], data['description'])
                    self.status_bar.showMessage("Event updated successfully", 3000)
                else:
                    self.db.add_event(data['name'], data['date'], 
                                    data['venue'], data['description'])
                    self.status_bar.showMessage("Event added successfully", 3000)
                self.load_events()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def edit_selected_event(self):
        if not self.event_list.currentItem():
            return
            
        event = self.event_list.currentItem().data(Qt.UserRole)
        event_data = {
            'id': event[0],
            'name': event[1],
            'date': event[2],
            'venue': event[3],
            'description': event[4]
        }
        self.add_edit_event(event_data)

    def delete_event(self):
        if not self.event_list.currentItem():
            return
            
        event = self.event_list.currentItem().data(Qt.UserRole)
        reply = QMessageBox.question(
            self, 'Delete Event', 
            f"Are you sure you want to delete '{event[1]}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_event(event[0])
                self.status_bar.showMessage("Event deleted successfully", 3000)
                self.load_events()
                self.details_panel.clear()
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
            item = QListWidgetItem(f"{event[1]} - {date.toString('MMM d, yyyy')}")
            item.setData(Qt.UserRole, event)
            self.event_list.addItem(item)

    def display_event_details(self, item):
        event = item.data(Qt.UserRole)
        details = (
            f"<h2>{event[1]}</h2>"
            f"<p><b>Date:</b> {event[2]}<br>"
            f"<b>Venue:</b> {event[3]}</p>"
            f"<p>{event[4].replace('\n', '<br>')}</p>"
        )
        self.details_panel.setHtml(details)
        self.delete_event_btn.setEnabled(True)

    def search_events(self, text):
        self.event_list.clear()
        events = self.db.search_events(text) if text else self.db.get_all_events()
        for event in events:
            date = QDate.fromString(event[2], "yyyy-MM-dd")
            item = QListWidgetItem(f"{event[1]} - {date.toString('MMM d, yyyy')}")
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

    def go_to_today(self):
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar_date_selected()

    def clear_selection(self):
        self.event_list.clearSelection()
        self.details_panel.clear()
        self.delete_event_btn.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    window = EventPlannerApp()
    window.show()
    sys.exit(app.exec_())