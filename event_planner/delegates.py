from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtCore import Qt

class CheckBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        return None  # Prevent editing, we'll handle clicks directly

    def editorEvent(self, event, model, option, index):
        if event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
            current_value = index.data(Qt.CheckStateRole)
            new_value = Qt.Unchecked if current_value == Qt.Checked else Qt.Checked
            model.setData(index, new_value, Qt.CheckStateRole)
            return True
        return False