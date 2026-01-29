import datetime

from tkinter.ttk import Notebook

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # Avoid circular imports during runtime
    from src.calendar_views import (
        CalendarView,
        CalendarWeekView,
        CalendarMonthView,
    )


class CalendarContainer(Notebook):
    """Tab container for switching between calendar views."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<<NotebookTabChanged>>", self._reset_calendar)

    def _get_active_calendar(self) -> CalendarView:
        """Get the currently active calendar view."""
        return self.nametowidget(self.select())

    def _reset_calendar(self, event):
        """Reset the active calendar to the current date."""
        active_calendar = self._get_active_calendar()
        # Reset to current date when tab is changed
        today = datetime.date.today()
        active_calendar.set_timeframe(today.year, today.month, today.day)

    def set_calendar_active(self, calendarName: str):
        """Set the active calendar view by name."""
        for index in range(self.index("end")):
            if self.tab(index, "text") == calendarName:
                self.select(index)
                break

    def add_calendar_tab(
        self, calendarName: str, calendar: CalendarWeekView | CalendarMonthView
    ):
        """Add a calendar view to the container."""
        self.add(calendar, text=calendarName)
