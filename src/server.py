"""
server.py

Title: Flask server
Author: Thomas Sirack
Date: 2021-12-17
"""

"""
This file mostly deals with creating the Flask server and serving
the pages.

It also handles some form processing.
"""

from flask import Flask, render_template, request, url_for
import src.db as db

import datetime
import time
from sqlite3 import IntegrityError

### other variables ###
DB_FILENAME = "inventory.db"

### Flask-related variables ###
APPLICATION = Flask(__name__)

## page definitions ##
@APPLICATION.route("/", methods=["GET", "POST"])
def index():
  """
  The main page of the website (index.html).
  """

  ALERT = ""

  ## open connection right away to avoid issues ##
  CONNECTION = db.get_connection(DB_FILENAME)
  CURSOR = db.get_cursor(CONNECTION)

  ## form handling ##
  if request.form:
    PRODUCT_NAME = request.form.get("product_name")
    UNIT_COUNT = request.form.get("item_count")
    UNIT_WEIGHT = request.form.get("unit_weight")
    EXPIRATION_DATE = request.form.get("expiration_date")
    BARCODE_NUMBER = request.form.get("barcode_number")

    ## add the item ##
    DATE_FORM = datetime.datetime.strptime(EXPIRATION_DATE, "%Y-%m-%d")
    DATE_FORM = int(datetime.datetime.timestamp(DATE_FORM))
    DATA = [PRODUCT_NAME, UNIT_COUNT, UNIT_WEIGHT, DATE_FORM, BARCODE_NUMBER]

    try:
      db.add_item(CONNECTION, CURSOR, DATA)
    except IntegrityError:
      ALERT = "An item with the same barcode already exists!"

  ## database items ##
  ITEMS = db.get_all_items(CURSOR)

  # modify Unix timestamp to human readable value #
  for i in range(len(ITEMS)):
    DATETIME_DATE = datetime.date.fromtimestamp(ITEMS[i][3])
    DATETIME_DATE = datetime.datetime.strftime(DATETIME_DATE, "%Y-%m-%d")

    # rather annoyingly, SQLite returns a list of tuples ...
    ITEMS[i] = (ITEMS[i][0], ITEMS[i][1], ITEMS[i][2], DATETIME_DATE, ITEMS[i][4])

  return render_template("index.html", alert=ALERT, pantry=ITEMS)

@APPLICATION.route("/expiring")
def expiring():
  """
  The page sorting by expiration date (expiring.html).
  """

  CONNECTION = db.get_connection(DB_FILENAME)
  CURSOR = db.get_cursor(CONNECTION)

  ITEMS = db.get_all_items_by_expiry(CURSOR)
  # modify Unix timestamp to human readable value #
  for i in range(len(ITEMS)):
    DATETIME_DATE = datetime.datetime.fromtimestamp(ITEMS[i][3])

    # if expiration date is past the present day, mark the text as red
    if time.time() > DATETIME_DATE.timestamp():
      DATETIME_DATE = datetime.datetime.strftime(DATETIME_DATE, "<span style='color:red;'><b>%Y-%m-%d</b></span>")
    else:
      DATETIME_DATE = datetime.datetime.strftime(DATETIME_DATE, "%Y-%m-%d")

    # rather annoyingly, SQLite returns a list of tuples ...
    ITEMS[i] = (ITEMS[i][0], ITEMS[i][1], ITEMS[i][2], DATETIME_DATE, ITEMS[i][4])

  return render_template("expiring.html", pantry=ITEMS)

@APPLICATION.route("/enough")
def enough():
  """
  The page to check if there is enough of an ingredient (enough.html).
  """

  ALERT = ""
  ENOUGH = False

  # N.B. this variable is also used to say how many of an ingredient are needed
  # if there are not enough already
  REMAINING = 0.0

  CONNECTION = db.get_connection(DB_FILENAME)
  CURSOR = db.get_cursor(CONNECTION)

  ## database items ##
  ITEMS = db.get_all_items(CURSOR)

  return render_template("enough.html", alert=ALERT, enough=ENOUGH, remaining=REMAINING, pantry=ITEMS)

### subroutines ###
def start_flask():
  """
  Starts the Flask server.
  """

  global APPLICATION

  """
  Required to allow inline HTML to display correctly, see
  https://stackoverflow.com/questions/62151238/how-to-set-the-jinja-environment-variable-in-flask

  Be mindful that this is very likely a security risk that allows for cross-side scripting (XSS)!
  """
  APPLICATION.jinja_options["autoescape"] = False
  APPLICATION.run(debug=True)

### "__main__ escape" ###
if __name__ == "__main__":
  pass
