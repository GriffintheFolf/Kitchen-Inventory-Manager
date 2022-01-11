"""
server.py

Title: Flask server
Author: Thomas Sirack
Date: 2021-12-17
"""

"""
This file mostly deals with creating the Flask server and serving
the pages.
"""

from flask import Flask, render_template, request
import src.db as db

### other variables ###
DB_FILENAME = "inventory.db"

### Flask-related variables ###
APPLICATION = Flask(__name__)

## page routing ##
@APPLICATION.route("/")

## page definitions ##
def index():
  """
  The main page of the website (index.html).
  """

  CONNECTION = db.get_connection(DB_FILENAME)
  CURSOR = db.get_cursor(CONNECTION)

  ITEMS = db.get_all_items(CURSOR)
  db.close_connection(CONNECTION)

  return render_template("index.html", pantry=ITEMS)

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
