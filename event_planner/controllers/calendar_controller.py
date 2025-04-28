from controllers.event_controller import EventController

class CalendarController:
    def __init__(self):
        self.event_controller = EventController()

    def get_event_dates(self):
        """Return a list of dates that have events."""
        events = self.event_controller.db.fetch_all('SELECT start_datetime FROM events')
        event_dates = set()
        for event in events:
            date = event['start_datetime'].split(" ")[0]
            event_dates.add(date)
        return list(event_dates)

    def get_events_on_date(self, date_str: str):
        """Return all events on a given date."""
        return self.event_controller.get_events_by_date(date_str)
