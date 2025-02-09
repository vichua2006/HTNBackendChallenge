import os
import sqlite3
import json
from utils.load_db import create_db
from flask import Flask, g

app = Flask(__name__)
DATABASE = "hackers.db"

@app.route("/users", methods=["GET"])
def all_users():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM hackers")
    users = cursor.fetchall()

    user_list = []
    for user in users:
        user_json = {
            "name": user[2],
            "badge_code": user[1],
            "email": user[3],
            "phone": user[4],
            "updated_at": user[5]
        }
        cursor.execute("SELECT * FROM scans WHERE hacker_badge = ?", (user[1],)) 
        activities = cursor.fetchall()
        activity_list = [{
            "activity_name": act[1],
            "activity_category": act[2],
            "scanned_at": act[3]
        } for act in activities]

        user_json["scans"] = activity_list

        user_list.append(user_json)
        
    return user_list


@app.teardown_appcontext
def close_connection(exception) -> None:
    '''Closes the connection to the database'''
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_db():
    '''Returns a connection to the database. If the db file does not exist, it will be created'''
    db = getattr(g, '_database', None)
    if db is None:
        if (not os.path.exists(DATABASE)):
            create_db()
        g._database = sqlite3.connect(DATABASE)
    return g._database