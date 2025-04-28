import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from views.calendar_view import CalendarView
from views.events_view import EventsView

from core.theme_manager import ThemeManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Planner")
        self.resize(1200, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Calendar screen
        self.calendar_view = CalendarView(self.navigate_to_events)
        self.stack.addWidget(self.calendar_view)

        # Placeholder for events screen (created later when needed)
        self.events_view = None

        self.theme_manager = ThemeManager()
        self.theme_manager.set_theme("Light")   # Set default theme
        self.theme_manager.apply_theme(self)    # Apply theme to MainWindow (self)

        # apply_theme(self, theme_name="light")  # Default theme

    def navigate_to_events(self, selected_date: str):
        self.events_view = EventsView(selected_date, self.navigate_back_to_calendar)
        self.stack.addWidget(self.events_view)
        self.stack.setCurrentWidget(self.events_view)

    def navigate_back_to_calendar(self):
        self.stack.setCurrentWidget(self.calendar_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
