from pathlib import Path

from tkinter import Tk
from tkinter.ttk import Style, Label

from client_src.gui_theming import set_window_theme
from client_src.gui_general import set_window_centered, set_icon_from_path

current_dir = Path(__file__).parent # Current running directory of this script

class App(Tk):
    """Main application window.
    """
    WINDOW_NAME = "Placeholder Window Title"
    WINDOW_DIMENSIONS = "1400x800"
    SELECTED_THEME = "dark"  # "dark" or "light"

    def __init__(self):
        super().__init__()
        self.iconify() # Hide window during setup

        # Style setup
        self.style = Style(self)
        # Set window theming
        self.style, self.theme_colors = set_window_theme(
            self, self.style, self.SELECTED_THEME
        )

        # Custom theming based on existing sv_ttk theme
        self.style.configure("Header.TLabel", font=("TkDefaultFont", 20, "bold"))

        self.title(self.WINDOW_NAME)
        self.geometry(self.WINDOW_DIMENSIONS)
        app_icon_path = current_dir / "assets" / "icon.ico"
        
        set_icon_from_path(self, app_icon_path.as_posix())

        self.place_widgets()

        self.deiconify() # Show window after setup
        # Center the window on the screen
        set_window_centered(
            self,
            int(self.WINDOW_DIMENSIONS.split("x")[0]),
            int(self.WINDOW_DIMENSIONS.split("x")[1]),
        )

    def place_widgets(self):
        """Place widgets in the main application window.
        """
        self.placeholderTitle = Label(
            self, text="Placeholder Heading", style="Header.TLabel"
        )
        self.placeholderTitle.pack(pady=20)

        


if __name__ == "__main__":
    app = App()
    app.mainloop()
