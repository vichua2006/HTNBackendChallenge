# following JSend specifications: https://github.com/omniti-labs/jsend
def format_json_success(data) -> dict:
    """Standardizes the format of the JSON response for success"""
    return {"status": "success", "data": data}


def format_json_error(message) -> dict:
    """Standardizes the format of the JSON response for errors"""
    return {"status": "error", "message": message}
