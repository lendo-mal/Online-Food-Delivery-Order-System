"""admin.py - Admin/Staff Delivery Dispatch Console."""

from datetime import datetime
from delivery import allowed_next_statuses, is_finished
from storage import load_orders, update_order
from riders import get_available_riders, find_rider
from helpers import (money, read_choice, confirm, print_order, print_order_table)
from customer import ask_for_order     # same "enter an order ID" helper


# ---------------- A. VIEW PENDING ORDERS ----------------

def view_pending_orders():
    """Show orders that are awaiting processing."""
    waiting = [order for order in load_orders() if order["status"] == "Pending"]
    if len(waiting) == 0:
        print("\nNo pending orders.")
        return
    print("\n--- PENDING ORDERS ---")
    print_order_table(waiting)
    order = ask_for_order("\nEnter order ID to view details (0 to go back): ")
    if order is not None:
        print_order(order, "ORDER DETAILS")


# ---------------- B. ASSIGN RIDER ----------------

def assign_rider():
    order = ask_for_order("\nEnter order ID to assign a rider (0 to go back): ")
    if order is None:
        return
    if order["order_type"] == "Pickup":
        print("Error: Pickup orders do not need a rider.")
        return
    if is_finished(order):
        print("Error: Order #" + str(order["order_id"]) + " is already " +
              order["status"].lower() + ".")
        return

    if order["rider"] is not None:
        print("Order #" + str(order["order_id"]) + " already has rider #" +
              order["rider"]["rider_id"] + " " + order["rider"]["name"] + ".")
        if not confirm("Change the assigned rider?"):
            print("Assignment unchanged.")
            return

    unavailable_rider_ids = [
        saved_order["rider"]["rider_id"]
        for saved_order in load_orders()
        if saved_order["order_id"] != order["order_id"]
        and saved_order["order_type"] == "Delivery"
        and not is_finished(saved_order)
        and saved_order["rider"] is not None
    ]
    riders = get_available_riders(unavailable_rider_ids)
    if len(riders) == 0:
        print("Error: no riders are available right now.")
        return
    print("\n--- AVAILABLE RIDERS ---")
    for rider in riders:
        print(rider["rider_id"] + ". " + rider["name"])
    valid_ids = [rider["rider_id"] for rider in riders]
    choice = read_choice("Select rider ID (0 to cancel): ", ["0"] + valid_ids)
    if choice == "0":
        return
    rider = find_rider(choice)
    if rider is None or not rider["available"]:      # extra safety check
        print("Error: that rider cannot be assigned.")
        return

    order["rider"] = {"rider_id": rider["rider_id"], "name": rider["name"]}
    if update_order(order):
        print("Rider " + rider["name"] + " was assigned to Order #" +
              str(order["order_id"]) + ".")
    else:
        print("Error: the assignment could not be saved.")


# ---------------- C. UPDATE DELIVERY STATUS ----------------

def update_status():
    order = ask_for_order("\nEnter order ID to update (0 to go back): ")
    if order is None:
        return
    if is_finished(order):
        print("Error: Order #" + str(order["order_id"]) + " is already " +
              order["status"] + " and cannot be processed again.")
        return

    print("\nOrder #" + str(order["order_id"]) + " (" + order["order_type"] + ")")
    print("Current status:", order["status"])
    allowed = allowed_next_statuses(order)
    print("Available next statuses:")
    valid = []
    for index, name in enumerate(allowed, 1):
        number = str(index)
        valid.append(number)
        print("  " + number + ". " + name)
    choice = read_choice("Select new status (0 to cancel): ", ["0"] + valid)
    if choice == "0":
        return
    new_status = allowed[int(choice) - 1]

    if new_status == "Out for Delivery" and order["rider"] is None:
        print("Error: assign a rider to this order before sending it out.")
        return
    if new_status == "Cancelled" and not confirm("Cancel this order?"):
        print("Status unchanged.")
        return

    order["status"] = new_status
    if update_order(order):
        print("Order #" + str(order["order_id"]) + " is now '" + new_status + "'.")
    else:
        print("Error: the new status could not be saved.")


# ---------------- D. DAILY REPORT ----------------

def view_daily_report():
    today = datetime.now().strftime("%Y-%m-%d")
    todays = [order for order in load_orders() if str(order["date_time"]).startswith(today)]

    completed = cancelled = pending = in_progress = 0
    deliveries = pickups = 0
    sales = fees = 0.0
    for order in todays:
        if order["status"] == "Delivered":
            completed += 1
            sales += order["total"]            # only completed orders count as sales
            fees += order["delivery_fee"]
        elif order["status"] == "Cancelled":
            cancelled += 1
        elif order["status"] == "Pending":
            pending += 1
        else:
            in_progress += 1
        if order["order_type"] == "Delivery":
            deliveries += 1
        else:
            pickups += 1

    print("\n========== DAILY DELIVERY REPORT ==========")
    print("Date:", today)
    print("-" * 43)
    print("Total orders received today :", len(todays))
    print("Completed orders            :", completed)
    print("Cancelled orders            :", cancelled)
    print("Pending orders              :", pending)
    print("In progress (other statuses):", in_progress)
    print("Delivery orders             :", deliveries)
    print("Pickup orders               :", pickups)
    print("-" * 43)
    print("Total sales (completed)     :", money(sales))
    print("Delivery fees (completed)   :", money(fees))
    print("=" * 43)


# ---------------- ADMIN CONSOLE MENU ----------------

def admin_console():
    while True:
        print("\n========== DELIVERY DISPATCH CONSOLE ==========\n")
        print("1. View Pending Orders")
        print("2. Assign Rider to Order")
        print("3. Update Delivery Status")
        print("4. View Daily Delivery Report")
        print("0. Logout")
        choice = input("\nSelect option: ").strip()
        if choice == "1":
            view_pending_orders()
        elif choice == "2":
            assign_rider()
        elif choice == "3":
            update_status()
        elif choice == "4":
            view_daily_report()
        elif choice == "0":
            print("Logged out.")
            break
        else:
            print("Invalid option. Please choose 1, 2, 3, 4 or 0.")
