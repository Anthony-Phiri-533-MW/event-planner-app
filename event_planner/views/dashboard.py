from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        welcome_label = QLabel("Welcome to Event Planner Dashboard")
        layout.addWidget(welcome_label)

        self.setLayout(layout)
