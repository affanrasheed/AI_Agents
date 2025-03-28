"""
Car rental tools for the Travel Assistant.
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional, Union

from langchain_core.tools import tool

from database.connection import get_connection


@tool
def search_car_rentals(
    location: Optional[str] = None,
    name: Optional[str] = None,
    price_tier: Optional[str] = None,
    start_date: Optional[Union[datetime, date]] = None,
    end_date: Optional[Union[datetime, date]] = None,
) -> List[Dict[str, Any]]:
    """
    Search for car rentals based on location, name, price tier, start date, and end date.

    Args:
        location: The location of the car rental
        name: The name of the car rental company
        price_tier: The price tier of the car rental
        start_date: The start date of the car rental
        end_date: The end date of the car rental

    Returns:
        A list of car rental dictionaries matching the search criteria
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM car_rentals WHERE 1=1"
    params = []

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
        
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
        
    # Note: For this tutorial, we allow matches on any dates and price tier
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    
    conn.close()

    return [dict(zip(column_names, row)) for row in results]


@tool
def book_car_rental(rental_id: int) -> str:
    """
    Book a car rental by its ID.

    Args:
        rental_id: The ID of the car rental to book

    Returns:
        A message indicating whether the car rental was successfully booked
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE car_rentals SET booked = 1 WHERE id = ?", (rental_id,))
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Car rental {rental_id} successfully booked."
    else:
        conn.close()
        return f"No car rental found with ID {rental_id}."


@tool
def update_car_rental(
    rental_id: int,
    start_date: Optional[Union[datetime, date]] = None,
    end_date: Optional[Union[datetime, date]] = None,
) -> str:
    """
    Update a car rental's start and end dates by its ID.

    Args:
        rental_id: The ID of the car rental to update
        start_date: The new start date of the car rental
        end_date: The new end date of the car rental

    Returns:
        A message indicating whether the car rental was successfully updated
    """
    conn = get_connection()
    cursor = conn.cursor()

    if start_date:
        cursor.execute(
            "UPDATE car_rentals SET start_date = ? WHERE id = ?",
            (start_date, rental_id),
        )
        
    if end_date:
        cursor.execute(
            "UPDATE car_rentals SET end_date = ? WHERE id = ?", 
            (end_date, rental_id)
        )

    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Car rental {rental_id} successfully updated."
    else:
        conn.close()
        return f"No car rental found with ID {rental_id}."


@tool
def cancel_car_rental(rental_id: int) -> str:
    """
    Cancel a car rental by its ID.

    Args:
        rental_id: The ID of the car rental to cancel

    Returns:
        A message indicating whether the car rental was successfully cancelled
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE car_rentals SET booked = 0 WHERE id = ?", (rental_id,))
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Car rental {rental_id} successfully cancelled."
    else:
        conn.close()
        return f"No car rental found with ID {rental_id}."