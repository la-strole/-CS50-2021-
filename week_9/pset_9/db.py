import sqlite3
import os
from flask import Flask
from helpers import take_symbols


def get_db(app):
    """
    Return database connection to from app.config[DATABASE_URI]
    if database not exist - create db in root directory with /schema.sql
    """
    assert isinstance(app, Flask)

    if not os.path.isfile(app.root_path + '/' + app.config.get("DATABASE_URI")):
        print(f'DB {app.config.get("DATABASE_URI")} not exist. Create it.')
        return create_db(app, app.config.get("DATABASE_URI"))
    db = sqlite3.connect(app.root_path + '/' + app.config.get("DATABASE_URI"),
                         detect_types=sqlite3.PARSE_DECLTYPES, timeout=10)
    db.row_factory = sqlite3.Row

    return db


def create_db(app, name='finance.db'):
    """
    Create db in root directory with name = name.
    return db as connection to db
    app - flask app to get path
    """
    assert isinstance(app, Flask)
    if os.path.isfile(app.root_path + '/' + name):
        raise RuntimeError(f"file with db {name} already exist")
    else:
        with app.open_resource('schema.sql') as f:
            con = sqlite3.connect(app.root_path + '/' + name)
            con.executescript(f.read().decode('utf8'))
            con.commit()
        db = con
        db.row_factory = sqlite3.Row
        # add data form symbols exies
        print(f"Add {fill_symbols_table(db)} rows from eixapis symbols")
        return db


def clear_db(app, name='finance.db'):
    """
    Create new database from schema.sql - way to clear db after test
    Return clear database
    app - flask app to get path
    """
    with app.open_resource('schema.sql') as f:
        con = sqlite3.connect(app.root_path + '/' + name)
        con.executescript(f.read().decode('utf8'))
    db = con
    db.row_factory = sqlite3.Row
    return db


def fill_symbols_table(db):
    """
    fill symbols table from database db with data from eixapis symbols list
    db - database connection
    return number of rows in new table (symbols)
    """
    assert isinstance(db, sqlite3.Connection)
    db.row_factory = sqlite3.Row
    # get json symbols from iexs
    symbols_json = take_symbols()
    # add symbols with enabled field = true to database
    integrity_errors = 0
    for row in symbols_json:
        if row.get("isEnabled"):
            try:
                db.execute("INSERT INTO symbols "
                           "(symbol, exchange, exchangeSuffix, exchangeName, name, date, type, region, currency, "
                           "isEnabled) "
                           "VALUES (?,?,?,?,?,?,?,?,?,?)",
                           (row.get("symbol"), row.get("exchange"), row.get("exchangeSuffix"), row.get("exchangeName"),
                            row.get("name"), row.get("date"), row.get("type"), row.get("region"), row.get("currency"),
                            str(row.get("isEnabled"))))
            except sqlite3.IntegrityError:
                integrity_errors += 1
    db.commit()

    return db.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
