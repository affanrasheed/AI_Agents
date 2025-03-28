"""
Database connection handling for the Travel Assistant.
"""
import os
import shutil
import sqlite3
from typing import Optional

import pandas as pd
import requests

import config


def download_database(force_download: bool = False) -> str:
    """
    Download the database if it doesn't exist locally.
    
    Args:
        force_download: Force download even if file exists
        
    Returns:
        Path to the local database file
    """
    if force_download or not os.path.exists(config.LOCAL_DB_PATH):
        response = requests.get(config.DB_URL)
        response.raise_for_status()  # Ensure request was successful
        
        with open(config.LOCAL_DB_PATH, "wb") as f:
            f.write(response.content)
            
        # Create backup - we will use this to "reset" our DB
        shutil.copy(config.LOCAL_DB_PATH, config.BACKUP_DB_PATH)
    
    return config.LOCAL_DB_PATH


def get_connection() -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.
    
    Returns:
        SQLite connection object
    """
    if not os.path.exists(config.LOCAL_DB_PATH):
        download_database()
        
    return sqlite3.connect(config.LOCAL_DB_PATH)


def update_dates(file: Optional[str] = None) -> str:
    """
    Update all dates in the database to be relative to the current time.
    This ensures that the flights are always in the future.
    
    Args:
        file: Path to the database file. If None, uses the default.
        
    Returns:
        Path to the updated database file
    """
    file = file or config.LOCAL_DB_PATH
    shutil.copy(config.BACKUP_DB_PATH, file)
    
    conn = sqlite3.connect(file)
    cursor = conn.cursor()

    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    ).name.tolist()
    tdf = {}
    for t in tables:
        tdf[t] = pd.read_sql(f"SELECT * from {t}", conn)

    example_time = pd.to_datetime(
        tdf["flights"]["actual_departure"].replace("\\N", pd.NaT)
    ).max()
    current_time = pd.to_datetime("now").tz_localize(example_time.tz)
    time_diff = current_time - example_time

    tdf["bookings"]["book_date"] = (
        pd.to_datetime(tdf["bookings"]["book_date"].replace("\\N", pd.NaT), utc=True)
        + time_diff
    )

    datetime_columns = [
        "scheduled_departure",
        "scheduled_arrival",
        "actual_departure",
        "actual_arrival",
    ]
    for column in datetime_columns:
        tdf["flights"][column] = (
            pd.to_datetime(tdf["flights"][column].replace("\\N", pd.NaT)) + time_diff
        )

    for table_name, df in tdf.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    
    conn.commit()
    conn.close()

    return file


def reset_database() -> str:
    """
    Reset the database to its original state.
    
    Returns:
        Path to the reset database file
    """
    return update_dates(config.LOCAL_DB_PATH)