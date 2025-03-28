"""
Trip recommendation tools for the Travel Assistant.
"""
from typing import List, Dict, Any, Optional

from langchain_core.tools import tool

from database.connection import get_connection


@tool
def search_trip_recommendations(
    location: Optional[str] = None,
    name: Optional[str] = None,
    keywords: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search for trip recommendations based on location, name, and keywords.

    Args:
        location: The location of the trip recommendation
        name: The name of the trip recommendation
        keywords: Comma-separated keywords associated with the trip recommendation

    Returns:
        A list of trip recommendation dictionaries matching the search criteria
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM trip_recommendations WHERE 1=1"
    params = []

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
        
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
        
    if keywords:
        keyword_list = keywords.split(",")
        keyword_conditions = " OR ".join(["keywords LIKE ?" for _ in keyword_list])
        query += f" AND ({keyword_conditions})"
        params.extend([f"%{keyword.strip()}%" for keyword in keyword_list])

    cursor.execute(query, params)
    results = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    
    conn.close()

    return [dict(zip(column_names, row)) for row in results]


@tool
def book_excursion(recommendation_id: int) -> str:
    """
    Book an excursion by its recommendation ID.

    Args:
        recommendation_id: The ID of the trip recommendation to book

    Returns:
        A message indicating whether the excursion was successfully booked
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE trip_recommendations SET booked = 1 WHERE id = ?", (recommendation_id,)
    )
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Excursion {recommendation_id} successfully booked."
    else:
        conn.close()
        return f"No excursion found with ID {recommendation_id}."


@tool
def update_excursion(recommendation_id: int, details: str) -> str:
    """
    Update an excursion's details by its ID.

    Args:
        recommendation_id: The ID of the excursion to update
        details: The new details of the excursion

    Returns:
        A message indicating whether the excursion was successfully updated
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE trip_recommendations SET details = ? WHERE id = ?",
        (details, recommendation_id),
    )
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Excursion {recommendation_id} successfully updated."
    else:
        conn.close()
        return f"No excursion found with ID {recommendation_id}."


@tool
def cancel_excursion(recommendation_id: int) -> str:
    """
    Cancel an excursion by its ID.

    Args:
        recommendation_id: The ID of the excursion to cancel

    Returns:
        A message indicating whether the excursion was successfully cancelled
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE trip_recommendations SET booked = 0 WHERE id = ?", (recommendation_id,)
    )
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Excursion {recommendation_id} successfully cancelled."
    else:
        conn.close()
        return f"No excursion found with ID {recommendation_id}."