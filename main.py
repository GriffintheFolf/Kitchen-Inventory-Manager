#!/usr/bin/env python3

"""
main.py

Title: main entry point for program
Author: Thomas Sirack
Date: 2022-01-10
"""

import src.db as db
import src.server as server

### variables ###
DB_FILENAME = "inventory.db"

### main program code ###
if __name__ == "__main__":
  # create database file if it does not exist
  if not db.does_exist(DB_FILENAME):
    CONNECTION = db.get_connection(DB_FILENAME)
    CURSOR = db.get_cursor(CONNECTION)
    db.init_db(CONNECTION, CURSOR)
    db.close_connection(CONNECTION)

  server.start_flask()
