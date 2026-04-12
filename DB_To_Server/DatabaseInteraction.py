import sqlite3
import json
import os


def exportToJSON(cur, outputPath):
    try:
        cur.execute("""
            SELECT
                e.EventName,
                e.Date,
                COALESCE(e.StartTime, SUBSTR(e.Time, 1, INSTR(e.Time, '-') - 1)),
                COALESCE(e.EndTime,   SUBSTR(e.Time, INSTR(e.Time, '-') + 1)),
                e.RoomID,
                lec.Name,
                lec.Surname
            FROM event e
            LEFT JOIN lecturer lec ON e.LecturerID = lec.LecturerID
            LEFT JOIN student s ON e.StudentID = s.StudentID
            ORDER BY e.Date, e.Time
            """)
    except sqlite3.Error as e:
        print(f"Query failed: {e}")
        return

    rows = cur.fetchall()
    events = {}

    for row in rows:
        event_name, date, start_time, end_time, room_id, lec_first_name, lec_surname = row

        try:
            year, month, day = date.split("-")
        except (ValueError, AttributeError):
            print(f"Skipping event '{event_name}' - invalid date: {date}")
            continue

        start_time = str(start_time).strip() if start_time else ""
        end_time = str(end_time).strip() if end_time else ""

        event_entry = {
            "title": event_name,
            "start_time": start_time,
            "end_time": end_time,
            "room": {
                "roomID": room_id
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


def getStaffAvailability(cur, lecturer_id):
    # Fetch lecturer info
    try:
        cur.execute("""
            SELECT Name, Surname FROM lecturer WHERE LecturerID = ?
        """, (lecturer_id,))
    except sqlite3.Error as e:
        print(f"Query failed: {e}")
        return None

    lecturer = cur.fetchone()
    if not lecturer:
        return {"error": f"Lecturer with ID {lecturer_id} not found"}

    lec_name, lec_surname = lecturer

    # Fetch recurring availability windows
    try:
        cur.execute("""
            SELECT DayOfWeek, StartTime, EndTime
            FROM lecturer_availability
            WHERE LecturerID = ?
            ORDER BY CASE DayOfWeek
                WHEN 'Monday'    THEN 1
                WHEN 'Tuesday'   THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday'  THEN 4
                WHEN 'Friday'    THEN 5
            END
        """, (lecturer_id,))
    except sqlite3.Error as e:
        print(f"Query failed: {e}")
        return None

    availability_rows = cur.fetchall()

    # Fetch existing bookings for this lecturer (day-of-week + time)
    try:
        cur.execute("""
            SELECT
                CASE CAST(strftime('%w', Date) AS INTEGER)
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                END AS DayOfWeek,
                StartTime,
                EndTime,
                EventName,
                Date
            FROM event
            WHERE LecturerID = ?
            ORDER BY Date, StartTime
        """, (lecturer_id,))
    except sqlite3.Error as e:
        print(f"Query failed: {e}")
        return None

    bookings = cur.fetchall()

    # Group bookings by day-of-week for easy lookup
    booked_by_day = {}
    for day, start, end, name, date in bookings:
        booked_by_day.setdefault(day, []).append({
            "event": name,
            "date": date,
            "start_time": start,
            "end_time": end
        })

    # Build availability response with booked slots noted
    schedule = {}
    for day, start, end in availability_rows:
        schedule.setdefault(day, {
            "available_window": {"start": start, "end": end},
            "booked_slots": []
        })
        schedule[day]["booked_slots"] = booked_by_day.get(day, [])

    return {
        "lecturer_id": lecturer_id,
        "name": f"{lec_name} {lec_surname}",
        "availability": schedule
    }


def bookTimeSlot(cur, conn, lecturer_id, day, start_time, end_time):
    # Validate lecturer exists
    try:
        cur.execute("SELECT Name, Surname FROM lecturer WHERE LecturerID = ?", (lecturer_id,))
    except sqlite3.Error as e:
        print(f"Query failed: {e}")
        return False

    lecturer = cur.fetchone()
    if not lecturer:
        print(f"Lecturer ID {lecturer_id} not found.")
        return False

    # Check lecturer has availability on this day of week
    try:
        cur.execute("""
            SELECT StartTime, EndTime FROM lecturer_availability
            WHERE LecturerID = ? AND DayOfWeek = ?
        """, (lecturer_id, day))
    except sqlite3.Error as e:
        print(f"Query failed: {e}")
        return False

    availability = cur.fetchone()
    if not availability:
        print(f"Lecturer has no availability on {day}.")
        return False

    avail_start, avail_end = availability

    # Validate requested slot fits within availability window
    if start_time < avail_start or end_time > avail_end or start_time >= end_time:
        print(f"Requested slot {start_time}-{end_time} is outside availability {avail_start}-{avail_end}.")
        return False

    # Check for conflicts with existing bookings on the same day-of-week
    # We check against events whose Date falls on the requested DayOfWeek
    try:
        cur.execute("""
            SELECT EventID, StartTime, EndTime, EventName FROM event
            WHERE LecturerID = ?
            AND CASE CAST(strftime('%w', Date) AS INTEGER)
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                END = ?
            AND StartTime < ? AND EndTime > ?
        """, (lecturer_id, day, end_time, start_time))
    except sqlite3.Error as e:
        print(f"Conflict check failed: {e}")
        return False

    conflicts = cur.fetchall()
    if conflicts:
        for c in conflicts:
            print(f"Booking conflict with event '{c[3]}' ({c[1]}-{c[2]})")
        return False

    # Insert the new booking event
    # Use the next upcoming date matching the requested day of week
    try:
        cur.execute("""
            SELECT date('now', 'weekday ' ||
                CASE ?
                    WHEN 'Monday'    THEN '1'
                    WHEN 'Tuesday'   THEN '2'
                    WHEN 'Wednesday' THEN '3'
                    WHEN 'Thursday'  THEN '4'
                    WHEN 'Friday'    THEN '5'
                END
            )
        """, (day,))
        next_date = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO event (EventName, Date, StartTime, EndTime, LecturerID)
            VALUES (?, ?, ?, ?, ?)
        """, (f"Booking - {lecturer[0]} {lecturer[1]}", next_date, start_time, end_time, lecturer_id))

        conn.commit()
        print(f"Booking created for {day} {start_time}-{end_time} (date: {next_date})")
        return True

    except sqlite3.Error as e:
        print(f"Insert failed: {e}")
        conn.rollback()
        return False
