import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

# from app 
from database import connect_db, get_all_events 

# from db import fetch_expenses, add_expenses, delete_expences

def main():
    app = QApplication(sys.argv)

    if not connect_db():
        QMessageBox.critical(None, "error", "Could not load database")
        sys.exit(1)

    print("BD creation: Success")
    
    sys.exit(app.exec())



if __name__ == "__main__":
    main()