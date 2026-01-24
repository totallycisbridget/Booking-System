from pathlib import Path

from tkinter import Tk

from src.gui_general import set_window_centered, set_icon_from_path
from src.gui_theming import apply_all_theming

current_dir = Path(__file__).parent  # Current running directory of this script


class App(Tk):
    """Main application window."""

    WINDOW_NAME = "Placeholder Window Title"
    WINDOW_DIMENSIONS = "1700x900"
    SELECTED_THEME = "dark"  # "dark" or "light"

    def __init__(self):
        super().__init__()
        self.iconify()  # Hide window during setup

        # Style setup and theming
        self.style, self.theme_colors = apply_all_theming(self, self.SELECTED_THEME)

        self.title(self.WINDOW_NAME)
        self.geometry(self.WINDOW_DIMENSIONS)

        # Set window icon
        app_icon_path = current_dir / "assets" / "icon.ico"
        set_icon_from_path(self, app_icon_path.as_posix())

        self.deiconify()  # Show window after setup

        # Center the window on the screen
        set_window_centered(
            self,
            *map(int, self.WINDOW_DIMENSIONS.split("x")),  # Unpack width and height
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()
