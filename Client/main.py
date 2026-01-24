from pathlib import Path

from tkinter import Tk
from tkinter.ttk import Separator

from src.gui_general import set_window_centered, set_icon_from_path
from src.gui_theming import apply_all_theming
from src.gui_sidebar import Sidebar

from src.calendar_container import CalendarContainer
from src.calendar_views import CalendarWeekView, CalendarMonthView

current_dir = Path(__file__).parent  # Current running directory of this script


class App(Tk):
    """Main application window."""

    WINDOW_NAME = "Placeholder Window Title"
    WINDOW_DIMENSIONS = "1700x900"
    SELECTED_THEME = "dark"  # "dark" or "light"

    WIDGET_PADDING = 5

    def __init__(self):
        super().__init__()
        self.iconify()  # Hide window during setup

        # Style setup and theming
        self.style, self.theme_colors = apply_all_theming(self, self.SELECTED_THEME)

        self.title(self.WINDOW_NAME)
        self.geometry(self.WINDOW_DIMENSIONS)

        # Set window icon
        self.assets_path = current_dir / "assets"
        app_icon_path = self.assets_path / "icon.ico"
        set_icon_from_path(self, app_icon_path.as_posix())

        # Setup Widgets
        self.place_widgets()

        self.deiconify()  # Show window after setup

        # Center the window on the screen
        set_window_centered(
            self,
            *map(int, self.WINDOW_DIMENSIONS.split("x")),  # Unpack width and height
        )

    def place_widgets(self):
        """Place main widgets in the application window."""
        self.sidebar = Sidebar(self, self.assets_path)
        self.sidebar.pack(side="left", fill="y", padx=self.WIDGET_PADDING)
        Separator(self, orient="vertical").pack(
            side="left", fill="y", padx=(0, self.WIDGET_PADDING)
        )
        
        self.calendar_container = CalendarContainer(self)
        
        self.calendar_container.add_calendar_tab(
            "Week", CalendarWeekView(self.calendar_container)
        )
        self.calendar_container.add_calendar_tab(
            "Month", CalendarMonthView(self.calendar_container)
        )
        self.calendar_container.pack(
            side="left", fill="both", expand=True, padx=self.WIDGET_PADDING, pady=self.WIDGET_PADDING
        )
        


if __name__ == "__main__":
    app = App()
    app.mainloop()
