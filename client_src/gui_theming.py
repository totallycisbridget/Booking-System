import sys
import sv_ttk
import pywinstyles
from tkinter import Tk
from tkinter.ttk import Style
from typing import Dict


def apply_theme_to_titlebar(root, theme_colors: Dict[str, str]):
    # Check if running on Windows
    if sys.platform != "win32":
        return
    if not hasattr(sys, "getwindowsversion"):
        return
    
    version = sys.getwindowsversion()

    if version.major == 10 and version.build >= 22000:
        # Set the title bar color to the background color on Windows 11 for better appearance
        pywinstyles.change_header_color(root, theme_colors.get('-bg', '#000000'))
    elif version.major == 10:
        # Set the title bar style on Windows 10
        pywinstyles.apply_style(root, "dark" if sv_ttk.get_theme() == "dark" else "normal")

def colors_from_tcl_namespace(root: Tk | None = None, namespace: str = 'ttk::theme::sv_dark', array_name: str = 'colors') -> Dict[str, str]:
    """Load sv_ttk theme into Tcl and read the Tcl array containing color hex values.

    Returns a dict mapping keys like '-fg' -> {'hex': '#fafafa', 'rgb': (250,250,250)}
    """
    owned_root = False
    if root is None:
        root = Tk()
        root.withdraw()
        owned_root = True

    style = Style(master=root)
    sv_ttk._load_theme(style)

    tcl_cmd = f"namespace eval {namespace} {{array get {array_name}}}"
    raw = root.tk.eval(tcl_cmd)
    items = root.tk.splitlist(raw) if raw else ()

    out: Dict[str, str] = {}
    for i in range(0, len(items), 2):
        k = items[i]
        v = items[i + 1] if i + 1 < len(items) else ''
        hexcol = v.lower()
        out[k] = hexcol

    if owned_root and isinstance(root, Tk):
        root.destroy()

    return out

def set_window_theme(root: Tk, style: Style, theme: str) -> tuple[Style, Dict[str, str]]:
    """Set the sv_ttk theme for the given Tk root window and return the style and extracted colors."""
    theme_colors = colors_from_tcl_namespace(root, namespace=f"ttk::theme::sv_{theme}")
    theme_colors.setdefault('-error', '#ff99a4') # Color inspected from sv_ttk entry error sprite
    match theme:
        case 'dark':
            theme_colors.setdefault('-border', '#2f2f2f')
        case 'light':
            theme_colors.setdefault('-border', '#e7e7e7')
    
    sv_ttk.set_theme(theme)
    apply_theme_to_titlebar(root, theme_colors)

    return (style, theme_colors)