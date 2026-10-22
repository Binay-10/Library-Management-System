"""
library.py
==========
Defines the Library class that manages the book collection, search algorithms,
borrowing/returning workflows, and JSON file persistence.
"""

from __future__ import annotations
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from book import Book

# Configure module-level logger
logger = logging.getLogger(__name__)


class Library:
    """Manages the library catalog, operations, and file persistence.

    Attributes:
        catalog_path (Path): Path to the JSON catalog file.
        books (list[Book]): In-memory collection of Book objects.
    """

    DEFAULT_BORROW_DAYS: int = 14

    def __init__(self, catalog_path: Path | str | None = None) -> None:
        """Initialize the Library instance and load the catalog.

        Args:
            catalog_path: Optional custom path to library_catalog.json.
                          Defaults to 'library_catalog.json' in the same directory as this file.
        """
        if catalog_path is not None:
            self.catalog_path: Path = Path(catalog_path).resolve()
        else:
            self.catalog_path = Path(__file__).resolve().parent / "library_catalog.json"

        self.books: list[Book] = []
        self.load_catalog()

    # -------------------------------------------------------------------------
    # Catalog Persistence (JSON Load / Save)
    # -------------------------------------------------------------------------

    def get_initial_sample_books(self) -> list[Book]:
        """Generate the default initial sample books required for a fresh catalog.

        Returns:
            list[Book]: 3 curated sample books with consistent borrowing data.
        """
        sample_due_date = (datetime.now() + timedelta(days=self.DEFAULT_BORROW_DAYS)).strftime("%Y-%m-%d")

        return [
            Book(
                title="Clean Code",
                author="Robert Martin",
                isbn="978-0134685991",
                is_borrowed=False,
                borrowed_by=None,
                due_date=None,
            ),
            Book(
                title="Python Cookbook",
                author="David Beazley",
                isbn="978-0596517748",
                is_borrowed=True,
                borrowed_by="Jane Doe",
                due_date=sample_due_date,
            ),
            Book(
                title="The Pragmatic Programmer",
                author="Andy Hunt",
                isbn="978-0132350884",
                is_borrowed=False,
                borrowed_by=None,
                due_date=None,
            ),
        ]

    def load_catalog(self) -> None:
        """Load and reconstruct Book objects from the JSON catalog file.

        - If the file does not exist, initializes with standard sample data and saves.
        - If the file exists but contains invalid/malformed JSON, logs a warning
          and does NOT overwrite the file to prevent data loss.
        """
        if not self.catalog_path.exists():
            print(f"[INFO] Catalog file not found. Creating initial catalog at: {self.catalog_path.name}")
            self.books = self.get_initial_sample_books()
            self.save_catalog()
            return

        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                print(
                    f"[ERROR] Catalog file '{self.catalog_path.name}' is invalid (root is not a list). "
                    "Preserving file on disk; starting with an empty in-memory catalog."
                )
                self.books = []
                return

            loaded_books: list[Book] = []
            seen_isbns: set[str] = set()

            for idx, item in enumerate(data, start=1):
                try:
                    book = Book.from_dict(item)
                    normalized_isbn = book.isbn.strip().lower()
                    if normalized_isbn in seen_isbns:
                        print(f"[WARNING] Skipping duplicate ISBN '{book.isbn}' at record #{idx}.")
                        continue
                    seen_isbns.add(normalized_isbn)
                    loaded_books.append(book)
                except (ValueError, KeyError, TypeError) as err:
                    print(f"[WARNING] Skipping malformed book record #{idx}: {err}")

            self.books = loaded_books

        except json.JSONDecodeError as err:
            print(
                f"[ERROR] Failed to parse '{self.catalog_path.name}' (Malformed JSON: {err}). "
                "CRITICAL: The existing file will NOT be overwritten to prevent accidental data loss."
            )
            self.books = []
        except OSError as err:
            print(f"[ERROR] Could not read catalog file '{self.catalog_path.name}': {err}")
            self.books = []

    def save_catalog(self) -> bool:
        """Serialize all book records to the JSON catalog file.

        Returns:
            bool: True if save succeeded, False otherwise.
        """
        try:
            data = [book.to_dict() for book in self.books]
            # Write to file cleanly formatted
            with open(self.catalog_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except OSError as err:
            print(f"[ERROR] Failed to save catalog to '{self.catalog_path.name}': {err}")
            return False

    # -------------------------------------------------------------------------
    # Core Operations
    # -------------------------------------------------------------------------

    def find_book_by_isbn(self, isbn: str) -> Book | None:
        """Locate a book in the catalog by exact ISBN (normalized, case-insensitive).

        Args:
            isbn: The ISBN string to search for.

        Returns:
            Book instance if found, else None.
        """
        if not isbn or not isinstance(isbn, str):
            return None
        target = isbn.strip().lower()
        for book in self.books:
            if book.isbn.strip().lower() == target:
                return book
        return None

    def add_book(self, title: str, author: str, isbn: str) -> tuple[bool, str]:
        """Add a new book to the catalog after validating fields and checking for duplicates.

        Args:
            title: Title of the book.
            author: Author of the book.
            isbn: International Standard Book Number.

        Returns:
            tuple[bool, str]: (Success boolean, Status message)
        """
        # Validate inputs
        if not title or not title.strip():
            return False, "Validation Error: Book title cannot be empty."
        if not author or not author.strip():
            return False, "Validation Error: Book author cannot be empty."
        if not isbn or not isbn.strip():
            return False, "Validation Error: ISBN cannot be empty."

        clean_isbn = isbn.strip()
        if self.find_book_by_isbn(clean_isbn) is not None:
            return False, f"Duplicate ISBN Error: A book with ISBN '{clean_isbn}' already exists in the catalog."

        try:
            new_book = Book(
                title=title,
                author=author,
                isbn=clean_isbn,
                is_borrowed=False,
                borrowed_by=None,
                due_date=None,
            )
        except ValueError as err:
            return False, f"Validation Error: {err}"

        self.books.append(new_book)
        self.save_catalog()
        return True, f"Success: '{new_book.title}' (ISBN: {new_book.isbn}) has been added to the catalog."

    def borrow_book(self, isbn: str, student_name: str) -> tuple[bool, str, str | None]:
        """Borrow an available book by ISBN for a designated student.

        Calculates a due date exactly 14 days from the borrowing date.

        Args:
            isbn: The ISBN of the book to borrow.
            student_name: The name of the student borrowing the book.

        Returns:
            tuple[bool, str, str | None]: (Success boolean, Status message, Due date string or None)
        """
        if not isbn or not isbn.strip():
            return False, "Error: ISBN cannot be blank.", None
        if not student_name or not student_name.strip():
            return False, "Error: Student name cannot be blank.", None

        clean_isbn = isbn.strip()
        book = self.find_book_by_isbn(clean_isbn)

        if book is None:
            return False, f"Error: No book found with ISBN '{clean_isbn}'.", None

        if book.is_borrowed:
            return (
                False,
                f"Unavailable: '{book.title}' is already borrowed by {book.borrowed_by} "
                f"(Due Date: {book.due_date}).",
                None,
            )

        due_date_str = (datetime.now() + timedelta(days=self.DEFAULT_BORROW_DAYS)).strftime("%Y-%m-%d")
        try:
            book.borrow(student_name=student_name.strip(), due_date=due_date_str)
        except ValueError as err:
            return False, f"Error: {err}", None

        self.save_catalog()
        message = (
            f"Success: '{book.title}' borrowed by {book.borrowed_by}.\n"
            f"Return Due Date (14 Days): {due_date_str}"
        )
        return True, message, due_date_str

    def return_book(self, isbn: str) -> tuple[bool, str]:
        """Return a borrowed book by ISBN and mark it as available.

        Args:
            isbn: The ISBN of the book to return.

        Returns:
            tuple[bool, str]: (Success boolean, Status message)
        """
        if not isbn or not isbn.strip():
            return False, "Error: ISBN cannot be blank."

        clean_isbn = isbn.strip()
        book = self.find_book_by_isbn(clean_isbn)

        if book is None:
            return False, f"Error: No book found with ISBN '{clean_isbn}'."

        if not book.is_borrowed:
            return False, f"Error: '{book.title}' (ISBN: {book.isbn}) is not currently borrowed."

        borrower = book.borrowed_by
        try:
            book.return_book()
        except ValueError as err:
            return False, f"Error: {err}"

        self.save_catalog()
        return True, f"Success: '{book.title}' has been successfully returned (previously borrowed by {borrower})."

    def search_book(self, query: str, search_type: str = "all") -> list[Book]:
        """Search books in the catalog by ISBN, title, or author.

        Searches for title and author are case-insensitive and support partial substring matching.
        ISBN search supports both exact and partial matches.

        Args:
            query: The search query string.
            search_type: 'isbn', 'title', 'author', or 'all'.

        Returns:
            list[Book]: Matching Book objects.
        """
        if not query or not query.strip():
            return []

        clean_query = query.strip().lower()
        results: list[Book] = []

        for book in self.books:
            title_lower = book.title.lower()
            author_lower = book.author.lower()
            isbn_lower = book.isbn.lower()

            match search_type.lower():
                case "isbn":
                    if clean_query in isbn_lower:
                        results.append(book)
                case "title":
                    if clean_query in title_lower:
                        results.append(book)
                case "author":
                    if clean_query in author_lower:
                        results.append(book)
                case _:  # Default: search across all fields
                    if (
                        clean_query in title_lower
                        or clean_query in author_lower
                        or clean_query in isbn_lower
                    ):
                        results.append(book)

        return results

    # -------------------------------------------------------------------------
    # Display & Formatting Utilities
    # -------------------------------------------------------------------------

    def format_books_table(self, books: list[Book] | None = None) -> str:
        """Generate a formatted ASCII table representing a list of books.

        Args:
            books: Optional list of books. If None, formats the full catalog.

        Returns:
            str: Pretty-printed tabular string.
        """
        book_list = self.books if books is None else books

        if not book_list:
            return "No books available in the catalog."

        headers = ["ISBN", "Title", "Author", "Status", "Borrowed By", "Due Date"]

        # Calculate dynamic column widths with sensible minimums
        col_widths = {
            "ISBN": max(len(headers[0]), max(len(b.isbn) for b in book_list)),
            "Title": max(len(headers[1]), max(len(b.title) for b in book_list)),
            "Author": max(len(headers[2]), max(len(b.author) for b in book_list)),
            "Status": max(len(headers[3]), 9),  # "Available" or "Borrowed"
            "Borrowed By": max(len(headers[4]), max(len(b.borrowed_by or "-") for b in book_list)),
            "Due Date": max(len(headers[5]), max(len(b.due_date or "-") for b in book_list)),
        }

        # Cap max widths if needed for terminal aesthetic
        col_widths["Title"] = min(max(col_widths["Title"], 12), 32)
        col_widths["Author"] = min(max(col_widths["Author"], 12), 24)

        def truncate(val: str, max_len: int) -> str:
            return val if len(val) <= max_len else val[: max_len - 3] + "..."

        # Separator line
        sep = "+" + "+".join("-" * (col_widths[h] + 2) for h in headers) + "+"

        # Header line
        header_line = "|" + "|".join(f" {h.ljust(col_widths[h])} " for h in headers) + "|"

        rows = [sep, header_line, sep]

        for b in book_list:
            status = "Borrowed" if b.is_borrowed else "Available"
            borrower = b.borrowed_by if (b.is_borrowed and b.borrowed_by) else "-"
            due = b.due_date if (b.is_borrowed and b.due_date) else "-"

            row = (
                f"| {truncate(b.isbn, col_widths['ISBN']).ljust(col_widths['ISBN'])} "
                f"| {truncate(b.title, col_widths['Title']).ljust(col_widths['Title'])} "
                f"| {truncate(b.author, col_widths['Author']).ljust(col_widths['Author'])} "
                f"| {status.ljust(col_widths['Status'])} "
                f"| {truncate(borrower, col_widths['Borrowed By']).ljust(col_widths['Borrowed By'])} "
                f"| {due.ljust(col_widths['Due Date'])} |"
            )
            rows.append(row)

        rows.append(sep)
        rows.append(f"Total Books: {len(book_list)}")
        return "\n".join(rows)

    def display_books(self) -> None:
        """Print all books in the catalog in a readable tabular format."""
        print("\n" + self.format_books_table(self.books) + "\n")
