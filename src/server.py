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

from flask import Flask, render_template, request
import src.db as db

import datetime

### other variables ###
DB_FILENAME = "inventory.db"

### Flask-related variables ###
APPLICATION = Flask(__name__)

## page routing ##
@APPLICATION.route("/", methods=["GET", "POST"])

## page definitions ##
def index():
  """
  The main page of the website (index.html).
  """

  ALERT = ""

  ## form handling ##
  if request.form:
    PRODUCT_NAME = request.form.get("product_name")
    UNIT_COUNT = request.form.get("item_count")
    UNIT_WEIGHT = request.form.get("unit_weight")
    EXPIRATION_DATE = request.form.get("expiration_date")
    BARCODE_NUMBER = request.form.get("barcode_number")

    ## check if item already exists ##
    CONNECTION = db.get_connection(DB_FILENAME)
    CURSOR = db.get_cursor(CONNECTION)

    if db.get_one_item(CURSOR, BARCODE_NUMBER):
      ALERT = "An item with the same barcode number already exists."
      db.close_connection(CONNECTION)

    ## add the item ##
    DATE_FORM = datetime.datetime.strptime(EXPIRATION_DATE, "%Y-%m-%d")
    DATE_FORM = int(datetime.datetime.timestamp(DATE_FORM))
    DATA = [PRODUCT_NAME, UNIT_COUNT, UNIT_WEIGHT, DATE_FORM, BARCODE_NUMBER]

    db.add_item(CONNECTION, CURSOR, DATA)
    db.close_connection(CONNECTION)

  ## database items ##
  CONNECTION = db.get_connection(DB_FILENAME)
  CURSOR = db.get_cursor(CONNECTION)

  ITEMS = db.get_all_items(CURSOR)
  db.close_connection(CONNECTION)

  # modify Unix timestamp to human readable value #

  return render_template("index.html", alert=ALERT, pantry=ITEMS)

### subroutines ###
def start_flask():
  """
  Starts the Flask server.
  """

  global APPLICATION
  APPLICATION.run(debug=True)

### "__main__ escape" ###
if __name__ == "__main__":
  pass
