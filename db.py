from PyQt6.QtSql import QSqlDatabase, QSqlQuery

def init_db(db_name):
    database = QSqlDatabase.addDatabase("QSQLITE")
    database.setDatabaseName(db_name)

    if not database.open():
        return False
    
    query = QSqlQuery()
    query.exec("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    category TEXT,
                    amount REAL,
                    description  TEXT 
                )
                """)
    
    return True

def fetch_expenses():
    query = QSqlQuery("SELECT * FROM expenses ORDER BY date DESC")
    expenses=[]
    while query.next():
        expenses.append([query.value(i) for i in range(5)])
    return expenses

def add_expenses(date, category, amount, description):
    query = QSqlQuery()
    print(query.lastError().text())
    query.prepare("""
                    INSERT INTO expenses (date, category, amount, description)
                    VALUES (?,?,?,?)
                """)
    
    query.addBindValue(date)
    query.addBindValue(category)
    query.addBindValue(amount)
    query.addBindValue(description)
    
    print(f"Adding: {date}, {category}, {amount}, {description}")
    
    return query.exec()

def delete_expences(expense_id):
    query = QSqlQuery()
    query.prepare("DELETE FROM expenses WHERE id = ?")

    query.addBindValue(expense_id)

    return query.exec()