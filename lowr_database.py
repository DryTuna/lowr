

import os
import psycopg2
from passlib.hash import pbkdf2_sha256
from contextlib import closing

DB_SCHEMA = """
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    id serial PRIMARY KEY,
    username VARCHAR (127) NOT NULL,
    email VARCHAR (127) NOT NULL,
    password VARCHAR (127) NOT NULL,
    created TIMESTAMP NOT NULL
)
"""

DB_ENTRY_INSERT = """
INSERT INTO accounts (title, text, created) VALUES (%s, %s, %s)
"""

DB_ENTRIES_LIST = """
SELECT id, title, text, created FROM accounts ORDER BY created DESC
"""

DB_ENTRY_LIST = """
SELECT id, title, text, created FROM accounts WHERE accounts.id = %s
"""

DB_DELETE_ENTRY_LIST = """
DELETE FROM accounts WHERE accounts.id = %s
"""

def connect_db():
    """Return a connection to the configured database"""
    return psycopg2.connect(app.config['DATABASE'])

def init_db():
    """Initialize the database using DB_SCHEMA

    WARNING: executing this function will drop existing tables.
    """
    with closing(connect_db()) as db:
        db.cursor().execute(DB_SCHEMA)
        db.commit()


def get_database_connection():
    db = getattr(g, 'db', None)
    if db is None:
        g.db = db = connect_db()
    return db


