
import http.server
import json
import os
from urllib.parse import urlparse, parse_qs
import DatabaseInteraction
import sqlite3

#database stuff
def getConnection():
    baseDir = os.getcwd()
    dbPath = os.path.join(baseDir, "bookingSystem.db")
    try:
        conn = sqlite3.connect(dbPath)
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        print("\nConnected successfully!\n")
        return conn, cur
    except sqlite3.Error as e:
        print("Failed to connect:", e)
        return None, None

def eventsHandler():
    conn, cur = getConnection()
    if not conn:
        return None
    outputPath = os.path.join(os.getcwd(), "events.json")
    calendar_data = DatabaseInteraction.exportToJSON(cur, outputPath)
    conn.close()
    return calendar_data

def availabilityHandler(lecturer_id):
    conn, cur = getConnection()
    if not conn:
        return None
    result = DatabaseInteraction.getStaffAvailability(cur, lecturer_id)
    conn.close()
    return result

def bookingHandler(lecturer_id, day, start_time, end_time):
    conn, cur = getConnection()
    if not conn:
        return False
    success = DatabaseInteraction.bookTimeSlot(cur, conn, lecturer_id, day, start_time, end_time)
    conn.close()
    return success

# -------------------------
# HELPER FUNCTION
# -------------------------
def send_json(handler, data):
    handler.send_response(200)
    handler.send_header("Content-type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode())

# -------------------------
# REQUEST HANDLER
# -------------------------
class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        # -------------------------
        # 1. GET USER CALENDAR
        # -------------------------
        if path == "/api/v1/getUserCalendar":
            # (ignoring date filtering for now)
            calendar_data = eventsHandler()
            send_json(self, calendar_data)

        # -------------------------
        # 2. GET STAFF AVAILABILITY
        # -------------------------

        # Uses format /api/v1/getStaffAvailableTime?staffID=[staffID]
        elif path == "/api/v1/getStaffAvailableTime":
            staff_id = int(query.get("staffID", [None])[0])
            response = availabilityHandler(staff_id)
            send_json(self, response)

        # -------------------------
        # 3. BOOK TIME SLOT
        # -------------------------

        # Uses format /api/v1/bookTimeSlot?staffID=[staffID]&bookDay=[Monday]&bookStart=[HH:MM]&bookEnd=[HH:MM]
        elif path == "/api/v1/bookTimeSlot":
            staff_id  = int(query.get("staffID",   [None])[0])
            day       = query.get("bookDay",    [None])[0]
            start     = query.get("bookStart",  [None])[0]
            end       = query.get("bookEnd",    [None])[0]
            success = False
            if staff_id and day and start and end:
                success = bookingHandler(staff_id, day, start, end)
            send_json(self, {"success": success})

        # -------------------------
        # UNKNOWN ROUTE
        # -------------------------
        else:
            handler_response = {"error": "Endpoint not found"}
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(handler_response).encode())

# -------------------------
# RUN SERVER
# -------------------------
def run():
    port = 8000
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Server running on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
