import json
import time
import os
from datetime import datetime
from flask import (
    Flask,
    request,
    jsonify,
)
from werkzeug.exceptions import InternalServerError
from sqlalchemy.exc import IntegrityError

from helpers.db_connector import create_db_connection
from helpers.api import validate_fields, encrypt_url, process_expiration_date
from helpers.exceptions import RequestFieldException
from helpers.consts import MAX_RECORDS

app = Flask(__name__)
db, table = create_db_connection()

INTERNAL_ERROR = {'status': 'error', 'msg': 'Internal server error'}
HASH_WAS_NOT_FOUND_ERROR = {
    'status': 'error',
    'msg': 'Currently such URL is impossible to be shortened. The reason: ' \
            'DB has all possible combinations of shorts. You can try ' \
            'again, this error should be disappear.'
}

@app.route('/')
def hello_world():
    return f'Your db url is {db.url}'

@app.route('/create_url', methods=['POST'])
@validate_fields
def create_short_link():
    """
    Makes a new short key from long url and timestamp
    Tries to insert new data to the DB
    """
    ts = time.time()
    with db.connect() as conn:
        # Cleanup from all old records
        conn.execute(
            table.delete().where(table.c.valid_to < datetime.fromtimestamp(ts))
        )

        # Try to find already existing real url in DB
        res = conn.execute(
            table.select().where(table.c.real_url == request.json["url"])
        )
        if res.rowcount > 0:
            full_short_url = os.path.join(
                request.url_root, res.first().short_url)
            return jsonify(
                {
                    "status": "ok",
                    "msg": f"This url is already here. Visit: {full_short_url}"
                }
            ), 200
        
        # Count all records in the DB
        res = conn.execute(
            table.select()
        )
        if res.rowcount >= MAX_RECORDS:
            return jsonify(
                {
                    "status": "error",
                    "msg": f"There is maximum amount of possible records!"
                }
            ), 409


        res_encr = encrypt_url(request.json["url"], ts)
        valid_to = process_expiration_date(ts, request.json.get("lifeterm", 90))
        # Try to insert new row
        for i in range(0, len(res_encr) - 5):
            try:
                conn.execute(
                    table.insert(),
                    {
                        "real_url": request.json["url"],
                        "short_url": res_encr[i:i+6],
                        "valid_to": valid_to
                    }
                )
                full_short_url = os.path.join(request.url_root, res_encr[i:i+6])
                return jsonify(
                    {
                        "status": "ok",
                        "msg": f"URL was shorted! Visit: {full_short_url}"
                    }
                ), 201
            except IntegrityError:
                # This error is possible only if hash exists in DB, 
                # so we just try to shift to the next 6 symbols in hash
                continue
        # if there was no break, than unique hash wasn't found
        return jsonify(HASH_WAS_NOT_FOUND_ERROR), 500


@app.errorhandler(InternalServerError)
def handle_internal_error(error):
    return jsonify(INTERNAL_ERROR), 500


@app.errorhandler(RequestFieldException)
def handle_request_fields_error(error):
    return jsonify({"status": "error", "msg": error.message}), 400

if __name__ == "__main__":
    app.run()