import os
import sqlite3
from utils.create_db import create_db
from utils.general import get_utc_now, format_json_success, format_json_error, to_int
from flask import Flask, g, request

app = Flask(__name__)
DATABASE_NAME = "hackers.db"


@app.route("/users", methods=["GET"])
def all_users():
    """Return a list of all the user data from the database in a JSON format."""
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM hackers")
    users = cursor.fetchall()

    user_list = [construct_user_json(user) for user in users]

    return format_json_success(user_list)


@app.route("/users/<badge_code>", methods=["GET", "PUT"])
def user_information(badge_code):
    """Return the user data for the user with the given badge code in a JSON format, or update the user data if a PUT request is made"""
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM hackers WHERE badge_code = ?", (badge_code,))

    user = cursor.fetchone()
    if not user:
        return format_json_error("User not found")

    if request.method == "GET":
        user_json = construct_user_json(user)
        return format_json_success(user_json)
    else:
        updates = request.json
        if not updates:
            return format_json_error("Invalid update: no data provided")

        # strict check for unexpected fields
        expected_fields = {"name", "email", "phone", "badge_code"}
        extra_fields = set(updates.keys()) - expected_fields
        if extra_fields:
            return format_json_error(f"Unexpected fields: {', '.join(extra_fields)}")

        # update the user data;
        old_badge_code = user[1]
        name = updates.get("name", user[2])
        email = updates.get("email", user[3])
        phone = updates.get("phone", user[4])
        new_badge_code = updates.get("badge_code", old_badge_code)
        updated_at = get_utc_now()

        cursor.execute(
            """UPDATE hackers
            SET name = ?, email = ?, phone = ?, updated_at = ?, badge_code = ?
            WHERE badge_code = ?""",
            (name, email, phone, updated_at, new_badge_code, old_badge_code),
        )
        get_db().commit()

        # Check if the badge code was actually updated and update the corresponding entires in the scans table
        if new_badge_code != old_badge_code:
            change_scan_badge_code(old_badge_code, new_badge_code)

        # Construct and return the updated user data
        new_user_json = {
            "name": name,
            "badge_code": new_badge_code,
            "email": email,
            "phone": phone,
            "updated_at": updated_at,
            "scans": get_user_scans(new_badge_code),
        }
        return format_json_success(new_user_json)


@app.route("/users/not-checked-in", methods=["GET"])
def not_checked_in():
    """Return a list of all the users who have not checked in (no badge_code), in a JSON format."""
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM hackers WHERE badge_code IS NULL")
    users = cursor.fetchall()
    users_list = [construct_user_json(user) for user in users]

    return users_list


@app.route("/scans", methods=["GET"])
def scan_data():
    """Return a list of all the scans from the database in a JSON format, with optional filters for the minimum and maximum frequency and activity category."""
    # strict check for unexpected query parameters
    params = request.args
    expected_fields = {"min_frequency", "max_frequency", "activity_category"}
    extra_fields = set(params.keys()) - expected_fields
    if extra_fields:
        return format_json_error(f"Unexpected parameters: {', '.join(extra_fields)}")

    min_frequency = params.get("min_frequency")
    max_frequency = params.get("max_frequency")
    activity_category = params.get("activity_category")
    filtered_list = filter_scans(
        to_int(min_frequency), to_int(max_frequency), activity_category
    )

    return format_json_success(filtered_list)


@app.route("/scans/<badge_code>", methods=["GET", "PUT"])
def user_scans(badge_code):
    cursor = get_db().cursor()

    cursor.execute("SELECT * FROM hackers WHERE badge_code = ?", (badge_code,))
    user = cursor.fetchone()
    if not user:
        return format_json_error("Invalid update: User not found")

    if request.method == "GET":
        scans = get_user_scans(badge_code)
        return format_json_success(scans)
    else:
        scan = request.json
        if not scan:
            return format_json_error("Invalid scan: no data provided")

        expected_fields = {"activity_name", "activity_category"}
        extra_fields = set(scan.keys()) - expected_fields
        if extra_fields:
            return format_json_error(f"Unexpected fields: {', '.join(extra_fields)}")

        activity_name = scan.get("activity_name")
        activity_category = scan.get("activity_category")
        scanned_at = get_utc_now()
        if not activity_name or not activity_category:
            return format_json_error("Invalid scan: missing data")

        cursor.execute(
            """INSERT INTO scans (activity_name, activity_category, scanned_at, hacker_badge)
            VALUES (?, ?, ?, ?)""",
            (activity_name, activity_category, scanned_at, badge_code),
        )
        # update corresponding user's updated_at field
        cursor.execute(
            """
            UPDATE hackers
            SET updated_at = ?
            WHERE badge_code = ?
            """,
            (scanned_at, badge_code),
        )

        get_db().commit()

        # Construct and return new scan
        scan_json = {
            "activity_name": activity_name,
            "activity_category": activity_category,
            "scanned_at": scanned_at,
            "badge_code": badge_code,
        }

        return format_json_success(scan_json)


@app.teardown_appcontext
def close_connection(exception):
    """Closes the connection to the database"""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


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
