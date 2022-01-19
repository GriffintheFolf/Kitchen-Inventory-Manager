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

## input ##
def add_item(CONNECTION, CURSOR, DATA):
  """
  Add an item to the database.

  Args:
    CONNECTION (object):
    CURSOR (object):
    DATA (list): list containing the product name, unit count,
                 unit weight, expiration date, and barcode
  """

  CURSOR.execute("""
    INSERT INTO
      pantry
    VALUES(
      ?, ?, ?, ?, ?
    )
  ;""", DATA)
  CONNECTION.commit()

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

def update_item(CONNECTION, CURSOR, DATA):
  """
  Updates an item in the database by barcode.

  Args:
    CONNECTION (object):
    CURSOR (object):
    DATA (list): new data to insert
  """

  CURSOR.execute("""
    UPDATE
      pantry
    SET
      product_name = ?,
      product_count = ?,
      unit_weight = ?,
      expiration_date = ?
    WHERE
      barcode_number = ?
  ;""", DATA)
  CONNECTION.commit()

def delete_item(CONNECTION, CURSOR, BARCODE):
  """
  Deletes an item in the database by barcode.

  Args:
    CONNECTION (object):
    CURSOR (object):
    BARCODE (str): item to remove
  """

  # f-strings are not the best idea, but for some reason SQLite DOES NOT
  # like me specifying the barcode as a binding; it errors saying I have specified
  # too many, when there is only one being specified...
  CURSOR.execute(f"""
    DELETE FROM
      pantry
    WHERE
      barcode_number = {BARCODE}
  ;""")
  CONNECTION.commit()

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
  - the barcode number is stored as a string to avoid stripping of zeroes at the
    beginning
  """

  CURSOR.execute("""
    CREATE TABLE
      pantry(
        product_name TEXT NOT NULL,
        product_count REAL NOT NULL,
        unit_weight REAL NOT NULL,
        expiration_date INT NOT NULL,
        barcode_number TEXT PRIMARY KEY
      )
  ;""")

  CONNECTION.commit()

## output ##
def get_one_item(CURSOR, BARCODE):
  """
  Returns the specified item from the database, determined by the
  primary key - in this case the barcode number.

  Args:
    CURSOR (object):
    BARCODE (str): the barcode number

  Returns:
    ITEM (list): the item in the database
  """

  ITEM = CURSOR.execute("""
    SELECT
      *
    FROM
      pantry
    WHERE
      barcode_number = ?
  ;""", [BARCODE]).fetchone()

  return ITEM

def get_all_items(CURSOR):
  """
  Returns all items presently in the database.

  Args:
    CURSOR (object):

  Returns:
    ITEMS (list): all items in the database
  """

  ITEMS = CURSOR.execute("""
    SELECT
      *
    FROM
      pantry
    ORDER BY
      product_name
  ;""").fetchall()

  return ITEMS

def get_all_items_by_expiry(CURSOR):
  """
  The same as get_all_items(), but ordered by expiration
  date instead.

  Args:
    CURSOR (object):

  Returns:
    ITEMS (list): list of items in the database.
  """

  ITEMS = CURSOR.execute("""
    SELECT
      *
    FROM
      pantry
    ORDER BY
      expiration_date
  ;""").fetchall()

  return ITEMS

### "__main__ escape" ###
if __name__ == "__main__":
  pass
