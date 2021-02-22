import re
import hashlib
import sqlalchemy
import time
from functools import wraps
from flask import Response, request, make_response
from datetime import datetime, timedelta

from .exceptions import RequestFieldException
from .consts import MAX_RECORDS


url_regex = re.compile(r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def validate_fields(f):
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


def cleanup(db: sqlalchemy.engine.Engine, table: sqlalchemy.Table):
    """
    Cronjob, which clears DB from old records
    """
    ts = time.time()
    with db.connect() as conn:
        # Cleanup from all old records
        conn.execute(table.delete().where(
            table.c.valid_to < datetime.fromtimestamp(ts))
        )
    print("Cleanup is finished!")


def is_max_rowscount(
        db: sqlalchemy.engine.Engine, 
        table: sqlalchemy.Table,
        pre_cleanup: bool = False
    ):
    """
    Checks for current table rows count with possible pre-delete
    """
    # Count all records in the DB
    with db.connect() as conn:
        if pre_cleanup:
            cleanup(db, table)

        res = conn.execute(
            sqlalchemy.func.count(table.c.id)
        )
    return res.rowcount >= MAX_RECORDS



def encrypt_url(long_url: str, ts: datetime.timestamp) -> str:
    """
    Uses md5 to encrypt combination of long url and request timestamp
    """
    encoded_data = str.encode(long_url + str(ts), "utf-8")
    return hashlib.md5(encoded_data).hexdigest()


def process_expiration_date(current_ts: datetime.timestamp, days: int) -> datetime:
    """
    Create expiration date by adding days number to current date
    """
    return datetime.fromtimestamp(current_ts) + timedelta(days)
