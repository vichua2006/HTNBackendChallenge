import os
import json
import sqlite3
from flask import g
from utils.general import get_utc_now

DATABASE_NAME = "hackers.db"


def create_db(filename: str = "database.db") -> None:
    """Creates a sqlite database and populates it with the data from the local example_hacker_data.json file.
    To be called from the root directory of the project, and
    assumes that there does NOT currenctly exist a database with the name in the root directory.
    """
    sqliteConnection = sqlite3.connect(f"{filename}")
    with open("./data/example_hacker_data.json") as file:
        hackerData = json.load(file)

    cursor = sqliteConnection.cursor()

    # init hacker table
    cursor.execute(
        """CREATE TABLE hackers (
        hacker_id INTEGER PRIMARY KEY AUTOINCREMENT,
        badge_code TEXT UNIQUE,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """
    )

    # init scanned activities table
    cursor.execute(
        """CREATE TABLE scans (
        scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_name TEXT NOT NULL,
        activity_category TEXT NOT NULL,
        scanned_at TEXT NOT NULL,
        hacker_badge TEXT NOT NULL,
        FOREIGN KEY(hacker_badge) REFERENCES hackers(badge_code)
    );
    """
    )

    for hacker in hackerData:
        utcTime = get_utc_now()

        # inserting into the hacker table
        badgeCode = (
            hacker["badge_code"] if hacker["badge_code"] else None
        )  # to acccount for hackers who have not checked in; their badge_code will be NULL
        data = (badgeCode, hacker["name"], hacker["email"], hacker["phone"], utcTime)
        command = """INSERT INTO hackers (badge_code, name, email, phone, updated_at) VALUES (?, ?, ?, ?, ?);"""
        cursor.execute(command, data)

        for activity in hacker["scans"]:
            # inserting into the scans table
            activityData = (
                activity["activity_name"],
                activity["activity_category"],
                activity["scanned_at"],
                hacker["badge_code"],
            )
            command = """INSERT INTO scans (activity_name, activity_category, scanned_at, hacker_badge) VALUES (?, ?, ?, ?);"""
            cursor.execute(command, activityData)

    sqliteConnection.commit()
    cursor.close()
    sqliteConnection.close()


def get_db() -> sqlite3.Connection:
    """Returns a connection to the database. If the db file does not exist, it will be created"""
    db = getattr(g, "_database", None)
    if db is None:
        if not os.path.exists(DATABASE_NAME):
            create_db(DATABASE_NAME)
        g._database = sqlite3.connect(DATABASE_NAME)
    return g._database


def get_user_scans(badge_code: str) -> list[dict[str, str]]:
    """Returns a list of all the scans for a user with the given badge code"""
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM scans WHERE hacker_badge = ?", (badge_code,))
    scans = cursor.fetchall()

    scans_list = [
        {"activity_name": scan[1], "activity_category": scan[2], "scanned_at": scan[3]}
        for scan in scans
    ]

    return scans_list


def change_scan_badge_code(old_code: str, new_code: str) -> None:
    """Change the badge code for all scans with the old badge code to the new badge code"""
    cursor = get_db().cursor()
    cursor.execute(
        "UPDATE scans SET hacker_badge = ? WHERE hacker_badge = ?", (new_code, old_code)
    )
    get_db().commit()


def construct_user_json(user_row: sqlite3.Row):
    """Constructs a JSON object for a user from a row in the hackers table"""
    user_json = {
        "name": user_row[2],
        "badge_code": user_row[1],
        "email": user_row[3],
        "phone": user_row[4],
        "updated_at": user_row[5],
    }

    user_json["scans"] = get_user_scans(user_row[1])

    return user_json


def filter_scans(
    min_frequency: int = None, max_frequency: int = None, activity_category: str = None
) -> list[dict[str, str]]:
    """Return a list of all the scans from the database in a JSON format, with optional filters for the minimum and maximum frequency and activity category.
    for additional filter options, consider refactoring options into individual functions that applies a filter the scans list efficiently
    """

    # filter category through sqlite query
    cursor = get_db().cursor()
    if activity_category:
        cursor.execute(
            "SELECT * FROM scans WHERE activity_category = ?", (activity_category,)
        )
    else:
        cursor.execute("SELECT * FROM scans")

    # filter min, max (and potentially other values and complicated combinations) directly in Python
    scans = cursor.fetchall()
    activity_frequency = {}
    for scan in scans:
        activity_name = scan[1]
        if not activity_frequency.get(activity_name):
            activity_frequency[activity_name] = 0
        activity_frequency[activity_name] += 1

    scans_list_json = []
    for name in activity_frequency:
        if min_frequency and activity_frequency[name] < min_frequency:
            continue
        if max_frequency and activity_frequency[name] > max_frequency:
            continue

        scans_list_json.append(
            {
                "activity_name": name,
                "frequency": activity_frequency[name],
            }
        )

    return scans_list_json
