from PyQt6.QtSql import QSqlDatabase, QSqlQuery

DB_NAME = "events.db"

def connect_db():
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(DB_NAME)
    if not db.open():
        raise Exception("Could not open database.")
    return db

def create_table():
    query = QSqlQuery()
    query.exec(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            event_time TEXT NOT NULL,
            location TEXT
        );
        """
    )

def get_all_events():
    query = QSqlQuery("SELECT * FROM events")
    results = []
    while query.next():
        row = (
            query.value(0),  # id
            query.value(1),  # event_type
            query.value(2),  # event_date
            query.value(3),  # event_time
            query.value(4),  # location
        )
        results.append(row)
    return results

def add_event(event_type, event_date, event_time, location):
    query = QSqlQuery()
    query.prepare(
        """
        INSERT INTO events (event_type, event_date, event_time, location)
        VALUES (?, ?, ?, ?)
        """
    )
    query.addBindValue(event_type)
    query.addBindValue(event_date)
    query.addBindValue(event_time)
    query.addBindValue(location)
    return query.exec()

def edit_event(event_id, event_type, event_date, event_time, location):
    query = QSqlQuery()
    query.prepare(
        """
        UPDATE events
        SET event_type = ?, event_date = ?, event_time = ?, location = ?
        WHERE id = ?
        """
    )
    query.addBindValue(event_type)
    query.addBindValue(event_date)
    query.addBindValue(event_time)
    query.addBindValue(location)
    query.addBindValue(event_id)
    return query.exec()

def delete_event(event_id):
    query = QSqlQuery()
    query.prepare("DELETE FROM events WHERE id = ?")
    query.addBindValue(event_id)
    return query.exec()

def create_tasks_table():
    query = QSqlQuery()
    query.exec(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            event_id INTEGER,
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
        );
        """
    )

def get_all_tasks():
    query = QSqlQuery("SELECT * FROM tasks")
    results = []
    while query.next():
        row = (
            query.value(0),  # id
            query.value(1),  # title
            query.value(2),  # status
            query.value(3),  # priority
            query.value(4),  # event_id
        )
        results.append(row)
    return results

def add_task(title, status, priority, event_id=None):
    query = QSqlQuery()
    query.prepare(
        """
        INSERT INTO tasks (title, status, priority, event_id)
        VALUES (?, ?, ?, ?)
        """
    )
    query.addBindValue(title)
    query.addBindValue(status)
    query.addBindValue(priority)
    query.addBindValue(event_id)
    return query.exec()

def edit_task(task_id, title, status, priority, event_id=None):
    query = QSqlQuery()
    query.prepare(
        """
        UPDATE tasks
        SET title = ?, status = ?, priority = ?, event_id = ?
        WHERE id = ?
        """
    )
    query.addBindValue(title)
    query.addBindValue(status)
    query.addBindValue(priority)
    query.addBindValue(event_id)
    query.addBindValue(task_id)
    return query.exec()

def delete_task(task_id):
    query = QSqlQuery()
    query.prepare("DELETE FROM tasks WHERE id = ?")
    query.addBindValue(task_id)
    return query.exec()
