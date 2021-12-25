from datetime import datetime
import os
import db
import sqlite3
# from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

import helpers
from configmodule import DevelopmentConfig
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)
app.config.from_object(DevelopmentConfig())


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
Session(app)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # collect tickers = [{'name':ticker_name, 'symbol':ticker_symbol, 'share':ticker_count_from_db,
    # 'current_cost': ticker_current_price;}]
    tickers = []
    total = 0
    # database context ---------------------------------------------------------------------------------------------
    database = db.get_db(app)

    # get DIST symbols for username from database
    rows = database.execute("SELECT symbol, share"
                            " FROM depo"
                            " WHERE user_id = ?",
                            (session["user_id"],))
    for row in rows:
        ticker = dict.fromkeys(('name', 'symbol', 'share', 'current_price'))
        ticker["share"] = row["share"]
        ticker["symbol"] = row["symbol"]
        tickers.append(ticker)
    # get cash from users table of database
    row = database.execute("SELECT cash, username "
                           "FROM users "
                           "WHERE id = ?",
                           (session["user_id"],))
    cash, username = row.fetchone()
    database.close()
    # END database context ----------------------------------------------------------------------------------------
    # for every symbol call helper.lookup() to collect name, symbol, current_cost to tickers dict. Calculate total
    for ticker in tickers:
        lookup_result = lookup(ticker["symbol"])
        if not lookup_result:
            flash(f"Can not get information about {ticker['symbol']} from IEX.")
            continue
        else:
            ticker['symbol'] = lookup_result.get("symbol")
            ticker['current_price'] = lookup_result.get("price")
            ticker['name'] = lookup_result.get('name')
            total = total + (int(ticker['share']) * float(ticker['current_price']))

    # call jinja template with variables: tickers:dict, cash, total
    return render_template("index.html", username=username, tickers=tickers, cash=cash, total=total + cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "GET":
        # if url like .../buy?symbol=somestock (if it is AJAX or regular GET response)
        if 'symbol' in request.args:
            error_messages = helpers.check_ticker_text_fail(request.args.get("symbol"))
            if not error_messages:
                # SELECT from DATABASE
                database = db.get_db(app)
                rows = database.execute("SELECT symbol FROM symbols WHERE symbol LIKE ? LIMIT 10",
                                        request.args.get("symbol")).fetchall()
                resp = jsonify([row["symbol"] for row in rows])
                database.close()
                return resp
            else:
                return jsonify([])
        # if it is regular GET request
        else:
            return render_template("buy.html")
    else:
        # get data from POST request
        ticker = request.form.get("symbol")
        count = request.form.get("shares")
        # check data
        error_message = helpers.check_ticker_text_fail(ticker)
        error_message_count = helpers.check_count_text_fail(count)
        if error_message:
            return apology(error_message)
        elif error_message_count:
            return apology(error_message_count)
        # If there are no errors with user request data
        else:
            count = int(count)
            # try to get data from EIXAPIS
            lookup_results = lookup(ticker)
            if not lookup_results:
                return apology(f"Sorry, there is no result for your ticker {ticker}")
            else:
                current_price = lookup_results.get("price")
                #  database context (auto database.commit())-----------------------------------------------------------
                database = db.get_db(app)

                # get user's cash from database - user_id from session["user_id"] cookies (set in login)
                username = database.execute("SELECT username FROM users WHERE id = ?",
                                            (session["user_id"],)).fetchone()["username"]
                current_cash = database.execute("SELECT cash FROM users WHERE username = ?",
                                                (username,)).fetchone()["cash"]
                # Check if user can afford this purchase
                if current_cash >= count * current_price:
                    # make purchase

                    # 1 add new data to depo table
                    # Check if this user already has this type of stock (ticket variable)
                    user_ticker_count = database.execute("SELECT COUNT(*) "
                                                         "FROM depo "
                                                         "WHERE depo.user_id = ? AND depo.symbol = ?",
                                                         (session["user_id"], lookup_results["symbol"])).fetchone()[0]
                    database.close()
                    # transaction - ADD stock to depo, take cash from users, add row to log
                    database = db.get_db(app)
                    database.isolation_level = None  # ON autocommit mode. Hand control of transaction-to group rollback
                    # TRANSACTION----------------------------
                    database.execute("begin")
                    try:
                        # 1 Add stock to depo table
                        if user_ticker_count > 0:
                            # if there are more than 1 row for user ticker - raise error
                            assert (user_ticker_count == 1, "Error with number of users rows in depo table in database")
                            # User has this type of stock - increase share column
                            database.execute("UPDATE depo SET share = share + ? "
                                             "WHERE user_id = ? "
                                             "AND symbol = ?",
                                             (count, session["user_id"], lookup_results["symbol"]))
                        else:
                            # User does not have this type of stock - add new row to depo table
                            database.execute("INSERT "
                                             "INTO depo (user_id, symbol, share) "
                                             "VALUES (?,?,?)",
                                             (session["user_id"], lookup_results["symbol"], count))

                        # 2 decrease cash from users table
                        database.execute("UPDATE users "
                                         "SET cash = cash - ?"
                                         "WHERE id = ?",
                                         (count * current_price, session["user_id"]))

                        # 3 add this purchase to log table
                        database.execute("INSERT "
                                         "INTO log (user_id, symbol, share, price, operation, date_time)"
                                         "VALUES (?,?,?,?,?,?)",
                                         (session["user_id"], lookup_results["symbol"], count, current_price, 'buy',
                                          datetime.now().isoformat()))
                        # 4 commit transaction changes
                        database.execute("commit")
                    # TODO change after test in production
                    except sqlite3.Error as e:
                        print("Error with sqlite3 in buy() function TRANSACTION")
                        database.execute("rollback")
                        database.close()
                        raise e

                    # END TRANSACTION ----------------------

                else:
                    flash(f"Sorry, but you do not have enough cash to buy {count} {lookup_results['symbol']} "
                          f"with current price {usd(current_price)}. Your cash is {usd(current_cash)}.")

                database.close()
                # END database context ---------------------------------------------------------------------------
                return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # database log table
    # database context ----------------------------------------------------------
    database = db.get_db(app)
    try:
        rows = database.execute("SELECT operation, symbol, share, price, date_time "
                                "FROM log "
                                "WHERE user_id = ? "
                                "ORDER BY id",
                                (session["user_id"],))
        username = database.execute("SELECT username "
                                    "FROM users "
                                    "WHERE id = ?",
                                    (session["user_id"],)).fetchone()["username"]
        if not username:
            username = "user"

    except sqlite3.Error:
        print("SQL error in history() function")
        database.close()
        flash("Sorry, something wring with log data. Please try again.")
        return redirect("/")

    try:
        resp = render_template("history.html", username=username, rows=rows)
    except Exception as e:
        print("Error in history() with jinja template")
        # test configurat
        # TODO remove it in production for silence
        database.close()
        raise e

    database.close()
    # END database context ------------------------------------------------------
    if resp:
        return resp
    else:
        flash("Sorry, something wrong with history data, please, try again.")
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        database = db.get_db(app)

        rows = database.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            database.close()
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        database.close()
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        # realize AJAX
        if 'symbol' in request.args:
            error_messages = helpers.check_ticker_text_fail(request.args.get("symbol"))
            if not error_messages:
                database = db.get_db(app)
                rows = database.execute("SELECT symbol FROM symbols WHERE symbol LIKE ? LIMIT 10",
                                        ((request.args.get('symbol') + '%'),)).fetchall()
                resp = jsonify([row["symbol"] for row in rows])
                database.close()
                return resp
            else:
                return jsonify([])
        else:
            return render_template("quote_get.html")
    elif request.method == "POST":
        # get ticker from client
        ticker = request.form.get("symbol")
        # check ticker and add flash error messages
        error_message = helpers.check_ticker_text_fail(ticker)
        # if alright - get response from EIXAPIS server
        if not error_message:
            # dictionary from eixapis with helpers.py
            lookup_results = lookup(ticker)
            # if everything is alright
            if lookup_results:
                return render_template("quote_post.html", name=lookup_results.get("name"),
                                       price=lookup_results.get("price"), symbol=lookup_results.get("symbol"))
            else:
                return apology(f"Sorry, there is not results for your ticker ({ticker})")
        else:
            return apology(f"Sorry, your ticker ({ticker}) is empty.")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # POST request from client
    if request.method == "POST":

        # get values from client
        username = str(request.form.get("username"))
        password = str(request.form.get("password"))
        conformation = request.form.get("confirmation")

        # Check username and password
        if not username:
            return apology("User field is empty", 400)
        if not password:
            return apology("Password field is empty", 400)
        if not conformation:
            return apology("Confirm field is empty", 400)
        if password != conformation:
            return apology("Password and Conform are different", 400)

        # Add username and hash password to database
        database = db.get_db(app)
        try:
            with database:
                database.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                                 (username, generate_password_hash(password)))
        except sqlite3.IntegrityError:
            # If username already exist
            print("SQL Integrity error in register() function")
            database.close()
            return apology(f"{username} is already exist, try another Username")

        # Remember which user has logged in
        rows = database.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()
        session["user_id"] = rows[0]["id"]
        database.close()
        # Redirect user to home page
        return redirect("/")

    # if client go to /register directly - GET request
    else:
        # return register template
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # GET REQUEST:
    if request.method == "GET":
        # get user's ticker and count from database
        # database context -----------------------------------------------------------------------------------
        database = db.get_db(app)
        tickers = []
        try:
            rows = database.execute("SELECT symbol, share FROM depo WHERE user_id = ?", (session["user_id"],))
        except sqlite3.Error:
            print("SQL error sell() function GET request")
            database.close()
            return apology("Sorry, it is seem to be something wrong with username. Try again, please.")
        for row in rows:
            tickers.append({'symbol': row['symbol'], 'share': row['share']})
        database.close()
        # END database context -------------------------------------------------------------------------------
        # create template with jinja - send it tickers=[{'symbol':<symbol_value>, 'share':<share_value>},]
        # return template sell.html
        return render_template("sell.html", tickers=tickers)
    # POST REQUEST
    if request.method == "POST":
        # Check client data
        symbol = request.form.get("symbol")
        number = request.form.get("shares")
        if not symbol:
            return apology("Sorry, it is seem to be you forgot to set stock name.")
        if not number:
            return apology("Sorry, it is seem to be you forgot to set share.")
        # check if syntax is correct
        error = helpers.check_ticker_text_fail(symbol)
        if error:
            return apology(f"Sorry, it is seem to be something wrong with your stock name {symbol}.")
        error = helpers.check_count_text_fail(number)
        if error or int(number) < 1:
            return apology("fSorry, it is seem to be something wrong with your number {number}.")
        # check from database data
        # database context -----------------------------------------------------------------------------------
        database = db.get_db(app)
        try:
            rows = database.execute("SELECT symbol, share "
                                    "FROM depo "
                                    "WHERE user_id = ? "
                                    "AND symbol = ?", (session["user_id"], symbol))
        except sqlite3.Error:
            print("SQL Error sell() function 1")
            database.close()
            return apology(f"Sorry, something wrong with stock name {symbol}. Please, try again.")
        db_symbol, db_number = rows.fetchone()
        database.close()
        # END database context ----------------------------------------------------------------------
        # Has user this ticker?
        if not db_symbol:
            return apology(f"Sorry, you have not this stock: {symbol}.")
        # Can user sell it in this quantity?
        if db_number < int(number):
            print(f"user id = {session['user_id']} error try ro sell more than have. db_symbol={db_symbol}, "
                  f"db_number={db_number}")
            return apology(f"Sorry, you have not enough stocks: You want to sell {number}, you have {db_number}.")
        # make call helpers.lookup() for current price
        lookup_results = lookup(symbol)
        if not lookup_results:
            return apology(f"Sorry, can not get current price from IEX of your stock {symbol}.")
        # update database
        database = db.get_db(app)
        database.isolation_level = None
        # TRANSACTION -----------------------------------------------------------
        database.execute("begin")
        try:
            # update depo table
            # delete row if share become 0, else - reduce data in depo table
            if db_number == int(number):
                database.execute("DELETE "
                                 "FROM depo "
                                 "WHERE user_id = ? "
                                 "AND symbol = ?",
                                 (session["user_id"], lookup_results.get("symbol")))
            else:
                database.execute("UPDATE depo SET share = share - ? "
                                 "WHERE user_id = ? "
                                 "AND symbol = ?",
                                 (int(number), session["user_id"], lookup_results.get("symbol")))
            # update users cash
            database.execute("UPDATE users "
                             "SET cash = cash + ?"
                             "WHERE id = ?",
                             (int(number) * lookup_results.get("price"), session["user_id"]))
            # set changes on log table
            database.execute("INSERT "
                             "INTO log (user_id, symbol, share, price, operation, date_time)"
                             "VALUES (?,?,?,?,?,?)",
                             (session["user_id"], lookup_results.get("symbol"), int(number),
                              lookup_results.get("price"), 'sell', datetime.now().isoformat()))
            # commit changes
            database.execute("commit")

        except sqlite3.Error:
            print("SQL error sell() function in transaction")
            database.execute("rollback")
        # END TRANSACTION ----------------------------------------------------------
        database.close()
        # END db context -----------------------------------------------------------------------------------------
        # return index.html
        return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
