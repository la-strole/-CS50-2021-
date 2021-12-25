from tempfile import mkdtemp
import shutil
import os
from flask import Flask
import db


class Config:
    TESTING = False
    # Configure session to use filesystem (instead of signed cookies)
    SESSION_FILE_DIR = mkdtemp()
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    DATABASE_URI = 'finance.db'
    # SECRET_KEY - set if with environment variable (export SECRET_KEY=VALUE)


class DevelopmentConfig(Config):
    DATABASE_URI = "finance.db"
    SECRET_KEY = "dev"
    DEBUG = True
    SESSION_FILE_DIR = os.getcwd() + mkdtemp()

    def clear_all_data(self, app):
        """
        clear all data - database, temp cookies
        app - Flask application
        """
        assert isinstance(app, Flask)
        root_dir = app.root_path
        # delete tmp with session cookies
        shutil.rmtree(f'/{root_dir}/tmp', ignore_errors=True)
        # delete db and make it from /schema.sql
        db.clear_db(app, app.config.get("DATABASE_URI"))


class TestingConfig(Config):
    DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
