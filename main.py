"""main.py - console program for an online food delivery system."""

from customer import customer_console
from admin import admin_console


def main():
    while True:
        print("\n========== ONLINE FOOD DELIVERY SYSTEM ==========\n")
        print("1. Customer Console")
        print("2. Admin / Staff Console")
        print("0. Exit")
        choice = input("\nSelect option: ").strip()
        if choice == "1":
            customer_console()
        elif choice == "2":
            admin_console()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 0, 1 or 2.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram closed. Goodbye!")
