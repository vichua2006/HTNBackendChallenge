import datetime


def get_utc_now() -> str:
    """Return the current time in UTC format (without "+00:00" at the end)."""
    return datetime.datetime.now(datetime.UTC).isoformat()[:-6]


# following JSend specifications: https://github.com/omniti-labs/jsend
def format_json_success(data) -> dict:
    return {"status": "success", "data": data}


def format_json_error(message) -> dict:
    return {"status": "error", "message": message}
