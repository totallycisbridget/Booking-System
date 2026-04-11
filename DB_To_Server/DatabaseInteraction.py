import sqlite3
import json
import os


def exportToJSON(cur, outputPath):
    try:
        cur.execute("""
            SELECT
                e.EventName,
                e.Date,
                e.StartTime,
                e.EndTime,
                l.RoomID,
                l.Building,
                l.Campus,
                lec.Name,
                lec.Surname
            FROM event e
            LEFT JOIN location l ON e.RoomID = l.RoomID
            LEFT JOIN lecturer lec ON e.LecturerID = lec.LecturerID
            LEFT JOIN student s ON e.StudentID = s.StudentID
            ORDER BY e.Date, e.StartTime
            """)
    except sqlite3.Error as e:
        print(f"Query failed: {e}")
        return

    rows = cur.fetchall()
    events = {}

    for row in rows:
        event_name, date, start_time, end_time, room_id, building, campus, lec_first_name, lec_surname= row

        try:
            year, month, day = date.split("-")
        except (ValueError, AttributeError):
            print(f"Skipping event '{event_name}' - invalid date: {date}")
            continue

        start_time = str(start_time).strip()
        end_time = str(end_time).strip()

        event_entry = {
            "title": event_name,
            "start_time": start_time,
            "end_time": end_time,
            "room": {
                "roomID": room_id,
                "building": building,
                "campus": campus
            },
            "lecturer": {
                "first_name": lec_first_name,
                "last_name": lec_surname
            }
        }

        events.setdefault(year, {}).setdefault(month, {}).setdefault(day, []).append(event_entry)
    try:
        with open(outputPath, "w") as f:
            json.dump(events, f, indent=4)
        print(f"\nExported {len(rows)} event(s) to '{outputPath}'\n")
    except OSError as e:
        print(f"Failed to write output file: {e}")

    return events