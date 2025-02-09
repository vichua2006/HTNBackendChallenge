# HTNBackendChallenge

## Overview

Sample server created for the Hack the North 2025 Backend Challenge!!!
The server is built with Python [Flask](https://flask.palletsprojects.com/en/stable/) and [sqlite](https://www.sqlite.org/), and follows (to the best of my abilities) REST API principles. It provides several endpoints to see modify the provided hacker and scanning data.

## Setup Instructions

Ensure you have a recent version of **Python** and **pip** installed.
Clone this repository and install Python dependencies:

```bash
git clone https://github.com/vichua2006/HTNBackendChallenge.git
cd HTNBackendChallenge
pip install -r requirements.txt
```

To run the server, navigate to the root directory and run:

```bash
flask run
```

By default the server runs in `http://localhost:5000/`. The first time the server is ran, a file `hackers.db` will be created and populated with the provided sample data in `/data/example_hacker_data.json`

## Database Schema

- The following is the schema of the database, containing the information of hackers and their scanned activities.
- It is a typical one-to-many relationship database; each hacker can have multiple scans, and each scan is linked to exactly one hacker via their `badge_code`.
- Hackers' `badge_code` is used as the identifier for API endpoints and the `FOREIGN KEY` for the `scan` table, but not as `hacker` table's `PRIMARY KEY`, as they can be `NULL` (for hackers not checked in) and potentially subject to change.
- An endpoint is provided to list all hackers who have not checked in, but no support is provided beyond that as they do not provide much data value.

#### Assumptions

- All emails, phone numbers, and names are non-empty (tested)

### Hackers Table

Stores information about participants (hackers).

| Column     | Type    | SQLite Constraints         | Description                       |
| ---------- | ------- | -------------------------- | --------------------------------- |
| hacker_id  | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each hacker |
| badge_code | TEXT    | UNIQUE                     | Unique badge code (can be `NULL`) |
| name       | TEXT    | NOT NULL                   | Full name of the hacker           |
| email      | TEXT    | NOT NULL                   | Hacker's email address            |
| phone      | TEXT    | NOT NULL                   | Contact phone number              |
| updated_at | TEXT    | NOT NULL                   | Last update timestamp             |

---

### Scans Table

Tracks hacker activity scans.

| Column            | Type    | SQL Constraints                            | Description                         |
| ----------------- | ------- | ------------------------------------------ | ----------------------------------- |
| scan_id           | INTEGER | PRIMARY KEY, AUTOINCREMENT                 | Unique scan ID                      |
| activity_name     | TEXT    | NOT NULL                                   | Name of the scanned activity        |
| activity_category | TEXT    | NOT NULL                                   | Category of the activity            |
| scanned_at        | TEXT    | NOT NULL                                   | Timestamp when activity was scanned |
| hacker_badge      | TEXT    | NOT NULL, FOREIGN KEY (hackers.badge_code) | Links to the hacker via badge code  |

---

### **Relationships**

- **`scans.hacker_badge` → `hackers.badge_code`**
  - Each scan **must** be linked to a hacker (badge code).
  - A hacker **can have multiple** scans.

## Endpoints

All responses follow [Jsend](https://github.com/omniti-labs/jsend) specifications.

### GET `/users`

#### **Description:**

Returns a list of all hackers in JSON format.

#### Response Format:

```json
{
  "status": "string",
  "data": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "badge_code": "string",
    "scans": [
      {
        "activity_name": "string",
        "activity_category": "string",
        "scanned_at": "string"
      }
    ]
  }
}
```

---

### GET/PUT `/users/<badge_code>`

#### **Description:**

- **`GET`**: Fetch user details by `badge_code`.
- **`PUT`**: Update user information. Scans cannot be updated.

#### Sample PUT Request Body:

```json
{
  "name": "Alice Johnson",
  "email": "alice.j@example.com",
  "phone": "987-654-3210",
  "badge_code": "NEWCODE123"
}
```

#### **Response (200 OK, Success Case):**

```json
{
  "status": "success",
  "data": {
    "name": "Alice Johnson",
    "badge_code": "NEWCODE123",
    "email": "alice.j@example.com",
    "phone": "987-654-3210",
    "updated_at": "2025-02-09T12:45:00Z",
    "scans": []
  }
}
```

---

### GET `/users/not-checked-in`

#### **Description:**

Returns a list of users who have **no badge code** assigned.

#### **Response (200 OK):**

```json
{
  "status": "success",
  "data": [
    {
      "name": "Bob",
      "email": "bob@example.com",
      "badge_code": null,
      "phone": "321-654-9870",
      "updated_at": "2025-02-09T11:00:00Z",
      "scans": []
    }
  ]
}
```

---

### GET `/scans`

#### **Description:**

Returns a list of all scan activities, with optional filters.

#### **Query Parameters (Optional):**

| Parameter           | Type     | Description                 |
| ------------------- | -------- | --------------------------- |
| `min_frequency`     | `int`    | Minimum scan frequency      |
| `max_frequency`     | `int`    | Maximum scan frequency      |
| `activity_category` | `string` | Filter by activity category |

#### **Example Request:**

```http
GET /scans?min_frequency=2&activity_category=workshop
```

#### **Response (200 OK):**

```json
{
  "status": "success",
  "data": [
    {
      "activity_name": "CTF Challenge",
      "activity_category": "workshop",
      "scanned_at": "2025-02-09T12:30:00Z"
    }
  ]
}
```

---

### GET/PUT `/scans/<badge_code>`

#### **Description:**

- **`GET`**: Retrieve all scans for a specific hacker.
- **`PUT`**: Add a new scan for the hacker.

#### **PUT Request Body:**

```json
{
  "activity_name": "Hackathon Finals",
  "activity_category": "competition"
}
```

#### **Response (201 Created, Success Case):**

```json
{
  "status": "success",
  "data": {
    "activity_name": "Hackathon Finals",
    "activity_category": "competition",
    "scanned_at": "2025-02-09T13:00:00Z"
  }
}
```
