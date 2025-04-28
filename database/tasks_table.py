from PyQt6.QtSql import QSqlDatabase, QSqlQuery

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
