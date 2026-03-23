import datetime

from tkinter.ttk import Frame, Label, Button, Separator
from tkinter import Canvas
from calendar import Calendar, month_name as MONTHS, day_name as WEEKDAYS, monthrange

from typing import Optional, TYPE_CHECKING

from src.data_local_manager import LocalDataManager

if TYPE_CHECKING:  # Avoid circular imports during runtime
    from src.calendar_container import CalendarContainer

INTERNAL_BORDER_PADDING = 4
CALENDAR_CELL_PADDING = 1

MAX_DAY_WIDTH = 200
MAX_MONTH_DAY_HEIGHT = 115
MAX_WEEK_DAY_HEIGHT = (MAX_MONTH_DAY_HEIGHT * 6) + (CALENDAR_CELL_PADDING * 2 * 5)

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

    @staticmethod
    def get_full_week_layout(
        year: int, month: int, day: int, include_other_months: bool = True
    ) -> list[int]:
        """Get the full week layout including days from previous and next months."""
        week = []

        # Get the week layout for the given day
        week_start = datetime.date(year, month, day) - datetime.timedelta(
            days=datetime.date(year, month, day).weekday()
        )
        for i in range(7):
            current_day = week_start + datetime.timedelta(days=i)
            if current_day.month == month:
                week.append(current_day.day)
            elif include_other_months:
                week.append(current_day.day)
            else:
                week.append(0)

        return week


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

    def __init__(self, parent: Frame, theme_colors: dict[str, str], height: int):
        super().__init__(parent, height=height, width=MAX_DAY_WIDTH)
        self.theme_colors = theme_colors
        self.initial_offset_y = 0
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

    def format_event_time(
        self,
        start_time: datetime.time | str | None,
        end_time: datetime.time | str | None,
    ) -> str:
        """Format an event time range for display."""

        def normalize_time(value: datetime.time | str | None) -> str:
            if isinstance(value, datetime.time):
                return value.strftime("%H:%M")
            if isinstance(value, str):
                try:
                    return datetime.datetime.strptime(value, "%H:%M").strftime("%H:%M")
                except ValueError:
                    return value
            return ""

        start_str = normalize_time(start_time)
        end_str = normalize_time(end_time)

        if start_str and end_str:
            return f"{start_str} - {end_str}"
        if start_str:
            return start_str
        return ""

    def draw_day_number(self, day_number: int, text_color: str):
        """Draw the day number in the top-left corner of the cell."""
        return self.draw_text(
            0,
            0,
            str(day_number),
            anchor="nw",
            text=str(day_number),
            font=("TkDefaultFont", 10, "bold"),
            fill=text_color,
        )

    def draw_events(self, events: list[dict], max_lines: int = 0):
        """Draw a list of event titles for the day."""
        raise NotImplementedError("Subclasses must implement draw_events method.")

    def draw_text(
        self,
        x: int | float,
        y: int | float,
        text: str,
        *,
        anchor: str = "nw",
        font: tuple = (),
        fill: str = "black",
        width: int | None = None,
    ) -> int:
        """Draw text and return its pixel height."""
        item_id = self.canvas.create_text(
            x,
            y,
            text=text,
            anchor=anchor,  # pyright: ignore[reportArgumentType]
            font=font,
            fill=fill,
            width=width,  # pyright: ignore[reportArgumentType]
        )
        bbox = self.canvas.bbox(item_id)
        height = (bbox[3] - bbox[1]) if bbox else 0
        return height

    def draw_line(
        self,
        x1: int | float,
        y1: int | float,
        x2: int | float,
        y2: int | float,
        *,
        fill: str = "black",
        width: int = 1,
    ):
        """Draw a straight line on the canvas."""
        return self.canvas.create_line(x1, y1, x2, y2, fill=fill, width=width)


