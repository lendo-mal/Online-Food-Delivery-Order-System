"""storage.py - saves and loads orders using a text file (one JSON order per line)."""

import json

ORDERS_FILE = "orders.txt"


def normalize_order(order):
    """Fill in fields that orders saved by the older version do not have."""
    defaults = {"customer": "Unknown", "restaurant_key": None, "restaurant": "Unknown",
                "order_type": "Delivery", "location": "N/A", "distance_km": 0.0,
                "delivery_zone": "N/A", "delivery_fee": 0.0, "items": [],
                "subtotal": 0.0, "total": 0.0, "date_time": "Unknown",
                "status": "Pending", "rider": None}
    for key, value in defaults.items():
        order.setdefault(key, value)
    for item in order["items"]:
        item.setdefault("meal_name", item.get("name", "Unknown item"))
        item.setdefault("unit_price", item.get("price", 0.0))
        item.setdefault("size", "-")
        item.setdefault("drink", "-")
        item.setdefault("side", "-")
        item.setdefault("extras", [])
        item.setdefault("quantity", 1)
        item.setdefault("line_total", item["unit_price"] * item["quantity"])
    return order


def save_order(order, filename=ORDERS_FILE):
    """Append one NEW order to the file (mode 'a' keeps old orders)."""
    try:
        with open(filename, "a") as file:
            file.write(json.dumps(order) + "\n")
        return True
    except OSError as error:
        print("Could not save the order:", error)
        return False


def load_orders(filename=ORDERS_FILE):
    """Read all saved orders. Returns an empty list if the file is missing."""
    orders = []
    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if line == "":
                    continue
                try:
                    orders.append(normalize_order(json.loads(line)))
                except (json.JSONDecodeError, AttributeError, TypeError):
                    print("Skipped a damaged line in " + filename)
    except FileNotFoundError:
        pass   # first run: no orders yet
    except OSError as error:
        print("Could not read " + filename + ":", error)
    return orders


def save_all_orders(orders, filename=ORDERS_FILE):
    """Rewrite the whole file (mode 'w'). Used when an order is updated."""
    try:
        with open(filename, "w") as file:
            for order in orders:
                file.write(json.dumps(order) + "\n")
        return True
    except OSError as error:
        print("Could not save the orders:", error)
        return False


def find_order(order_id, filename=ORDERS_FILE):
    """Return the saved order with this ID, or None."""
    for order in load_orders(filename):
        if order["order_id"] == order_id:
            return order
    return None


def update_order(order, filename=ORDERS_FILE):
    """Replace the saved record that has the same order ID (no duplicates)."""
    orders = load_orders(filename)
    for index in range(len(orders)):
        if orders[index]["order_id"] == order["order_id"]:
            orders[index] = order
            return save_all_orders(orders, filename)
    print("Order #" + str(order["order_id"]) + " was not found in storage.")
    return False


def next_order_id(filename=ORDERS_FILE):
    """Return the next order number (highest saved ID + 1)."""
    highest = 0
    for order in load_orders(filename):
        if order["order_id"] > highest:
            highest = order["order_id"]
    return highest + 1
