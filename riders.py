"""riders.py - predefined rider list used for rider assignment."""

# List of dictionaries (no rider add/remove menus, as required)
RIDERS = [
    {"rider_id": "1", "name": "Juan Dela Cruz", "available": True},
    {"rider_id": "2", "name": "Mark Santos", "available": True},
    {"rider_id": "3", "name": "Paolo Reyes", "available": False},
    {"rider_id": "4", "name": "Carlo Mendoza", "available": True},
]


def get_available_riders(unavailable_rider_ids=None):
    """Return available riders, excluding those already assigned to active orders."""
    unavailable_rider_ids = unavailable_rider_ids or []
    return [rider for rider in RIDERS
            if rider["available"] and rider["rider_id"] not in unavailable_rider_ids]


def find_rider(rider_id):
    """Return the rider with this ID, or None."""
    for rider in RIDERS:
        if rider["rider_id"] == rider_id:
            return rider
    return None
