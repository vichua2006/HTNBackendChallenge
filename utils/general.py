import datetime


def get_utc_now() -> str:
    """Return the current time in UTC format (without "+00:00" at the end)."""
    return datetime.datetime.now(datetime.UTC).isoformat()[:-6]


def to_int(value) -> int | None:
    """Converts a string to an integer, or returns None if the conversion fails."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# following JSend specifications: https://github.com/omniti-labs/jsend
def format_json_success(data) -> dict:
    """Standardizes the format of the JSON response for success"""
    return {"status": "success", "data": data}


def format_json_error(message) -> dict:
    """Standardizes the format of the JSON response for errors"""
    return {"status": "error", "message": message}
