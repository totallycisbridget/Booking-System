from pathlib import Path

def set_window_centered(window, width: int, height: int) -> None:
    """Set the given window's geometry to be centered on the screen with the given width and height."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    window.geometry(f"{width}x{height}+{x}+{y}")
    
def set_icon_from_path(window, icon_path: str) -> None:
    """Set the window icon from the given file path."""

    icon_file = Path(icon_path)
    if icon_file.is_file():
        window.iconbitmap(str(icon_file))