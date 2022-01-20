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

from flask import Flask, redirect, render_template, request, url_for
import src.db as db

import datetime
import html
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

    ## this is *VERY IMPORTANT* to mitigate XSS, as inline HTML is on ##
    PRODUCT_NAME = html.escape(PRODUCT_NAME)
    UNIT_COUNT = html.escape(UNIT_COUNT)
    UNIT_WEIGHT = html.escape(UNIT_WEIGHT)
    EXPIRATION_DATE = html.escape(EXPIRATION_DATE)
    BARCODE_NUMBER = html.escape(BARCODE_NUMBER)

    ## strip unit weight and product count to just the raw number ##
    try:
      # see https://stackoverflow.com/questions/3939361/remove-specific-characters-from-a-string-in-python
      # could probably just use regex, but i don't know how it works
      UNIT_WEIGHT = UNIT_WEIGHT.translate({ord(c): None for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz~!@#$%^&*()_+{}|:\"<>?`-=[]\\;',/"})
      UNIT_WEIGHT = float(UNIT_WEIGHT)
      UNIT_COUNT = UNIT_COUNT.translate({ord(c): None for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz~!@#$%^&*()_+{}|:\"<>?`-=[]\\;',/"})
      UNIT_COUNT = float(UNIT_COUNT)
    except ValueError:
      ALERT = "Unit amount is not a valid number!"

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
  TWO_WEEKS = (86400 * 14)
  TWO_WEEKS_FROM_NOW = time.time() + TWO_WEEKS

  for i in range(len(ITEMS)):
    DATETIME_DATE = datetime.datetime.fromtimestamp(ITEMS[i][3])

    # if expiration date is past the present day, mark the text as red
    if time.time() > DATETIME_DATE.timestamp():
      DATETIME_DATE = datetime.datetime.strftime(DATETIME_DATE, "<span style='color:red;'><b>%Y-%m-%d</b></span>")

    # if the item will expire within two weeks (threshold specified by client), mark in orange
    elif (DATETIME_DATE.timestamp() - time.time()) < TWO_WEEKS:
      DATETIME_DATE = datetime.datetime.strftime(DATETIME_DATE, "<span style='color:orange;'><b>%Y-%m-%d</b></span>")

    else:
      DATETIME_DATE = datetime.datetime.strftime(DATETIME_DATE, "%Y-%m-%d")

    # rather annoyingly, SQLite returns a list of tuples ...
    ITEMS[i] = (ITEMS[i][0], ITEMS[i][1], ITEMS[i][2], DATETIME_DATE, ITEMS[i][4])

  return render_template("expiring.html", pantry=ITEMS)

@APPLICATION.route("/enough", methods=["GET", "POST"])
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

  if request.form:
    SELECTED_ITEM = request.form.get("selected_item")
    AMOUNT_NEEDED = request.form.get("amount_needed")

    ## strip needed amount to just the raw number ##
    AMOUNT_NEEDED = html.escape(AMOUNT_NEEDED)
    try:
      # see https://stackoverflow.com/questions/3939361/remove-specific-characters-from-a-string-in-python
      # could probably just use regex, but i don't know how it works
      AMOUNT_NEEDED = AMOUNT_NEEDED.translate({ord(c): None for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz~!@#$%^&*()_+{}|:\"<>?`-=[]\\;',/"})
      AMOUNT_NEEDED = float(AMOUNT_NEEDED)
    except ValueError:
      ALERT = "Amount needed is not a valid number!"

    ITEM = db.get_one_item(CURSOR, SELECTED_ITEM)

    # total amount of grams available - the simplest check
    UNIT_COUNT = ITEM[1]
    UNIT_WEIGHT = ITEM[2]
    TOTAL_AVAILABLE = UNIT_COUNT * UNIT_WEIGHT

    if AMOUNT_NEEDED > TOTAL_AVAILABLE:
      ENOUGH = False
      ALERT = "You do not have enough of this item."

      # determine how many units are needed to have enough
      DIFFERENCE = AMOUNT_NEEDED - TOTAL_AVAILABLE
      REMAINING = DIFFERENCE / UNIT_WEIGHT
    else:
      # if there is enough #
      ENOUGH = True
      ALERT = "You have enough of this item."

      # determine how many units will remain after use #
      TOTAL_AFTER = TOTAL_AVAILABLE - AMOUNT_NEEDED
      REMAINING = TOTAL_AFTER / UNIT_WEIGHT

  ## database items ##
  ITEMS = db.get_all_items(CURSOR)

  return render_template("enough.html", alert=ALERT, enough=ENOUGH, remaining=REMAINING, pantry=ITEMS)


@APPLICATION.route("/edit/<BARCODE>", methods=["GET", "POST"])
def edit(BARCODE):
  """
  The page to edit information for an item (edit.html).

  No actual form submission is handled here, edit_action does that.
  """

  ALERT = ""

  CONNECTION = db.get_connection(DB_FILENAME)
  CURSOR = db.get_cursor(CONNECTION)

  ITEM = db.get_one_item(CURSOR, BARCODE)

  # convert Unix timestamp to human-readable form #
  DATETIME_DATE = datetime.datetime.fromtimestamp(ITEM[3])
  DATETIME_TEXT = datetime.datetime.strftime(DATETIME_DATE, "%Y-%m-%d")
  ITEM = (ITEM[0], ITEM[1], ITEM[2], DATETIME_TEXT, ITEM[4])

  return render_template("/edit.html", alert=ALERT, item=ITEM)

@APPLICATION.route("/edit_action", methods=["GET", "POST"])
def edit_action():
  """
  The actions for editing an item in the database.
  """

  CONNECTION = db.get_connection(DB_FILENAME)
  CURSOR = db.get_cursor(CONNECTION)

  if request.form:
    PRODUCT_NAME = request.form.get("product_name")
    ITEM_COUNT = request.form.get("item_count")
    UNIT_AMOUNT = request.form.get("unit_weight")
    EXPIRATION_DATE = request.form.get("expiration_date")
    BARCODE_NUMBER = request.form.get("barcode_number")

    # convert human-readable form back to Unix timestamp #
    DATETIME_DATE = datetime.datetime.strptime(EXPIRATION_DATE, "%Y-%m-%d")
    EXPIRATION_DATE = DATETIME_DATE.timestamp()

    DATA = [PRODUCT_NAME, ITEM_COUNT, UNIT_AMOUNT, EXPIRATION_DATE, BARCODE_NUMBER]
    db.update_item(CONNECTION, CURSOR, DATA)

    db.close_connection(CONNECTION)

  return redirect("/")


@APPLICATION.route("/delete/<BARCODE>")
def delete(BARCODE):
  """
  Deletes an item from the database.

  Args:
    BARCODE (str): the barcode of the item to delete
  """

  CONNECTION = db.get_connection(DB_FILENAME)
  CURSOR = db.get_cursor(CONNECTION)

  db.delete_item(CONNECTION, CURSOR, BARCODE)
  db.close_connection(CONNECTION)

  return redirect("/")

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
