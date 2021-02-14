from functools import wraps
from flask import Response, request, make_response
import re
from .exceptions import RequestFieldException


url_regex = re.compile(r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def create_fields_validation(f):
    """
    Decorator to validate `/create` request POST fields

    There must be an `url` field, non-empty and URL-validated
    There can be a `lifeterm` field, integer and in range [1, 365]
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # non-JSON requests
        if not request.json:
            raise RequestFieldException("Request body isn't JSON!")
        # Absent request fields
        if "url" not in request.json:
            raise RequestFieldException("Request has not all required fields!")
        # Empty request `url` field
        if str.strip(request.json["url"]) == "":
            raise RequestFieldException("URL field is empty!")
        # Non-valid url
        if re.match(url_regex, request.json["url"]) is None:
            raise RequestFieldException("URL isn't valid!")

        # If there was provided `lifeterm` value
        if "lifeterm" in request.json:
            # Non-int `lifeterm` field
            if not isinstance(request.json["lifeterm"], int):
                raise RequestFieldException("Lifeterm isn't integer!")
            if request.json["lifeterm"] < 1 or request.json["lifeterm"] > 365:
                raise RequestFieldException("Lifeterm has to be in range [1, 365] days!")
        return f(*args, **kwargs)
    return decorated_function