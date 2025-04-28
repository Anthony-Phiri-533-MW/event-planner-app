class ThemeManager:
    def __init__(self):
        self.current_theme = "Light"

    def set_theme(self, theme_name):
        self.current_theme = theme_name

    def apply_theme(self, widget):
        if self.current_theme == "Dark":
            widget.setStyleSheet("""
                QWidget {
                    background-color: #250034;
                    color: #FFFFFF;
                }
                QPushButton {
                    background-color: #BE87D5;
                    color: #FFFFFF;
                }
            """)
        else:
            widget.setStyleSheet("""
                QWidget {
                    background-color: #FFFFFF;
                    color: #250034;
                }
                QPushButton {
                    background-color: #BE87D5;
                    color: #250034;
                }
            """)
