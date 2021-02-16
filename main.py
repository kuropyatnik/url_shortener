import json
from flask import (
    Flask,
    request,
    jsonify,
)
from werkzeug.exceptions import InternalServerError

from helpers.db_connector import create_db_connection
from helpers.decorators import create_fields_validation
from helpers.exceptions import RequestFieldException

app = Flask(__name__)
db = create_db_connection()

INTERNAL_ERROR = {'status': 'error', 'msg': 'Internal server error'}


@app.route('/')
def hello_world():
    return f'Your db url is {db.url}'

@app.route('/create', methods=['POST'])
@create_fields_validation
def create_short_link():
    return "HELLO, GUY FROM POST", 201


@app.errorhandler(InternalServerError)
def handle_internal_error(error):
    return jsonify(INTERNAL_ERROR), 500


@app.errorhandler(RequestFieldException)
def handle_request_fields_error(error):
    return jsonify({"status": "error", "msg": error.message}), 400

if __name__ == "__main__":
    app.run()