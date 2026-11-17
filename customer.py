"""customer.py - Customer Console: new orders, order history, manage orders."""

from menu import RESTAURANTS, MAX_QUANTITY, MIN_DISTANCE_KM, MAX_DISTANCE_KM
from delivery import (add_to_cart, build_item, build_order, get_delivery_zone,
                      recalculate_order, customer_can_edit, edit_block_message)
from storage import (save_order, next_order_id, load_orders, find_order,
                     update_order)
from helpers import (money, read_text, read_number, read_choice, confirm,
                     print_order, print_order_table)

RECENT_LIMIT = 10   # how many latest orders "View Recent Orders" lists


# ---------------- small selection helpers ----------------

def choose_one(title, options):
    """Show options (code -> (name, price)) and return the chosen code."""
    print("\n" + title)
    for code, (name, price) in options.items():
        extra = "" if price == 0 else "  (+" + money(price) + ")"
        print("  " + code + ". " + name + extra)
    return read_choice("Select: ", list(options.keys()))


def choose_extras(options):
    """Let the customer pick any number of extras. Returns a list of codes."""
    print("\nOptional extras / upgrades:")
    print("  0. No extras")
    for code, (name, price) in options.items():
        print("  " + code + ". " + name + "  (+" + money(price) + ")")
    while True:
        text = input("Enter codes separated by commas (e.g. 1,3) or 0 for none: ").strip()
        if text == "0":
            return []
        codes = [part.strip() for part in text.split(",")]
        valid = True
        for code in codes:
            if code not in options:
                valid = False
        if valid:
            return codes
        print("Invalid extra. Please use only the listed codes.")


def read_quantity():
    while True:
        quantity = read_number("Quantity: ", int)
        if 1 <= quantity <= MAX_QUANTITY:
            return quantity
        print("Quantity must be between 1 and " + str(MAX_QUANTITY) + ".")


def choose_item_number(items, prompt):
    """Show numbered items. Returns the list index, or None if the user backs out."""
    print()
    for number in range(len(items)):
        item = items[number]
        print(str(number + 1) + ". " + item["meal_name"] + " x" + str(item["quantity"]) +
              " - " + money(item["line_total"]))
    valid = [str(number) for number in range(0, len(items) + 1)]
    choice = read_choice(prompt + " (0 to go back): ", valid)
    if choice == "0":
        return None
    return int(choice) - 1


# ---------------- ordering helpers ----------------

def show_restaurant_meals(restaurant_key):
    restaurant = RESTAURANTS[restaurant_key]
    print("\n--- " + restaurant["name"].upper() + " COMBO MEALS ---")
    for code, meal in restaurant["meals"].items():
        print(code + ". " + meal["name"] + " - " + money(meal["price"]))


def customize_meal(restaurant_key, meal_code):
    """Ask for every customization. Returns (size, drink, side, extras, quantity)."""
    meal = RESTAURANTS[restaurant_key]["meals"][meal_code]
    print("\nCustomizing: " + meal["name"] + " (base " + money(meal["price"]) + ")")
    size = choose_one("Choose size:", meal["sizes"])
    drink = choose_one("Choose drink:", meal["drinks"])
    side = choose_one("Choose side dish:", meal["sides"])
    extras = choose_extras(meal["extras"])
    quantity = read_quantity()
    return size, drink, side, extras, quantity


def add_meals(restaurant_key, cart):
    """Keep adding customized meals to cart until the customer types 'done'."""
    show_restaurant_meals(restaurant_key)
    meals = RESTAURANTS[restaurant_key]["meals"]
    while True:
        code = input("\nEnter meal code (or 'done'): ").strip()
        if code.lower() == "done":
            break
        if code not in meals:
            print("Error: Menu code '" + code + "' does not exist.")
            continue
        choices = customize_meal(restaurant_key, code)
        try:
            item = add_to_cart(cart, restaurant_key, code, *choices)
            print("Added: " + item["meal_name"] + " x" + str(item["quantity"]) +
                  " - " + money(item["line_total"]))
            show_restaurant_meals(restaurant_key)
        except ValueError as error:
            print("Error:", error)


def read_distance():
    """Ask for the distance until it is inside a delivery zone."""
    print("We deliver from " + str(MIN_DISTANCE_KM) + " km to " + str(MAX_DISTANCE_KM) + " km.")
    while True:
        distance = read_number("Delivery distance in km: ", float)
        try:
            zone, fee = get_delivery_zone(distance)
            print(zone + " - delivery fee " + money(fee))
            return distance
        except ValueError as error:
            print("Error:", error)


