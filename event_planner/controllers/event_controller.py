from core.database import Database

class EventController:
    def __init__(self):
        self.db = Database()

    def create_event(self, event_data: dict):
        query = '''INSERT INTO events (title, description, start_datetime, end_datetime, category_id, event_type_id, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))'''
        params = (
            event_data["title"],
            event_data.get("description", ""),
            event_data["start_datetime"],
            event_data["end_datetime"],
            event_data.get("category_id"),
            event_data.get("event_type_id")
        )
        self.db.execute(query, params)

    def get_events_by_date(self, date_str: str):
        query = '''SELECT * FROM events WHERE date(start_datetime) = ?'''
        return self.db.fetch_all(query, (date_str,))

    def update_event(self, event_id: int, updated_data: dict):
        query = '''UPDATE events SET title = ?, description = ?, start_datetime = ?, end_datetime = ?, category_id = ?, event_type_id = ?, updated_at = datetime('now') WHERE id = ?'''
        params = (
            updated_data["title"],
            updated_data.get("description", ""),
            updated_data["start_datetime"],
            updated_data["end_datetime"],
            updated_data.get("category_id"),
            updated_data.get("event_type_id"),
            event_id
        )
        self.db.execute(query, params)

    def delete_event(self, event_id: int):
        query = '''DELETE FROM events WHERE id = ?'''
        self.db.execute(query, (event_id,))
