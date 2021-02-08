from flask import Flask
from consts import DB_HOST, DB_NAME

app = Flask(__name__)

@app.route('/')
def hello_world():
    return f'Your db_host is {DB_HOST}, and db_name: {DB_NAME}'

if __name__ == "__main__":
    app.run()