# ---------------- A. SET UP A NEW ORDER ----------------

def take_order():
    print("\n--- NEW ORDER ---")
    # Step 1: order type
    print("1. Delivery")
    print("2. Pickup")
    print("0. Cancel")
    choice = read_choice("Select order type: ", ["0", "1", "2"])
    if choice == "0":
        return
    order_type = "Delivery" if choice == "1" else "Pickup"

    customer = read_text("Your name: ")
    location = "N/A"
    distance = 0.0
    if order_type == "Delivery":
        location = read_text("Delivery address/landmark: ")
        distance = read_distance()

    # Step 2: restaurant
    print("\n--- SELECT RESTAURANT ---")
    for code, restaurant in RESTAURANTS.items():
        print(code + ". " + restaurant["name"])
    print("0. Cancel")
    restaurant_key = read_choice("Select restaurant: ", ["0"] + list(RESTAURANTS.keys()))
    if restaurant_key == "0":
        return

    # Steps 3 and 4: add meals, then review
    cart = []
    while True:
        add_meals(restaurant_key, cart)
        while True:
            if len(cart) == 0:
                print("\nYour order is empty. Please add at least one meal.")
                break
            try:
                draft = build_order(None, customer, location, order_type,
                                    restaurant_key, distance, cart)
            except ValueError as error:
                print("Error:", error)
                return
            print_order(draft, "ORDER SUMMARY (REVIEW)")
            print("1. Confirm order")
            print("2. Add more meals")
            print("3. Remove a meal")
            print("4. Cancel this order")
            action = read_choice("Select option: ", ["1", "2", "3", "4"])
            if action == "1":
                confirm_order(customer, location, order_type, restaurant_key,
                              distance, cart)
                return
            if action == "2":
                break
            if action == "3":
                index = choose_item_number(cart, "Meal number to remove")
                if index is not None:
                    removed = cart.pop(index)
                    print("Removed: " + removed["meal_name"])
            if action == "4":
                if confirm("Cancel this whole order?"):
                    print("Order cancelled.")
                    return


# Step 5
def confirm_order(customer, location, order_type, restaurant_key, distance, cart):
    try:
        order = build_order(next_order_id(), customer, location, order_type,
                            restaurant_key, distance, cart)
    except ValueError as error:
        print("Error:", error)
        return
    if save_order(order):
        print_order(order, "RECEIPT")
        print("Order #" + str(order["order_id"]) + " was saved successfully. Status: Pending.")
    else:
        print("Your order could not be saved. Please try again.")


# ---------------- B. VIEW RECENT ORDERS ----------------

def ask_for_order(prompt):
    """Ask for an order ID until a saved order is found. Returns None for 0."""
    while True:
        order_id = read_number(prompt, int)
        if order_id == 0:
            return None
        order = find_order(order_id)
        if order is not None:
            return order
        print("Error: Order #" + str(order_id) + " was not found.")


def order_belongs_to_customer(order, customer_name):
    return str(order.get("customer", "")).strip().casefold() == customer_name.strip().casefold()


def ask_for_customer_order(prompt, customer_name):
    """Ask for an order ID belonging to the named customer. Returns None for 0."""
    while True:
        order_id = read_number(prompt, int)
        if order_id == 0:
            return None
        order = find_order(order_id)
        if order is not None and order_belongs_to_customer(order, customer_name):
            return order
        print("Error: no matching order was found for that customer name.")


def view_orders():
    customer_name = read_text("Enter the customer name on the order: ")
    orders = [order for order in load_orders()
              if order_belongs_to_customer(order, customer_name)]
    if len(orders) == 0:
        print("\nNo saved orders found for that customer name.")
        return
    recent = orders[-RECENT_LIMIT:]
    recent.reverse()                     # newest first
    print("\n--- RECENT ORDERS (latest " + str(RECENT_LIMIT) + ") ---")
    print_order_table(recent)
    order = ask_for_customer_order(
        "\nEnter order ID to view details (0 to go back): ", customer_name)
    if order is not None:
        print_order(order, "ORDER DETAILS")


# ---------------- C. MANAGE EXISTING ORDERS ----------------

def save_changes(order):
    """Recalculate the totals and update the saved record."""
    recalculate_order(order)
    if update_order(order):
        print("Order #" + str(order["order_id"]) + " updated. New total: " +
              money(order["total"]))
    else:
        print("Error: the changes could not be saved.")


def add_items_to_order(order):
    items = list(order["items"])          # work on a copy until confirmed
    before = len(items)
    add_meals(order["restaurant_key"], items)
    if len(items) == before:
        print("No items were added.")
    elif confirm("Save the added items to this order?"):
        order["items"] = items
        save_changes(order)
    else:
        print("Changes discarded.")


