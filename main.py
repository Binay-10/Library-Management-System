"""
main.py
=======
Entry point for the University Library Management System.
Displays the interactive command-line interface, handles user inputs,
dispatches commands via Python 3.10+ pattern matching, and manages application lifecycle.
"""

from __future__ import annotations
import sys
from library import Library


def print_header(title: str) -> None:
    """Print a clean visual section header."""
    print(f"\n--- {title.upper()} ---")


def prompt_non_empty(prompt_text: str) -> str:
    """Prompt the user for input repeatedly until a non-empty string is provided.

    Args:
        prompt_text: The prompt message displayed to the user.

    Returns:
        str: Validated, trimmed input string.
    """
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("[!] Input cannot be blank. Please try again.")


def handle_borrow_book(library: Library) -> None:
    """Handle menu option 2: Borrowing a book."""
    print_header("Borrow a Book")
    isbn = prompt_non_empty("Enter Book ISBN: ")
    student_name = prompt_non_empty("Enter Student Name: ")

    success, message, _ = library.borrow_book(isbn, student_name)
    if success:
        print(f"\n[+] {message}")
    else:
        print(f"\n[-] {message}")


def handle_return_book(library: Library) -> None:
    """Handle menu option 3: Returning a book."""
    print_header("Return a Book")
    isbn = prompt_non_empty("Enter Book ISBN to return: ")

    success, message = library.return_book(isbn)
    if success:
        print(f"\n[+] {message}")
    else:
        print(f"\n[-] {message}")


def handle_add_book(library: Library) -> None:
    """Handle menu option 4: Adding a new book (Admin)."""
    print_header("Add New Book (Admin)")
    title = prompt_non_empty("Enter Book Title: ")
    author = prompt_non_empty("Enter Author Name: ")
    isbn = prompt_non_empty("Enter Book ISBN (e.g. 978-0134685991): ")

    success, message = library.add_book(title, author, isbn)
    if success:
        print(f"\n[+] {message}")
    else:
        print(f"\n[-] {message}")


def handle_search_book(library: Library) -> None:
    """Handle menu option 5: Searching for books in the catalog."""
    print_header("Search Catalog")
    print("Choose search criteria:")
    print("  1. Search by Title (case-insensitive, partial match)")
    print("  2. Search by Author (case-insensitive, partial match)")
    print("  3. Search by ISBN")
    print("  4. Universal Search (Title, Author, or ISBN)")
    print("  5. Return to Main Menu")

    search_choice = input("Select Search Criterion [1-5]: ").strip()
    if search_choice == "5":
        return

    field_map = {
        "1": ("title", "Enter Title keyword: "),
        "2": ("author", "Enter Author keyword: "),
        "3": ("isbn", "Enter ISBN query: "),
        "4": ("all", "Enter search query: "),
    }

    if search_choice not in field_map:
        print("[-] Invalid search criterion selected. Returning to main menu.")
        return

    field, prompt_str = field_map[search_choice]
    query = prompt_non_empty(prompt_str)

    results = library.search_book(query, search_type=field)
    print(f"\n--- Search Results for '{query}' (Found: {len(results)}) ---")
    if results:
        print(library.format_books_table(results))
    else:
        print(f"[-] No books found matching your query: '{query}'.")


def main() -> None:
    """Application main loop."""
    print("\nInitializing University Library Management System...")
    library = Library()

    menu_text = (
        "\n=== UNIVERSITY LIBRARY MANAGEMENT SYSTEM ===\n\n"
        "1. View All Books\n"
        "2. Borrow a Book\n"
        "3. Return a Book\n"
        "4. Add New Book (Admin)\n"
        "5. Search Book\n"
        "6. Exit\n"
    )

    while True:
        try:
            print(menu_text)
            choice = input("Select Option: ").strip()

            match choice:
                case "1":
                    print_header("Library Catalog")
                    library.display_books()

                case "2":
                    handle_borrow_book(library)

                case "3":
                    handle_return_book(library)

                case "4":
                    handle_add_book(library)

                case "5":
                    handle_search_book(library)

                case "6":
                    print("\nSaving catalog and shutting down...")
                    library.save_catalog()
                    print("Thank you for using the University Library Management System. Goodbye!\n")
                    break

                case _:
                    print("\n[!] Invalid selection. Please enter a number between 1 and 6.")

        except (KeyboardInterrupt, EOFError):
            print("\n\n[INFO] Session interrupted by user. Saving catalog safely before exiting...")
            library.save_catalog()
            print("Catalog saved. Goodbye!\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
