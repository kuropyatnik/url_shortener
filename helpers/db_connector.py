from sqlalchemy import (
    MetaData,
    create_engine,
    engine,
    Table,
    Column,
    Integer,
    String,
    DateTime
) 
from sqlalchemy_utils import create_database, database_exists
from .consts import (
    DB_HOST,
    DB_NAME,
    DB_USERNAME,
    DB_PASSWD,
    TABLE_NAME
)


def create_db_connection() -> engine.Engine:
    """
    Creates DB connection via pymysql dialect.
    Also, ensures that expected DB exists, 
    and if it's not, creates a new one
    """
    engine = create_engine(
        f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWD}@{DB_HOST}/{DB_NAME}"
    )
    # Initial create of database (if needed)
    if not database_exists(engine.url):
        create_database(engine.url)
    
    # Initial create of table (if needed)
    if not engine.dialect.has_table(engine, TABLE_NAME):
        meta = MetaData()
        table = Table(
            TABLE_NAME,
            meta,
            Column("id", Integer, primary_key=True),
            Column("real_url", String(1000), unique=True),
            Column("short_url", String(200), unique=True),
            Column("valid_to", DateTime)
        )
        meta.create_all(engine)

    return engine
