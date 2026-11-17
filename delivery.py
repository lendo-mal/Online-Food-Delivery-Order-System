"""delivery.py - cart, price, delivery fee and order status calculations."""

from datetime import datetime
from menu import (RESTAURANTS, DELIVERY_ZONES, MIN_DISTANCE_KM, MAX_DISTANCE_KM,
                  MAX_QUANTITY, TRANSITIONS, FINISHED_STATUSES,
                  CUSTOMER_EDITABLE_STATUSES)


def build_item(restaurant_key, meal_code, size_code, drink_code, side_code,
               extra_codes, quantity):
    """Validate the choices and return one cart item (a dictionary)."""
    restaurant = RESTAURANTS.get(restaurant_key)
    if restaurant is None:
        raise ValueError("Restaurant does not exist.")
    meal = restaurant["meals"].get(meal_code)
    if meal is None:
        raise ValueError("Menu code '" + str(meal_code) + "' does not exist.")
    if quantity < 1 or quantity > MAX_QUANTITY:
        raise ValueError("Quantity must be between 1 and " + str(MAX_QUANTITY) + ".")
    if size_code not in meal["sizes"]:
        raise ValueError("Invalid size option.")
    if drink_code not in meal["drinks"]:
        raise ValueError("Invalid drink option.")
    if side_code not in meal["sides"]:
        raise ValueError("Invalid side dish option.")

    extra_names = []
    unique_codes = []
    extras_total = 0.0
    for code in extra_codes:
        if code not in meal["extras"]:
            raise ValueError("Invalid extra option '" + str(code) + "'.")
        if code in unique_codes:
            continue                       # ignore duplicates
        unique_codes.append(code)
        name, price = meal["extras"][code]  # tuple unpacking
        extra_names.append(name)
        extras_total += price

    size_name, size_price = meal["sizes"][size_code]
    drink_name, drink_price = meal["drinks"][drink_code]
    side_name, side_price = meal["sides"][side_code]
    unit_price = meal["price"] + size_price + drink_price + side_price + extras_total

    return {
        "meal_code": meal_code, "meal_name": meal["name"], "base_price": meal["price"],
        "size_code": size_code, "size": size_name,
        "drink_code": drink_code, "drink": drink_name,
        "side_code": side_code, "side": side_name,
        "extra_codes": unique_codes, "extras": extra_names,
        "unit_price": unit_price, "quantity": quantity,
        "line_total": unit_price * quantity,
    }


def add_to_cart(cart, restaurant_key, meal_code, size_code, drink_code,
                side_code, extra_codes, quantity):
    """Add a customized meal to the cart (a list of dictionaries)."""
    item = build_item(restaurant_key, meal_code, size_code, drink_code,
                      side_code, extra_codes, quantity)
    cart.append(item)
    return item


def calculate_subtotal(cart):
    """Return the total price of all items in the cart."""
    total = 0.0
    for item in cart:
        total += item["line_total"]
    return total


def get_delivery_zone(distance_km):
    """Return (zone name, fee) for a distance. Raises ValueError if not allowed."""
    # "not (a <= x <= b)" also rejects nan/inf typed by mistake
    if not (MIN_DISTANCE_KM <= distance_km <= MAX_DISTANCE_KM):
        raise ValueError("Delivery distance must be from " + str(MIN_DISTANCE_KM) +
                         " km to " + str(MAX_DISTANCE_KM) + " km.")
    for zone_name, zone in DELIVERY_ZONES.items():
        if distance_km <= zone["max_km"]:
            if zone["fee"] < 0:
                raise ValueError("Invalid delivery fee set for " + zone_name + ".")
            return zone_name, zone["fee"]
    raise ValueError("No delivery zone covers " + str(distance_km) + " km.")


def calculate_delivery_fee(distance_km):
    """Return the delivery fee for a distance in kilometres."""
    return get_delivery_zone(distance_km)[1]


def build_order(order_id, customer, location, order_type, restaurant_key,
                distance_km, cart):
    """Combine everything into one order dictionary."""
    if len(cart) == 0:
        raise ValueError("An empty order cannot be confirmed.")
    restaurant = RESTAURANTS.get(restaurant_key)
    if restaurant is None:
        raise ValueError("Restaurant does not exist.")

    if order_type == "Delivery":
        zone, fee = get_delivery_zone(distance_km)
    else:                       # Pickup: no distance, zone or fee
        location, distance_km, zone, fee = "N/A", 0.0, "N/A", 0.0

    subtotal = calculate_subtotal(cart)
    return {
        "order_id": order_id,
        "customer": customer,
        "restaurant_key": restaurant_key,
        "restaurant": restaurant["name"],
        "order_type": order_type,
        "location": location,
        "distance_km": distance_km,
        "delivery_zone": zone,
        "delivery_fee": fee,
        "items": list(cart),
        "subtotal": subtotal,
        "total": subtotal + fee,
        "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Pending",
        "rider": None,
    }


def recalculate_order(order):
    """Refresh subtotal and total after the items changed."""
    order["subtotal"] = calculate_subtotal(order["items"])
    order["total"] = order["subtotal"] + order["delivery_fee"]


# ---------------- status rules ----------------

def allowed_next_statuses(order):
    """List of statuses this order may move to next."""
    return TRANSITIONS[order["order_type"]].get(order["status"], [])


def is_finished(order):
    return order["status"] in FINISHED_STATUSES


def customer_can_edit(order):
    return order["status"] in CUSTOMER_EDITABLE_STATUSES


def edit_block_message(order):
    """Explain why a customer cannot change this order."""
    label = "Order #" + str(order["order_id"])
    if is_finished(order):
        return label + " is already " + order["status"].lower() + " and cannot be changed."
    return label + " is already '" + order["status"] + \
        "' (being prepared or dispatched) and can no longer be changed."
