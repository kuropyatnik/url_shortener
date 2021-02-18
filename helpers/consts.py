import os
from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWD = os.getenv("DB_PASSWD")
DB_NAME = os.getenv("DB_NAME")

TABLE_NAME = "links"
MAX_RECORDS = 1000000