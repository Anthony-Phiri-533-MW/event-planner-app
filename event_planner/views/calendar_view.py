from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCalendarWidget
from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6.QtCore import Qt, QDate

from controllers.calendar_controller import CalendarController
from controllers.event_controller import EventController

class CalendarView(QWidget):
    def __init__(self, navigate_to_events_callback):
        super().__init__()

        self.calendar_controller = CalendarController()
        self.event_controller = EventController()
        self.navigate_to_events_callback = navigate_to_events_callback  # function from main window

        self.layout = QVBoxLayout(self)

        self.title = QLabel("Calendar")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_clicked)

        self.layout.addWidget(self.calendar)

        self.highlight_event_days()

    def highlight_event_days(self):
        event_dates = self.calendar_controller.get_event_dates()

        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#BE87D5"))  # Accent color
        highlight_format.setForeground(QColor("#FFFFFF"))

        for date_str in event_dates:
            year, month, day = map(int, date_str.split('-'))
            qdate = QDate(year, month, day)
            self.calendar.setDateTextFormat(qdate, highlight_format)

    def on_date_clicked(self, qdate: QDate):
        selected_date = qdate.toString("yyyy-MM-dd")
        print(f"Clicked date: {selected_date}")
        self.navigate_to_events_callback(selected_date)  # Move to Events View for that date
