import os
import requests
import urllib.parse
import re

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def take_symbols():
    """
    take list of allowed symbols form iexapis
    """
    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/ref-data/symbols?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    # Parse response
    try:
        symbols_json = response.json()
        return symbols_json
    except (ValueError, TypeError):
        return None


def check_ticker_text_fail(ticker: str):
    """
    return None if ticker is letter or digit or -+= symbol
    else return error message
    ticker: str - string as stock symbol
    """
    assert isinstance(ticker, str)
    if ticker:
        if len(ticker) <= 6:
            pattern = re.compile("[A-Za-z0-9+-=]+")
            if not pattern.fullmatch(ticker):
                return f"Sorry, your ticker ({ticker}) is not consists only from letters, digits and + - = symbols."
            # alright
            return None
        else:
            return f"Sorry, your ticker ({ticker}) is longer than 6 chars."
    else:
        return f"Sorry, your ticker ({ticker}) is empty."


def check_count_text_fail(count: str):
    """
    Check count as a positive integer
    Return None if there are no errors, else return error text
    count - str
    """
    assert isinstance(count, str)
    if count:
        pattern = re.compile("[0-9]+")
        if not pattern.fullmatch(count):
            return f"Sorry, your number ({count}) is not consists only from positive digits 1-9."
        else:
            try:
                int(count)
                return None
            except ValueError:
                return f"Sorry, something wrong with your number {count}"
    else:
        return f"Sorry, your number ({count}) is empty."