class CalendarMonthDayCell(CalendarDayCell):
    """Calendar day cell for month view."""

    def __init__(
        self,
        parent: Frame,
        theme_colors: dict[str, str],
        day_number: int,
    ):
        super().__init__(parent, theme_colors, MAX_MONTH_DAY_HEIGHT)
        self.initial_offset_y = self.draw_day_number(day_number, self.default_text_color)

    def draw_events(self, events: list[dict], max_lines: int = 3):
        if len(events) == 0 or max_lines <= 0:
            return

        offset = self.initial_offset_y + 5  # Start below day number with small gap
        events_shown = 0

        for event in events:
            if events_shown >= max_lines:
                # Show "more events" indicator if there are remaining events
                remaining = len(events) - events_shown
                self.draw_text(
                    0,
                    offset,
                    f"+ {remaining} more",
                    anchor="nw",
                    font=("TkDefaultFont", 8, "italic"),
                    fill=self.accent_text_color,
                    width=MAX_DAY_WIDTH - (INTERNAL_BORDER_PADDING * 2),
                )
                break

            event_title = event.get("title", "No Title")
            start_time = event.get("start_time")
            time_str = self.format_event_time(start_time, None)

            # For month view, show time and title on same line if possible
            if time_str:
                display_text = f"{time_str} {event_title}"
            else:
                display_text = event_title

            title_height = self.draw_text(
                0,
                offset,
                display_text,
                anchor="nw",
                font=("TkDefaultFont", 8),
                fill=self.default_text_color,
                width=MAX_DAY_WIDTH - (INTERNAL_BORDER_PADDING * 2),
            )

            offset += title_height + 2  # Small gap between events
            events_shown += 1


class CalendarWeekDayCell(CalendarDayCell):
    """Calendar day cell for week view."""

    def __init__(self, parent: Frame, theme_colors: dict[str, str], day_number: int):
        super().__init__(parent, theme_colors, MAX_WEEK_DAY_HEIGHT)
        self.initial_offset_y = self.draw_day_number(
            day_number, self.default_text_color
        )

    def draw_events(self, events: list[dict], max_lines: int = 6):
        if len(events) == 0 or max_lines <= 0:
            return

        offset = self.initial_offset_y  # Start below day number

        for event in events:
            offset = self.draw_event(event, offset)

    def draw_event(self, event: dict, y_position: int) -> int:
        event_title = event.get("title", "No Title")
        start_time = event.get("start_time")
        end_time = event.get("end_time")
        time_str = self.format_event_time(start_time, end_time)

        title_height = self.draw_text(
            0,
            y_position,
            event_title,
            anchor="nw",
            font=("TkDefaultFont", 10),
            fill=self.default_text_color,
            width=MAX_DAY_WIDTH - (INTERNAL_BORDER_PADDING * 2),
        )

        y_position += title_height

        time_height = self.draw_text(
            0,
            y_position,
            time_str,
            anchor="nw",
            font=("TkDefaultFont", 8, "italic"),
            fill=self.default_text_color,
            width=MAX_DAY_WIDTH - (INTERNAL_BORDER_PADDING * 2),
        )

        y_position += time_height

        # Draw horizontal separator line
        y_position += 2  # Small gap before line
        self.draw_line(
            0,
            y_position,
            MAX_DAY_WIDTH - (INTERNAL_BORDER_PADDING * 2),
            y_position,
            fill=self.theme_colors.get("-border", "grey"),
        )

        y_position += 4  # Small gap after line

        return y_position  # Return new y_position after drawing event


