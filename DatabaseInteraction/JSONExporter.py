import sqlite3
import os
import DatabaseInteraction


def main():
    baseDir = os.getcwd()
    dbName = "bookingSystem.db"
    dbPath = os.path.join(baseDir, dbName)

    try:
        conn = sqlite3.connect(dbPath)
        conn.execute("PRAGMA foreign_keys = ON")  # enforce FK constraints
        cur = conn.cursor()
        print("\nConnected successfully!\n")
    except sqlite3.Error as e:
        print("Failed to connect:", e)
        return

    outputPath = os.path.join(baseDir, "events.json")
    DatabaseInteraction.exportToJSON(cur, outputPath)

    conn.close()


if __name__ == "__main__":
    main()