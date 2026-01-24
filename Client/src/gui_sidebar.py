from tkinter.ttk import Frame, Button


class Sidebar(Frame):
    """Sidebar frame for the application."""

    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        self.home_button = Button(self, text="Home", style="Large.TButton")
        self.home_button.pack(fill="x", padx=5, pady=5)
        self.calendar_button = Button(self, text="Calendar", style="Large.TButton")
        self.calendar_button.pack(fill="x", padx=5, pady=5)
        self.settings_button = Button(self, text="Settings", style="Large.TButton")
        self.settings_button.pack(fill="x", padx=5, pady=5)
        self.about_button = Button(self, text="About", style="Large.TButton")
        self.about_button.pack(fill="x", padx=5, pady=5)
        self.help_button = Button(self, text="Help", style="Large.TButton")
        self.help_button.pack(fill="x", padx=5, pady=5)
