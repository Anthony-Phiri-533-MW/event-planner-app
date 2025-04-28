from PyQt6.QtSql import QSqlDatabase, QSqlQuery

DB_NAME = "event_planner.db"

def connect_db():
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(DB_NAME)
    if not db.open():
        raise Exception("Could not open database.")
    return db

