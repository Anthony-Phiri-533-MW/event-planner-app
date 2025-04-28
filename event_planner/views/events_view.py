from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QHBoxLayout
from controllers.event_controller import EventController
from views.add_edit_event_form import AddEditEventForm

class EventsView(QWidget):
    def __init__(self, date_str: str, navigate_back_callback):
        super().__init__()

        self.date_str = date_str
        self.navigate_back_callback = navigate_back_callback

        self.event_controller = EventController()

        self.layout = QVBoxLayout(self)

        self.header = QLabel(f"Events on {self.date_str}")
        self.header.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        self.layout.addWidget(self.header)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.button_layout = QHBoxLayout()

        self.back_button = QPushButton("Back to Calendar")
        self.back_button.clicked.connect(self.navigate_back)
        self.button_layout.addWidget(self.back_button)

        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.clicked.connect(self.add_event)
        self.button_layout.addWidget(self.add_event_button)

        self.layout.addLayout(self.button_layout)

        self.load_events()

    def load_events(self):
        self.list_widget.clear()
        events = self.event_controller.get_events_by_date(self.date_str)
        if not events:
            item = QListWidgetItem("No events on this day.")
            self.list_widget.addItem(item)
            self.list_widget.setEnabled(False)
        else:
            self.list_widget.setEnabled(True)
            for event in events:
                item_text = f"{event['title']} ({event['start_datetime'].split(' ')[1]} - {event['end_datetime'].split(' ')[1]})"
                item = QListWidgetItem(item_text)
                item.setData(1000, event)  # Store event data inside
                self.list_widget.addItem(item)

            self.list_widget.itemDoubleClicked.connect(self.show_event_actions)

    def navigate_back(self):
        self.navigate_back_callback()

    def add_event(self):
        dialog = AddEditEventForm(self.date_str, on_save_callback=self.load_events)
        dialog.exec()

    def show_event_actions(self, item: QListWidgetItem):
        event = item.data(1000)
        choice = QMessageBox.question(self, "Event Actions",
            f"Event: {event['title']}\n\nWhat would you like to do?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        if choice == QMessageBox.StandardButton.Yes:
            self.edit_event(event)
        elif choice == QMessageBox.StandardButton.No:
            self.delete_event(event)

    def edit_event(self, event):
        dialog = AddEditEventForm(self.date_str, event_data=event, on_save_callback=self.load_events)
        dialog.exec()

    def delete_event(self, event):
        confirm = QMessageBox.question(self, "Delete Event",
            f"Are you sure you want to delete '{event['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.event_controller.delete_event(event["id"])
            QMessageBox.information(self, "Deleted", f"'{event['title']}' has been deleted.")
            self.load_events()