def modify_items_in_order(order):
    restaurant_key = order["restaurant_key"]
    index = choose_item_number(order["items"], "Meal number to modify")
    if index is None:
        return
    item = order["items"][index]
    print("\nWhat do you want to change?")
    print("1. Combo meal")
    print("2. Size")
    print("3. Drink")
    print("4. Side dish")
    print("5. Extras")
    print("6. Quantity")
    print("0. Back")
    change = read_choice("Select option: ", ["0", "1", "2", "3", "4", "5", "6"])
    if change == "0":
        return

    meal_key = item["meal_code"]
    size, drink, side = item["size_code"], item["drink_code"], item["side_code"]
    extras, quantity = item["extra_codes"], item["quantity"]
    try:
        if change == "1":
            show_restaurant_meals(restaurant_key)
            meals = RESTAURANTS[restaurant_key]["meals"]
            meal_key = read_choice("New meal code: ", list(meals.keys()))
            size, drink, side, extras, quantity = customize_meal(restaurant_key, meal_key)
        else:
            meal = RESTAURANTS[restaurant_key]["meals"][meal_key]
            if change == "2":
                size = choose_one("Choose size:", meal["sizes"])
            elif change == "3":
                drink = choose_one("Choose drink:", meal["drinks"])
            elif change == "4":
                side = choose_one("Choose side dish:", meal["sides"])
            elif change == "5":
                extras = choose_extras(meal["extras"])
            else:
                quantity = read_quantity()
        new_item = build_item(restaurant_key, meal_key, size, drink, side, extras, quantity)
    except (ValueError, KeyError) as error:
        print("Error: this item could not be changed (" + str(error) + ").")
        return

    print("\nNew version: " + new_item["meal_name"] + " x" + str(new_item["quantity"]) +
          " - " + money(new_item["line_total"]))
    if confirm("Save this change?"):
        order["items"][index] = new_item
        save_changes(order)
    else:
        print("Change discarded.")


def remove_items_from_order(order):
    if len(order["items"]) == 1:
        print("This order has only one item. Removing it would leave an empty order -")
        print("use 'Cancel Order' instead.")
        return
    index = choose_item_number(order["items"], "Meal number to remove")
    if index is None:
        return
    item = order["items"][index]
    if confirm("Remove " + item["meal_name"] + " x" + str(item["quantity"]) + "?"):
        order["items"].pop(index)
        save_changes(order)
    else:
        print("Nothing was removed.")


def cancel_order(order):
    if confirm("Cancel Order #" + str(order["order_id"]) + "? This cannot be undone"):
        order["status"] = "Cancelled"
        if update_order(order):
            print("Order #" + str(order["order_id"]) + " has been cancelled.")
        else:
            print("Error: the cancellation could not be saved.")
    else:
        print("The order was not cancelled.")


def manage_one_order(order):
    while True:
        print_order(order, "MANAGING ORDER #" + str(order["order_id"]))
        print("1. Add items")
        print("2. Modify items")
        print("3. Remove items")
        print("4. Cancel order")
        print("0. Back")
        choice = read_choice("Select option: ", ["0", "1", "2", "3", "4"])
        if choice == "0":
            return
        if choice == "1":
            add_items_to_order(order)
        elif choice == "2":
            modify_items_in_order(order)
        elif choice == "3":
            remove_items_from_order(order)
        else:
            cancel_order(order)
            if order["status"] == "Cancelled":
                return


def manage_orders():
    print("\n--- MANAGE EXISTING ORDERS ---")
    customer_name = read_text("Enter the customer name on the order: ")
    while True:
        order = ask_for_customer_order(
            "\nEnter order ID to manage (0 to go back): ", customer_name)
        if order is None:
            return
        if not customer_can_edit(order):
            print(edit_block_message(order))
        elif order["restaurant_key"] is None:
            print("This order was saved by an older version and cannot be edited.")
        else:
            manage_one_order(order)
            return


# ---------------- CUSTOMER CONSOLE MENU ----------------

def customer_console():
    while True:
        print("\n========== CUSTOMER CONSOLE ==========\n")
        print("1. Set Up a New Order")
        print("2. View Recent Orders")
        print("3. Manage Existing Orders")
        print("0. Back to Main Menu")
        choice = input("\nSelect option: ").strip()
        if choice == "1":
            take_order()
        elif choice == "2":
            view_orders()
        elif choice == "3":
            manage_orders()
        elif choice == "0":
            break
        else:
            print("Invalid option. Please choose 0-3.")
