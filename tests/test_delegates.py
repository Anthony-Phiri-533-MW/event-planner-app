import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt, QEvent
from event_planner.delegates import CheckBoxDelegate

@pytest.fixture
def delegate():
    with patch('PyQt5.QtWidgets.QStyledItemDelegate.__init__', return_value=None):
        return CheckBoxDelegate()

@pytest.fixture
def mock_setup():
    model = MagicMock()
    index = MagicMock()
    option = MagicMock()
    return model, index, option

def test_create_editor(delegate, mock_setup):
    model, index, option = mock_setup
    editor = delegate.createEditor(None, option, index)
    assert editor is None

def test_editor_event_toggle_checked(delegate, mock_setup):
    model, index, option = mock_setup
    event = MagicMock(spec=QEvent)
    event.type.return_value = QEvent.MouseButtonRelease
    event.button.return_value = Qt.LeftButton
    index.data.return_value = Qt.Checked

    result = delegate.editorEvent(event, model, option, index)

    assert result
    model.setData.assert_called_with(index, Qt.Unchecked, Qt.CheckStateRole)

def test_editor_event_toggle_unchecked(delegate, mock_setup):
    model, index, option = mock_setup
    event = MagicMock(spec=QEvent)
    event.type.return_value = QEvent.MouseButtonRelease
    event.button.return_value = Qt.LeftButton
    index.data.return_value = Qt.Unchecked

    result = delegate.editorEvent(event, model, option, index)

    assert result
    model.setData.assert_called_with(index, Qt.Checked, Qt.CheckStateRole)

def test_editor_event_non_mouse_release(delegate, mock_setup):
    model, index, option = mock_setup
    event = MagicMock(spec=QEvent)
    event.type.return_value = QEvent.MouseButtonPress

    result = delegate.editorEvent(event, model, option, index)

    assert not result
    model.setData.assert_not_called()