"""
db.py

Title: SQL database functions
Author: Thomas Sirack
Date: 2022-01-10
"""

"""
This file deals with the creation and management of the database.
"""

import sqlite3
import pathlib

### subroutines ###

## processing ##
def does_exist(DB_FILENAME):
  """
  Checks to see if the database file at DB_FILENAME
  exists.

  Args:
    DB_FILENAME (str): path to the database file

  Returns:
    EXISTS (bool):
  """

  if(pathlib.Path.cwd() / DB_FILENAME).exists():
    return True

  return False

def get_connection(DB_FILENAME):
  """
  Opens the connection to the database file at DB_FILENAME.

  Args:
    DB_FILENAME (str): path to the database file

  Returns:
    CONNECTION (object):
  """

  CONNECTION = sqlite3.connect(DB_FILENAME)
  return CONNECTION

def get_cursor(CONNECTION):
  """
  Gets the cursor for the specified connection.

  Args:
    CONNECTION (object):

  Returns:
    CURSOR (object):
  """

  CURSOR = CONNECTION.cursor()
  return CURSOR

def close_connection(CONNECTION):
  """
  Closes the specified connection.
  Be advised that any cursor objects that used this connection
  will no longer work.

  Args:
    CONNECTION (object):
  """

  CONNECTION.close()

def init_db(CONNECTION, CURSOR):
  """
  Initialize the database file.
  This function adds the tables and columns to the database on the first run.

  Args:
    CONNECTION (object): connection to the database
    CURSOR (object):
  """

  """
  Notes:

  - the unit weight is how many grams per "container" of a product
    (e.g. a single 454 gram box of crackers has a unit weight of 454 grams)
  - likewise, product count is how many containers of a product you have.
    it is stored as a REAL to allow for partial containers (e.g. 0.5 of a box)
  - the expiration date is stored as an INT object as the number of seconds since
    the Unix epoch (January 1, 1970, 00:00:00 UTC)
  """

  CURSOR.execute("""
    CREATE TABLE
      pantry(
        product_name TEXT NOT NULL,
        product_count REAL NOT NULL,
        unit_weight REAL NOT NULL,
        expiration_date INT NOT NULL,
        barcode_number INT PRIMARY KEY
      )
  ;""")

  CONNECTION.commit()

### "__main__ escape" ###
if __name__ == "__main__":
  pass
