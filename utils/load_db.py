import sqlite3
import json
import datetime

def create_db(filename: str = "hackers") -> None:
    '''Creates a sqlite database and populates it with the data from the example_hacker_data.json file.
    Assumes that there does NOT currenctly exist a database with the name hackers.db in root directory '''
    sqliteConnection = sqlite3.connect(f"../{filename}.db")
    with open("../data/example_hacker_data.json") as file:
        hackerData = json.load(file)

    cursor = sqliteConnection.cursor()

    # init hacker table
    cursor.execute('''CREATE TABLE hackers (
        hacker_id INTEGER PRIMARY KEY AUTOINCREMENT,
        badge_code TEXT UNIQUE,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    ''')

    # init scanned activities table
    cursor.execute('''CREATE TABLE scans (
        scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_name TEXT NOT NULL,
        activity_category TEXT NOT NULL,
        scanned_at TEXT NOT NULL,
        hacker_badge TEXT NOT NULL,
        FOREIGN KEY(hacker_badge) REFERENCES hackers(badge_code)
    );
    ''')

    for hacker in hackerData:
        # get the current time in UTC (without +00:00, same format as the provided json)
        utcTime = datetime.datetime.now(datetime.UTC).isoformat()[:-6]
        # inserting into the hacker table
        badgeCode = hacker["badge_code"] if hacker["badge_code"] else None # to acccount for hackers who have not checked in; their badge_code will be NULL
        data = (badgeCode, hacker["name"], hacker["email"], hacker["phone"], utcTime)
        command = '''INSERT INTO hackers (badge_code, name, email, phone, updated_at) VALUES (?, ?, ?, ?, ?);'''
        cursor.execute(command, data)
        for activity in hacker["scans"]:
            # inserting into the scans table
            activityData = (activity["activity_name"], activity["activity_category"], activity["scanned_at"], hacker["badge_code"])
            command = '''INSERT INTO scans (activity_name, activity_category, scanned_at, hacker_badge) VALUES (?, ?, ?, ?);'''
            cursor.execute(command, activityData)

    sqliteConnection.commit()
    cursor.close()
    sqliteConnection.close()


if __name__ == "__main__":
    create_db()