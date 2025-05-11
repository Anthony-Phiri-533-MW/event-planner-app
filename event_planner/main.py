import sys
from PyQt5.QtWidgets import QApplication
from .app import EventPlannerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = EventPlannerApp()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec_())
