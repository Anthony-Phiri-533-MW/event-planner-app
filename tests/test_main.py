import pytest
from unittest.mock import patch, MagicMock
from event_planner.main import QApplication
from event_planner.app import EventPlannerApp

def test_main():
    with patch('event_planner.main.QApplication') as mock_qapplication:
        with patch('event_planner.app.EventPlannerApp') as mock_event_planner_app:
            mock_app = mock_qapplication.return_value
            mock_window = mock_event_planner_app.return_value

            with patch('sys.argv', ['script.py']):
                import event_planner.main
                event_planner.main

            mock_qapplication.assert_called_once()
            mock_event_planner_app.assert_called_once()
            mock_window.resize.assert_called_with(1000, 600)
            mock_window.show.assert_called_once()
            mock_app.exec_.assert_called_once()