class CalendarView(Frame):
    """Base class for calendar views."""

    def __init__(
        self,
        parent: "CalendarContainer",
        theme_colors: dict[str, str],
        data_manager: Optional[LocalDataManager] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ):
        self.theme_colors = theme_colors
        self.data_manager = data_manager
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
        self.calendar_controls_frame = Frame(self)

        # Give each control column equal weight so the Today button sits in the center column
        for col in range(3):
            self.calendar_controls_frame.columnconfigure(col, weight=1)
        
        self.previous_button = Button(
            self.calendar_controls_frame,
            text="< Previous",
            command=self._go_to_previous
        )
        self.next_button = Button(
            self.calendar_controls_frame,
            text="Next >",
            command=self._go_to_next
        )
        self.set_timeframe_today_button = Button(
            self.calendar_controls_frame,
            text="Today",
            command=self._go_to_today,
            style="Accent.TButton"
        )
        
        self.previous_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.set_timeframe_today_button.grid(row=0, column=1, padx=5, pady=5)
        self.next_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        self.calendar_controls_frame.pack(side="bottom", fill="x")
        Separator(self, orient="horizontal").pack(side="bottom", fill="x")

    def build_day_headers(self, calendar_grid: Frame):
        """Add weekday headers to the provided calendar grid."""
        for col, day_name in enumerate(WEEKDAYS):
            header_day = CalendarHeader(calendar_grid, self.theme_colors, day_name)

    def _get_events_for_date(self, date_value: datetime.date) -> list[dict]:
        """Return events for a specific date if data is available."""
        if not self.data_manager or not self.data_manager.data_loaded:
            return []
        try:
            events = self.data_manager.get_data_at_day(
                date_value.year, date_value.month, date_value.day
            )
            return events if isinstance(events, list) else []
        except Exception:
            return []

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

    def _shift_month(self, delta_months: int) -> tuple[int, int, int]:
        """Return year, month, day after shifting the current month by delta_months."""
        total_months = (self.year * 12 + (self.month - 1)) + delta_months
        new_year = total_months // 12
        new_month = total_months % 12 + 1
        max_day = monthrange(new_year, new_month)[1]
        new_day = min(self.day, max_day)
        return new_year, new_month, new_day

    def _go_to_previous(self):
        """Navigate to the previous week or month based on the view type."""
        if isinstance(self, CalendarWeekView):
            new_date = self.selected_date - datetime.timedelta(days=7)
            self.set_timeframe(new_date.year, new_date.month, new_date.day)
        else:
            new_year, new_month, new_day = self._shift_month(-1)
            self.set_timeframe(new_year, new_month, new_day)

    def _go_to_next(self):
        """Navigate to the next week or month based on the view type."""
        if isinstance(self, CalendarWeekView):
            new_date = self.selected_date + datetime.timedelta(days=7)
            self.set_timeframe(new_date.year, new_date.month, new_date.day)
        else:
            new_year, new_month, new_day = self._shift_month(1)
            self.set_timeframe(new_year, new_month, new_day)

    def _go_to_today(self):
        """Navigate to today's date for the active view."""
        today = datetime.date.today()
        self.set_timeframe(today.year, today.month, today.day)


class CalendarMonthView(CalendarView):
    """Calendar month view."""

    def __init__(
        self,
        parent: CalendarContainer,
        theme_colors: dict[str, str],
        data_manager: Optional[LocalDataManager] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ):
        super().__init__(parent, theme_colors, data_manager, year, month, day)

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
        self.build_day_headers(calendar_grid)

        # Create month day cells
        for row, week in enumerate(layout):
            for col, day_number in enumerate(week):
                # Ignore days outside the month (represented by 0)
                if day_number != 0:
                    day_cell = CalendarMonthDayCell(
                        calendar_grid, self.theme_colors, day_number
                    day_cell.draw_events(
                        self._get_events_for_date(date_value), max_lines=3
                    )
                    day_cell.grid(
                        row=row + 1, column=col, sticky="nsew", padx=CALENDAR_CELL_PADDING, pady=CALENDAR_CELL_PADDING
                    )

        calendar_grid.pack(side="top", fill="y", expand=True)
        
        # Call the base class build_calendar to finalize
        super().build_calendar()


class CalendarWeekView(CalendarView):
    """Calendar week view."""

    def __init__(
        self,
        parent: CalendarContainer,
        theme_colors: dict[str, str],
        data_manager: Optional[LocalDataManager] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ):
        super().__init__(parent, theme_colors, data_manager, year, month, day)

    def build_calendar(self):
        """Build the week view calendar."""
        layout = CalendarHelper.get_full_week_layout(self.year, self.month, self.day)
        # Add title saying week range
        week_start = datetime.date(
            self.year, self.month, self.day
        ) - datetime.timedelta(
            days=datetime.date(self.year, self.month, self.day).weekday()
        )
        week_end = week_start + datetime.timedelta(days=6)

        if week_start.month == week_end.month:
            label_text = f"Week of {MONTHS[week_start.month]} {week_start.day} - {week_end.day}, {week_start.year}"
        else:
            label_text = f"Week of {MONTHS[week_start.month]} {week_start.day} - {MONTHS[week_end.month]} {week_end.day}, {week_end.year}"

        title_label = Label(self, text=label_text, style="Header.TLabel")
        title_label.pack(pady=5)

        calendar_grid = Frame(self)

        # Generate week day headers
        self.build_day_headers(calendar_grid)

        for col, day_number in enumerate(layout):
            day_cell = CalendarWeekDayCell(calendar_grid, self.theme_colors, day_number)
            day_cell.draw_events(self._get_events_for_date(date_value), max_lines=30)
            day_cell.grid(row=1, column=col, sticky="nsew", padx=CALENDAR_CELL_PADDING, pady=CALENDAR_CELL_PADDING)

        calendar_grid.pack(side="top", fill="y", expand=True)
        
        # Call the base class build_calendar to finalize
        super().build_calendar()
