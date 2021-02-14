from flask import Flask
from helpers.db_connector import create_db_connection


app = Flask(__name__)
db = create_db_connection()


@app.route('/')
def hello_world():
    return f'Your db url is {db.url}'


if __name__ == "__main__":
    app.run()