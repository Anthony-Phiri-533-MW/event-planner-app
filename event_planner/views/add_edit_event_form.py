from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QHBoxLayout, QDateTimeEdit, QComboBox, QMessageBox
from PyQt6.QtCore import QDateTime
from controllers.event_controller import EventController
from controllers.category_controller import CategoryController
from controllers.event_type_controller import EventTypeController

class AddEditEventForm(QDialog):
    def __init__(self, date_str, event_data=None, on_save_callback=None):
        super().__init__()

        self.setWindowTitle("Add/Edit Event")
        self.resize(400, 500)

        self.date_str = date_str
        self.event_data = event_data  # If None => Add, Else => Edit
        self.on_save_callback = on_save_callback

        self.event_controller = EventController()
        self.category_controller = CategoryController()
        self.event_type_controller = EventTypeController()

        self.layout = QVBoxLayout(self)

        # Title
        self.title_input = QLineEdit()
        self.layout.addWidget(QLabel("Title:"))
        self.layout.addWidget(self.title_input)

        # Description
        self.description_input = QTextEdit()
        self.layout.addWidget(QLabel("Description:"))
        self.layout.addWidget(self.description_input)

        # Start Datetime
        self.start_datetime_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_datetime_input.setCalendarPopup(True)
        self.layout.addWidget(QLabel("Start Time:"))
        self.layout.addWidget(self.start_datetime_input)

        # End Datetime
        self.end_datetime_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_datetime_input.setCalendarPopup(True)
        self.layout.addWidget(QLabel("End Time:"))
        self.layout.addWidget(self.end_datetime_input)

        # Category Dropdown
        self.category_dropdown = QComboBox()
        self.layout.addWidget(QLabel("Category:"))
        self.layout.addWidget(self.category_dropdown)

        # Event Type Dropdown
        self.event_type_dropdown = QComboBox()
        self.layout.addWidget(QLabel("Event Type:"))
        self.layout.addWidget(self.event_type_dropdown)

        # Save/Cancel Buttons
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_event)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_layout)

        self.load_dropdowns()

        if self.event_data:
            self.load_event_data()

    def load_dropdowns(self):
        self.categories = self.category_controller.get_all_categories()
        self.category_dropdown.addItem("None", None)
        for cat in self.categories:
            self.category_dropdown.addItem(cat["name"], cat["id"])

        self.event_types = self.event_type_controller.get_all_event_types()
        self.event_type_dropdown.addItem("None", None)
        for etype in self.event_types:
            self.event_type_dropdown.addItem(etype["name"], etype["id"])

    def load_event_data(self):
        self.title_input.setText(self.event_data["title"])
        self.description_input.setPlainText(self.event_data["description"])
        self.start_datetime_input.setDateTime(QDateTime.fromString(self.event_data["start_datetime"], "yyyy-MM-dd HH:mm:ss"))
        self.end_datetime_input.setDateTime(QDateTime.fromString(self.event_data["end_datetime"], "yyyy-MM-dd HH:mm:ss"))

        if self.event_data["category_id"]:
            idx = self.category_dropdown.findData(self.event_data["category_id"])
            if idx != -1:
                self.category_dropdown.setCurrentIndex(idx)

        if self.event_data["event_type_id"]:
            idx = self.event_type_dropdown.findData(self.event_data["event_type_id"])
            if idx != -1:
                self.event_type_dropdown.setCurrentIndex(idx)

    def save_event(self):
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        start_datetime = self.start_datetime_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_datetime = self.end_datetime_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        category_id = self.category_dropdown.currentData()
        event_type_id = self.event_type_dropdown.currentData()

        if not title:
            QMessageBox.warning(self, "Validation Error", "Title is required!")
            return

        if self.event_data:
            # Edit existing event
            self.event_controller.update_event(
                self.event_data["id"], title, description, start_datetime, end_datetime, category_id, event_type_id
            )
        else:
            # Add new event
            self.event_controller.add_event(
                title, description, start_datetime, end_datetime, category_id, event_type_id
            )

        if self.on_save_callback:
            self.on_save_callback()
        self.accept()
