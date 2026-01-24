import datetime

from tkinter.ttk import Frame, Label
from tkinter import Canvas
from calendar import Calendar, month_name as MONTHS, day_name as WEEKDAYS

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:  # Avoid circular imports during runtime
    from src.calendar_container import CalendarContainer

INTERNAL_BORDER_PADDING = 4

MAX_DAY_WIDTH = 200
MAX_MONTH_DAY_HEIGHT = 125

MAX_HEADER_HIGHT = MAX_MONTH_DAY_HEIGHT // 2


class CalendarHelper:
    """Static helpers for generating month and week layouts."""

    @staticmethod
    def get_calendar_month_layout(year: int, month: int) -> list[list[int]]:
        """Get the month layout as a list of weeks, each week is a list of day numbers.
        Days outside the month are represented by 0.
        """
        cal = Calendar(firstweekday=0)  # Monday as the first day
        month_days = cal.monthdayscalendar(year, month)

        return month_days


class CalendarItem(Frame):
    """Base widget for calendar cells."""

    def __init__(self, parent: Frame, height: int, width: int):
        super().__init__(parent, height=height, width=width, style="Card.TFrame")
        self.pack_propagate(False)  # Prevent frame from resizing to fit contents


class CalendarHeader(CalendarItem):
    """Header widget for calendar days."""

    def __init__(self, parent: Frame, theme_colors: dict[str, str], day_name: str):
        super().__init__(parent, height=MAX_HEADER_HIGHT, width=MAX_DAY_WIDTH)
        self.config(style="TButton")

        label = Label(
            self,
            text=day_name,
            style="Large.TLabel",
            background=theme_colors["-buttonbg"],
        )
        label.pack(
            expand=True,
            anchor="center",
            padx=INTERNAL_BORDER_PADDING,
            pady=INTERNAL_BORDER_PADDING,
        )


class CalendarDayCell(CalendarItem):
    """Generic calendar day cell widget."""

    def __init__(
        self, parent: Frame, theme_colors: dict[str, str], day_number: int, height: int
    ):
        super().__init__(parent, height=height, width=MAX_DAY_WIDTH)
        # Use canvas instead of multiple labels for better performance
        self.canvas = Canvas(
            self, bg=theme_colors.get("-bg", "ffffff"), highlightthickness=0
        )
        self.default_text_color = theme_colors.get("-fg", "black")
        self.accent_text_color = theme_colors.get("-accent", self.default_text_color)
        self.canvas.pack(
            fill="both",
            expand=True,
            padx=INTERNAL_BORDER_PADDING,
            pady=INTERNAL_BORDER_PADDING,
        )

    def draw_day_number(self, day_number: int, text_color: str):
        """Draw the day number in the top-left corner of the cell."""
        self.canvas.create_text(
            0,
            0,
            anchor="nw",
            text=str(day_number),
            font=("TkDefaultFont", 10, "bold"),
            fill=text_color,
        )


class CalendarMonthDayCell(CalendarDayCell):
    """Calendar day cell for month view."""

    def __init__(self, parent: Frame, theme_colors: dict[str, str], day_number: int):
        super().__init__(parent, theme_colors, day_number, MAX_MONTH_DAY_HEIGHT)
        self.draw_day_number(day_number, self.default_text_color)


class CalendarView(Frame):
    """Base class for calendar views."""

    def __init__(
        self,
        parent: "CalendarContainer",
        theme_colors: dict[str, str],
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ):
        self.theme_colors = theme_colors
        super().__init__(parent)
        # Initialize date to today if not provided
        today = datetime.date.today()
        # Check if year, month, day are provided, else use today's date
        self.year = year if year is not None else today.year
        self.month = month if month is not None else today.month
        self.day = day if day is not None else today.day

        self.selected_date = datetime.date(self.year, self.month, self.day)

        self.build_calendar()

    def build_calendar(self):
        """Build the calendar view. To be ran during class specific initialisation for all calendar views."""
        pass

    def set_timeframe(self, year: int, month: int, day: int):
        """Set the timeframe for the calendar view."""
        # Set year, month, day and update selected date
        self.year = year
        self.month = month
        self.day = day
        self.selected_date = datetime.date(self.year, self.month, self.day)

        # Rebuild the calendar view
        for widget in self.winfo_children():
            widget.destroy()
        self.build_calendar()


class CalendarMonthView(CalendarView):
    """Calendar month view."""

    def __init__(
        self,
        parent: CalendarContainer,
        theme_colors: dict[str, str],
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ):
        super().__init__(parent, theme_colors, year, month, day)

    def build_calendar(self):
        """Build the month view calendar."""
        layout = CalendarHelper.get_calendar_month_layout(self.year, self.month)

        # Add title saying month and year
        month_name = MONTHS[self.month]
        title_label = Label(
            self, text=f"{month_name} {self.year}", style="Header.TLabel"
        )
        title_label.pack(side="top", pady=5)

        calendar_grid = Frame(self)

        # Create day headers
        for col, day_name in enumerate(WEEKDAYS):
            header_day = CalendarHeader(calendar_grid, self.theme_colors, day_name)
            header_day.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        calendar_grid.pack(side="top", fill="y", expand=True)

        # Create month day cells
        for row, week in enumerate(layout):
            for col, day_number in enumerate(week):
                # Ignore days outside the month (represented by 0)
                if day_number != 0:
                    day_cell = CalendarMonthDayCell(
                        calendar_grid, self.theme_colors, day_number
                    )
                    day_cell.grid(row=row + 1, column=col, sticky="nsew", padx=1, pady=1)

class CalendarWeekView(CalendarView):
    """Calendar week view."""

    def __init__(
        self,
        parent: CalendarContainer,
        theme_colors: dict[str, str],
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ):
        super().__init__(parent, theme_colors, year, month, day)

    def build_calendar(self):
        """Build the week view calendar."""
        # TODO: Placeholder information
        week_label = Label(
            self,
            text=f"Week View: Week of {self.selected_date.strftime('%d %B %Y')}",
            font=("Arial", 16),
        )
        week_label.pack(pady=10)
