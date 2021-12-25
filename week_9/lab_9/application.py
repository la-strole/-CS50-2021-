import os
import db_logic
# from cs50 import SQL

from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///birthdays.db")

ERROR_MESSAGE = []
DB_SOURCE = "birthdays.db"


@app.route("/", methods=["GET", "POST"])
def index():
    global ERROR_MESSAGE
    database = db_logic.DataBase(DB_SOURCE)

    if request.method == "POST":
        ERROR_MESSAGE = []
        # get data from client
        name = request.form.get("name")
        if not name or \
                len(name) > 20 or \
                len(name) < 2 or \
                not name.isalpha():
            ERROR_MESSAGE.append("Please, change name")

        month = request.form.get("month")
        try:
            month = int(month)
            if month < 1 or month > 12:
                ERROR_MESSAGE.append("Please, change month")
        except ValueError:
            ERROR_MESSAGE.append("Please, change month")

        day = request.form.get("day")
        try:
            day = int(day)
            if day < 1 or \
                    day > 31 or \
                    (month in [4, 6, 9, 11] and day > 30) or \
                    (month == 2 and day > 29):
                ERROR_MESSAGE.append("Please, change date")
        except ValueError:
            ERROR_MESSAGE.append("Please, change date")

        # insert user data to database
        if not ERROR_MESSAGE:
            database.insert_name_date(name, month, day)

        return redirect("/")

    else:
        name_date = database.get_name_date()
        if ERROR_MESSAGE:
            alert_message = ', '.join(ERROR_MESSAGE)
        else:
            alert_message = ""
        ERROR_MESSAGE = []
        print(f"from get - alert msg = {alert_message}")
        return render_template("index.html", name_date=name_date, alert_message=alert_message)

