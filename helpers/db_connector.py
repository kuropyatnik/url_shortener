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
from typing import Tuple
from random import randint

from .consts import (
    DB_HOST,
    DB_NAME,
    DB_USERNAME,
    DB_PASSWD,
    TABLE_NAME
)


def create_db_connection() -> Tuple[engine.Engine, Table]:
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
    
    meta = MetaData(engine)
    # Initial create of table (if needed)
    if not engine.dialect.has_table(engine, TABLE_NAME):
        table = Table(
            TABLE_NAME,
            meta,
            Column("id", Integer, primary_key=True),
            Column("real_url", String(1000), unique=True),
            Column("short_url", String(200), unique=True),
            Column("valid_to", DateTime)
        )
        meta.create_all(engine)
    else:
        meta.reflect(only=[TABLE_NAME])
        table = meta.tables[TABLE_NAME]

    return engine, table


def create_test_table(engine: engine.Engine, real_table: Table) -> Table:
    """
    Creates a testing table with a real table schema
    """
    meta = MetaData(engine)
    # Test copy of main table schema
    new_table = Table("test" + str(randint(1, 50)), meta)
    for column in real_table.columns:
        new_table.append_column(column.copy())
    meta.create_all(engine)
    return new_table
