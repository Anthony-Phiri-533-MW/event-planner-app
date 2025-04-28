from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from controllers.log_controller import LogController

class LogsView(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Log Viewer")
        self.resize(600, 400)

        self.layout = QVBoxLayout(self)

        # Table to display logs
        self.log_table = QTableWidget()
        self.layout.addWidget(self.log_table)

        # Fetch logs
        self.load_logs()

        # Clear Logs Button
        self.clear_logs_button = QPushButton("Clear Logs")
        self.clear_logs_button.clicked.connect(self.clear_logs)
        self.layout.addWidget(self.clear_logs_button)

    def load_logs(self):
        log_controller = LogController()
        logs = log_controller.get_logs()

        self.log_table.setRowCount(len(logs))
        self.log_table.setColumnCount(3)
        self.log_table.setHorizontalHeaderLabels(["Timestamp", "Level", "Message"])

        for row_idx, log in enumerate(logs):
            self.log_table.setItem(row_idx, 0, QTableWidgetItem(log["timestamp"]))
            self.log_table.setItem(row_idx, 1, QTableWidgetItem(log["level"]))
            self.log_table.setItem(row_idx, 2, QTableWidgetItem(log["message"]))

        # Resize columns to fit content
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def clear_logs(self):
        log_controller = LogController()
        log_controller.clear_logs()
        self.load_logs()
