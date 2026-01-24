from pathlib import Path

from tkinter.ttk import Frame, Button, Label

from PIL import Image, ImageTk


class AppImage(Frame):
    """Frame to hold and display an image in the application."""

    def __init__(self, parent, image_path: Path, size: tuple = (100, 100)):
        super().__init__(parent)
        self.image_host = []  # Keep references to image objects

        self.img = Image.open(image_path.as_posix())
        self.img.thumbnail(size)
        self.photo = ImageTk.PhotoImage(self.img)
        self.image_host.append(self.photo)
        self.img_label = Label(self, image=self.photo)
        self.img_label.pack()


class Sidebar(Frame):
    """Sidebar frame for the application."""

    def __init__(self, parent, assets_path: Path):
        super().__init__(parent)
        self.sidebar_img_path = assets_path / "icon.png"
        self.create_widgets()

    def create_widgets(self):
        # Load image assets/icon.png
        self.img = AppImage(self, self.sidebar_img_path, size=(100, 100))
        self.img.pack(pady=10)

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
