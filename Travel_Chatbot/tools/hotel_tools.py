"""
Hotel-related tools for the Travel Assistant.
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional, Union

from langchain_core.tools import tool

from database.connection import get_connection


@tool
def search_hotels(
    location: Optional[str] = None,
    name: Optional[str] = None,
    price_tier: Optional[str] = None,
    checkin_date: Optional[Union[datetime, date]] = None,
    checkout_date: Optional[Union[datetime, date]] = None,
) -> List[Dict[str, Any]]:
    """
    Search for hotels based on location, name, price tier, check-in date, and check-out date.

    Args:
        location: The location of the hotel
        name: The name of the hotel
        price_tier: The price tier of the hotel (Midscale, Upper Midscale, Upscale, Luxury)
        checkin_date: The check-in date of the hotel
        checkout_date: The check-out date of the hotel

    Returns:
        A list of hotel dictionaries matching the search criteria
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM hotels WHERE 1=1"
    params = []

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
        
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
        
    # Note: For this tutorial, we allow matches on any dates and price tier
    # because our toy dataset doesn't have much data
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    
    conn.close()

    return [dict(zip(column_names, row)) for row in results]


@tool
def book_hotel(hotel_id: int) -> str:
    """
    Book a hotel by its ID.

    Args:
        hotel_id: The ID of the hotel to book

    Returns:
        A message indicating whether the hotel was successfully booked
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE hotels SET booked = 1 WHERE id = ?", (hotel_id,))
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Hotel {hotel_id} successfully booked."
    else:
        conn.close()
        return f"No hotel found with ID {hotel_id}."


@tool
def update_hotel(
    hotel_id: int,
    checkin_date: Optional[Union[datetime, date]] = None,
    checkout_date: Optional[Union[datetime, date]] = None,
) -> str:
    """
    Update a hotel's check-in and check-out dates by its ID.

    Args:
        hotel_id: The ID of the hotel to update
        checkin_date: The new check-in date of the hotel
        checkout_date: The new check-out date of the hotel

    Returns:
        A message indicating whether the hotel was successfully updated
    """
    conn = get_connection()
    cursor = conn.cursor()

    if checkin_date:
        cursor.execute(
            "UPDATE hotels SET checkin_date = ? WHERE id = ?", (checkin_date, hotel_id)
        )
        
    if checkout_date:
        cursor.execute(
            "UPDATE hotels SET checkout_date = ? WHERE id = ?",
            (checkout_date, hotel_id),
        )

    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Hotel {hotel_id} successfully updated."
    else:
        conn.close()
        return f"No hotel found with ID {hotel_id}."


@tool
def cancel_hotel(hotel_id: int) -> str:
    """
    Cancel a hotel booking by its ID.

    Args:
        hotel_id: The ID of the hotel to cancel

    Returns:
        A message indicating whether the hotel was successfully cancelled
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE hotels SET booked = 0 WHERE id = ?", (hotel_id,))
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Hotel {hotel_id} successfully cancelled."
    else:
        conn.close()
        return f"No hotel found with ID {hotel_id}."