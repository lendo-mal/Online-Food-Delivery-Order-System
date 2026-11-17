"""menu.py - restaurants, meals, customization options and delivery settings."""


def make_meal(name, price, sizes, drinks, sides, extras):
    """Build one combo meal. Every option group is a dictionary:
    key = option code, value = tuple (option name, extra price in PHP).
    The first code of sizes/drinks/sides is the default (usually PHP 0.00)."""
    return {"name": name, "price": price, "sizes": sizes,
            "drinks": drinks, "sides": sides, "extras": extras}


# ---------------- JOLLIBEE ----------------
J_SIZES = {"1": ("Regular", 0.00), "2": ("Large", 20.00)}
J_DRINKS = {"1": ("Iced Tea", 0.00), "2": ("Coke", 0.00), "3": ("Pineapple Juice", 15.00)}
J_SIDES = {"1": ("No side", 0.00), "2": ("Crispy Fries", 35.00), "3": ("Creamy Macaroni Soup", 45.00)}
J_PASTA_SIDES = {"1": ("No side", 0.00), "2": ("Garlic Bread", 25.00), "3": ("Crispy Fries", 35.00)}

# ---------------- McDONALD'S ----------------
M_SIZES = {"1": ("Medium", 0.00), "2": ("Large", 25.00)}
M_DRINKS = {"1": ("Coke", 0.00), "2": ("Sprite", 0.00), "3": ("Coke Float", 25.00)}
M_BURGER_SIDES = {"1": ("Regular Fries", 0.00), "2": ("Corn Cup", 10.00), "3": ("Chicken McNuggets 4pc", 60.00)}
M_RICE_SIDES = {"1": ("Steamed Rice", 0.00), "2": ("Fries instead of rice", 15.00)}

# ---------------- CHOWKING ----------------
C_SIZES = {"1": ("Regular", 0.00), "2": ("Large", 25.00)}
C_DRINKS = {"1": ("Iced Tea", 0.00), "2": ("Coke", 0.00), "3": ("Buko Pandan Shake", 35.00)}

# Dictionary of dictionaries: key = restaurant code
RESTAURANTS = {
    "1": {
        "name": "Jollibee",
        "meals": {
            "1": make_meal("Chickenjoy Solo", 99.00, J_SIZES, J_DRINKS, J_SIDES,
                           {"1": ("Extra Gravy", 10.00), "2": ("Extra Rice", 20.00),
                            "3": ("Peach Mango Pie", 40.00)}),
            "2": make_meal("Jolly Spaghetti Solo", 85.00, J_SIZES, J_DRINKS, J_PASTA_SIDES,
                           {"1": ("Extra Hotdog", 25.00), "2": ("Extra Cheese", 15.00),
                            "3": ("Peach Mango Pie", 40.00)}),
            "3": make_meal("Yumburger Meal", 79.00, J_SIZES, J_DRINKS, J_SIDES,
                           {"1": ("Extra Cheese Slice", 12.00), "2": ("Extra Patty", 35.00),
                            "3": ("Peach Mango Pie", 40.00)}),
        },
    },
    "2": {
        "name": "McDonald's",
        "meals": {
            "1": make_meal("Big Mac Meal", 175.00, M_SIZES, M_DRINKS, M_BURGER_SIDES,
                           {"1": ("Extra Cheese", 15.00), "2": ("Extra Patty", 55.00),
                            "3": ("Apple Pie", 45.00)}),
            "2": make_meal("McChicken Meal", 150.00, M_SIZES, M_DRINKS, M_BURGER_SIDES,
                           {"1": ("Extra Cheese", 15.00), "2": ("Extra Sauce", 8.00),
                            "3": ("Apple Pie", 45.00)}),
            "3": make_meal("Chicken McDo 2pc with Rice", 140.00, M_SIZES, M_DRINKS, M_RICE_SIDES,
                           {"1": ("Extra Gravy", 12.00), "2": ("Extra Rice", 25.00),
                            "3": ("Apple Pie", 45.00)}),
        },
    },
    "3": {
        "name": "Chowking",
        "meals": {
            "1": make_meal("Chicken Chao Fan Meal", 119.00, C_SIZES, C_DRINKS,
                           {"1": ("No side", 0.00), "2": ("Siomai 2pc", 40.00),
                            "3": ("Lumpiang Shanghai 3pc", 45.00)},
                           {"1": ("Extra Egg", 15.00), "2": ("Chili Garlic Sauce", 5.00),
                            "3": ("Halo-Halo", 75.00)}),
            "2": make_meal("Beef Noodle Mami Meal", 109.00, C_SIZES, C_DRINKS,
                           {"1": ("No side", 0.00), "2": ("Siopao Asado", 55.00),
                            "3": ("Siomai 2pc", 40.00)},
                           {"1": ("Extra Egg", 15.00), "2": ("Extra Noodles", 30.00),
                            "3": ("Halo-Halo", 75.00)}),
            "3": make_meal("Pancit Canton Meal", 99.00, C_SIZES, C_DRINKS,
                           {"1": ("No side", 0.00), "2": ("Lumpiang Shanghai 3pc", 45.00),
                            "3": ("Siomai 2pc", 40.00)},
                           {"1": ("Extra Egg", 15.00), "2": ("Calamansi", 5.00),
                            "3": ("Halo-Halo", 75.00)}),
        },
    },
}

MAX_QUANTITY = 20      # most of one customized meal per line

# ---------------- DELIVERY ZONES ----------------
MIN_DISTANCE_KM = 1.0
MAX_DISTANCE_KM = 10.0

# Zones are checked in this order: a distance belongs to the first zone
# whose max_km it does not exceed. Change the fees here (PHP).
DELIVERY_ZONES = {
    "Zone 1": {"min_km": 1.0, "max_km": 5.0, "fee": 49.00},
    "Zone 2": {"min_km": 5.0, "max_km": 10.0, "fee": 89.00},
}

# ---------------- ORDER STATUS RULES ----------------
STATUS_LIST = ["Pending", "Confirmed", "Preparing", "Ready for Pickup",
               "Out for Delivery", "Delivered", "Cancelled"]   # numbers 1-7

FINISHED_STATUSES = ["Delivered", "Cancelled"]
CUSTOMER_EDITABLE_STATUSES = ["Pending", "Confirmed"]

# Allowed next statuses: order type -> current status -> list of next statuses
TRANSITIONS = {
    "Delivery": {
        "Pending": ["Confirmed", "Cancelled"],
        "Confirmed": ["Preparing", "Cancelled"],
        "Preparing": ["Out for Delivery", "Cancelled"],
        "Out for Delivery": ["Delivered"],
    },
    "Pickup": {
        "Pending": ["Confirmed", "Cancelled"],
        "Confirmed": ["Preparing", "Cancelled"],
        "Preparing": ["Ready for Pickup", "Cancelled"],
        "Ready for Pickup": ["Delivered"],   # "Delivered" = picked up / completed
    },
}
