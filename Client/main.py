from pathlib import Path

from tkinter import Tk

from src.gui_general import set_window_centered

current_dir = Path(__file__).parent  # Current running directory of this script


class App(Tk):
    """Main application window."""

    WINDOW_NAME = "Placeholder Window Title"
    WINDOW_DIMENSIONS = "1700x900"

    def __init__(self):
        super().__init__()
        self.iconify()  # Hide window during setup

        self.title(self.WINDOW_NAME)
        self.geometry(self.WINDOW_DIMENSIONS)
        
        self.deiconify()  # Show window after setup

        # Center the window on the screen
        set_window_centered(
            self,
            *map(int, self.WINDOW_DIMENSIONS.split("x")), # Unpack width and height
        )

if __name__ == "__main__":
    app = App()
    app.mainloop()