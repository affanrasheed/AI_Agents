"""
Database package for the Travel Assistant.
"""
# This makes the functions directly importable from the database package
from database.connection import (
    download_database, 
    get_connection, 
    update_dates, 
    reset_database
)