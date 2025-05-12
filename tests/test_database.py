import pytest
from event_planner.database import EventDatabase

@pytest.fixture
def db():
    db = EventDatabase(":memory:")
    db.create_tables()
    yield db
    db.conn.close()

def test_create_user(db):
    user_id = db.create_user("test_user", "password", "test@example.com")
    assert user_id is not None
    user = db.get_user_by_id(user_id)
    assert user["username"] == "test_user"
    assert user["email"] == "test@example.com"
    assert user["password_hash"] != "password"

def test_create_user_duplicate(db):
    db.create_user("test_user", "password")
    user_id = db.create_user("test_user", "password2")
    assert user_id is None

def test_authenticate_user(db):
    user_id = db.create_user("test_user", "password")
    assert db.authenticate_user("test_user", "password") == user_id
    assert db.authenticate_user("test_user", "wrong") is None
    assert db.authenticate_user("nonexistent", "password") is None

def test_add_event(db):
    user_id = db.create_user("test_user", "password")
    event_id = db.add_event(user_id, "Event 1", "2025-06-01", "12:00", "Venue", "Desc")
    events = db.get_all_events(user_id)
    assert len(events) == 1
    assert events[0][2] == "Event 1"
    assert events[0][1] == user_id

def test_update_event(db):
    user_id = db.create_user("test_user", "password")
    event_id = db.add_event(user_id, "Event 1", "2025-06-01", "12:00", "Venue", "Desc")
    db.update_event(event_id, "Updated Event", "2025-06-02", "13:00", "New Venue", "New Desc")
    event = db.get_event_by_id(event_id)
    assert event[2] == "Updated Event"
    assert event[3] == "2025-06-02"

def test_delete_event(db):
    user_id = db.create_user("test_user", "password")
    event_id = db.add_event(user_id, "Event 1", "2025-06-01", "12:00", "Venue", "Desc")
    db.delete_event(event_id)
    events = db.get_all_events(user_id)
    assert len(events) == 0

def test_add_task(db):
    user_id = db.create_user("test_user", "password")
    event_id = db.add_event(user_id, "Event 1", "2025-06-01", "12:00", "Venue", "Desc")
    db.add_task(event_id, "Task 1")
    tasks = db.get_tasks_for_event(event_id)
    assert len(tasks) == 1
    assert tasks[0][2] == "Task 1"

def test_add_guest(db):
    user_id = db.create_user("test_user", "password")
    event_id = db.add_event(user_id, "Event 1", "2025-06-01", "12:00", "Venue", "Desc")
    db.add_guest(event_id, "Guest 1", "guest@example.com")
    guests = db.get_guests_for_event(event_id)
    assert len(guests) == 1
    assert guests[0][2] == "Guest 1"

def test_archive_event(db):
    user_id = db.create_user("test_user", "password")
    event_id = db.add_event(user_id, "Event 1", "2025-06-01", "12:00", "Venue", "Desc")
    db.add_task(event_id, "Task 1")
    db.update_task_status(1, True)
    success = db.archive_event(event_id)
    assert success
    archived = db.get_archived_events(user_id)
    assert len(archived) == 1
    assert archived[0][2] == "Event 1"
    events = db.get_all_events(user_id)
    assert len(events) == 0