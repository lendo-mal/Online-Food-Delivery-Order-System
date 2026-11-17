"""helpers.py - input reading and order display shared by both consoles."""


def money(amount):
    return "PHP " + format(amount, ",.2f")


def read_text(prompt):
    """Keep asking until the user types something that is not empty."""
    while True:
        value = input(prompt).strip()
        if value == "":
            print("Input cannot be empty.")
        else:
            return value


def read_number(prompt, number_type):
    """Keep asking until the user types a valid number."""
    while True:
        try:
            return number_type(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")


def read_choice(prompt, valid_choices):
    """Keep asking until the answer is one of valid_choices (a list of strings)."""
    while True:
        value = input(prompt).strip()
        if value in valid_choices:
            return value
        print("Invalid choice. Please select one of: " + ", ".join(valid_choices))


def confirm(question):
    """Ask a yes/no question. Returns True for yes."""
    while True:
        answer = input(question + " (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please type y or n.")


def print_order_table(orders):
    """Print a list of orders as one table row each."""
    print("\n" + "ID".ljust(5) + "Customer".ljust(16) + "Restaurant".ljust(13) +
          "Date/Time".ljust(21) + "Type".ljust(10) + "Total".rjust(11) + "  Status")
    print("-" * 90)
    for order in orders:
        print(str(order["order_id"]).ljust(5) + order["customer"][:14].ljust(16) +
              order["restaurant"][:11].ljust(13) + str(order["date_time"]).ljust(21) +
              order["order_type"].ljust(10) + format(order["total"], ",.2f").rjust(11) +
              "  " + order["status"])


def print_order(order, title):
    """Print the complete details of one order (also used as the receipt)."""
    line = "=" * 48
    order_id = "(assigned when confirmed)" if order["order_id"] is None else order["order_id"]
    print("\n" + line)
    print(title.center(48))
    print(line)
    print("Order ID   :", order_id)
    print("Customer   :", order["customer"])
    print("Restaurant :", order["restaurant"])
    print("Order type :", order["order_type"])
    print("Date/Time  :", order["date_time"])
    print("Status     :", order["status"])
    if order["order_type"] == "Delivery":
        print("Deliver to :", order["location"])
        print("Distance   :", order["distance_km"], "km (" + order["delivery_zone"] + ")")
        if order["rider"] is None:
            print("Rider      : Not assigned yet")
        else:
            print("Rider      :", "#" + order["rider"]["rider_id"], order["rider"]["name"])
    print("-" * 48)
    number = 1
    for item in order["items"]:
        print(str(number) + ". " + item["meal_name"] + " x" + str(item["quantity"]))
        print("   Size: " + item["size"] + " | Drink: " + item["drink"] +
              " | Side: " + item["side"])
        if len(item["extras"]) > 0:
            print("   Extras: " + ", ".join(item["extras"]))
        print("   " + money(item["unit_price"]) + " each = " + money(item["line_total"]))
        number += 1
    print("-" * 48)
    print("Subtotal     : " + money(order["subtotal"]).rjust(15))
    if order["order_type"] == "Delivery":
        print("Delivery fee : " + money(order["delivery_fee"]).rjust(15))
    print("GRAND TOTAL  : " + money(order["total"]).rjust(15))
    print(line)
