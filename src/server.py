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

### Flask-related variables ##
APPLICATION = Flask(__name__)

## page routing ##
@APPLICATION.route("/")

## page definitions ##
def index():
  """
  The main page of the website (index.html).
  """

  return render_template("index.html")

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
