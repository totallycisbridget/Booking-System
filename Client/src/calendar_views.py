import datetime

from tkinter.ttk import Frame, Label

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:  # Avoid circular imports during runtime
    from src.calendar_container import CalendarContainer


class CalendarView(Frame):
    """Base class for calendar views."""

    def __init__(
        self,
        parent: "CalendarContainer",
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ):
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
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ):
        super().__init__(parent, year, month, day)

    def build_calendar(self):
        """Build the month view calendar."""
        # TODO: Placeholder information
        month_label = Label(
            self,
            text=f"Month View: {self.selected_date.strftime('%B %Y')}",
            font=("Arial", 16),
        )
        month_label.pack(pady=10)


class CalendarWeekView(CalendarView):
    """Calendar week view."""

    def __init__(
        self,
        parent: CalendarContainer,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ):
        super().__init__(parent, year, month, day)

    def build_calendar(self):
        """Build the week view calendar."""
        # TODO: Placeholder information
        week_label = Label(
            self,
            text=f"Week View: Week of {self.selected_date.strftime('%d %B %Y')}",
            font=("Arial", 16),
        )
        week_label.pack(pady=10)
