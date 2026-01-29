from pathlib import Path
import json


class LocalDataManager:
    """Manages local data storage and retrieval for the client application."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.events = self.storage_path / "events.json"
        self.data_loaded = False
        self.events_data = {}

    def validate_and_load_data(self) -> dict[str, bool | str]:
        """Load data from local storage."""

        # Check if storage path exists
        if not self.storage_path.exists():
            return {"state": False, "reason": "Storage path does not exist."}
        # Check if events file exists
        if not self.events.exists():
            return {"state": False, "reason": "Events file does not exist."}
        try:
            with open(self.events, "r") as f:
                self.events_data = json.load(f)
            self.data_loaded = True
            return {"state": True}
        except json.JSONDecodeError:
            return {"state": False, "reason": "Failed to decode events file."}
        except Exception as e:
            return {"state": False, "reason": str(e)}

    def get_data_at_year(self, year: int):
        """Retrieve events for a specific year."""
        if not self.data_loaded:
            raise RuntimeError("Data not loaded. Call validate_and_load_data() first.")

        year_data = self.events_data.get(str(year), {})
        return year_data

    def get_data_at_month(self, year: int, month: int):
        """Retrieve events for a specific month and year."""
        if not self.data_loaded:
            raise RuntimeError("Data not loaded. Call validate_and_load_data() first.")

        year_data = self.get_data_at_year(year)
        if not year_data:
            print(f"No data for year: {year}")
            return {}
        month_data = year_data.get(str(month).zfill(2), {})
        return month_data

    def get_data_at_day(self, year: int, month: int, day: int):
        """Retrieve events for a specific day, month, and year."""
        if not self.data_loaded:
            raise RuntimeError("Data not loaded. Call validate_and_load_data() first.")

        month_data = self.get_data_at_month(year, month)
        if not month_data:
            print(f"No data for month: {month} in year: {year}")
            return {}
        day_data = month_data.get(str(day).zfill(2), [])
        return day_data