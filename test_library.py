"""
test_library.py
===============
Comprehensive automated test suite verifying all 13 core requirements of the
University Library Management System without altering production data.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from book import Book
from library import Library


class TestLibraryManagementSystem(unittest.TestCase):
    """Unit and integration tests covering all requirements."""

    def setUp(self) -> None:
        """Create an isolated temporary catalog file for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.catalog_file = Path(self.temp_dir.name) / "test_catalog.json"
        # Seed test catalog with the standard initial data
        initial_data = [
            {
                "title": "Clean Code",
                "author": "Robert Martin",
                "isbn": "978-0134685991",
                "is_borrowed": False,
                "borrowed_by": None,
                "due_date": None,
            },
            {
                "title": "Python Cookbook",
                "author": "David Beazley",
                "isbn": "978-0596517748",
                "is_borrowed": True,
                "borrowed_by": "Jane Doe",
                "due_date": "2026-11-05",
            },
            {
                "title": "The Pragmatic Programmer",
                "author": "Andy Hunt",
                "isbn": "978-0132350884",
                "is_borrowed": False,
                "borrowed_by": None,
                "due_date": None,
            },
        ]
        with open(self.catalog_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2)

        self.library = Library(catalog_path=self.catalog_file)

    def tearDown(self) -> None:
        """Clean up the temporary directory after each test."""
        self.temp_dir.cleanup()

    # Case 1: Add a new book successfully
    def test_01_add_book_success(self) -> None:
        success, msg = self.library.add_book(
            title="Design Patterns",
            author="Erich Gamma",
            isbn="978-0201633610",
        )
        self.assertTrue(success)
        self.assertIn("added to the catalog", msg)
        book = self.library.find_book_by_isbn("978-0201633610")
        self.assertIsNotNone(book)
        self.assertEqual(book.title, "Design Patterns")
        self.assertFalse(book.is_borrowed)

    # Case 2: Reject a duplicate ISBN
    def test_02_reject_duplicate_isbn(self) -> None:
        # Existing ISBN in setup is 978-0134685991
        success, msg = self.library.add_book(
            title="Clean Code Duplicate",
            author="Another Author",
            isbn="978-0134685991",
        )
        self.assertFalse(success)
        self.assertIn("Duplicate ISBN Error", msg)

    # Case 3: Display the full catalog
    def test_03_display_books_table(self) -> None:
        table_output = self.library.format_books_table()
        self.assertIn("Clean Code", table_output)
        self.assertIn("Python Cookbook", table_output)
        self.assertIn("The Pragmatic Programmer", table_output)
        self.assertIn("Total Books: 3", table_output)

    # Case 4: Search by exact ISBN
    def test_04_search_by_exact_isbn(self) -> None:
        results = self.library.search_book("978-0134685991", search_type="isbn")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Clean Code")

    # Case 5: Search by partial title
    def test_05_search_by_partial_title(self) -> None:
        results = self.library.search_book("Pragmatic", search_type="title")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].isbn, "978-0132350884")

    # Case 6: Search by author without case sensitivity
    def test_06_search_by_author_case_insensitive(self) -> None:
        results = self.library.search_book("dAvId bEaZleY", search_type="author")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Python Cookbook")

    # Case 7: Borrow an available book
    def test_07_borrow_available_book(self) -> None:
        success, msg, due_date = self.library.borrow_book(
            isbn="978-0134685991", student_name="Alice Smith"
        )
        self.assertTrue(success)
        expected_due = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        self.assertEqual(due_date, expected_due)
        book = self.library.find_book_by_isbn("978-0134685991")
        self.assertTrue(book.is_borrowed)
        self.assertEqual(book.borrowed_by, "Alice Smith")
        self.assertEqual(book.due_date, expected_due)

    # Case 8: Prevent borrowing an already-borrowed book
    def test_08_prevent_borrowing_already_borrowed_book(self) -> None:
        # Python Cookbook is already borrowed in setup
        success, msg, due_date = self.library.borrow_book(
            isbn="978-0596517748", student_name="Bob Jones"
        )
        self.assertFalse(success)
        self.assertIsNone(due_date)
        self.assertIn("already borrowed", msg)

    # Case 9: Return a borrowed book
    def test_09_return_borrowed_book(self) -> None:
        success, msg = self.library.return_book("978-0596517748")
        self.assertTrue(success)
        self.assertIn("successfully returned", msg)
        book = self.library.find_book_by_isbn("978-0596517748")
        self.assertFalse(book.is_borrowed)
        self.assertIsNone(book.borrowed_by)
        self.assertIsNone(book.due_date)

    # Case 10: Prevent returning a book that is not borrowed
    def test_10_prevent_returning_available_book(self) -> None:
        # Clean Code is available in setup
        success, msg = self.library.return_book("978-0134685991")
        self.assertFalse(success)
        self.assertIn("not currently borrowed", msg)

    # Case 11: Preserve catalog data after restarting the program
    def test_11_preserve_catalog_after_restart(self) -> None:
        # Add a book and borrow an existing book
        self.library.add_book("Refactoring", "Martin Fowler", "978-0201485677")
        self.library.borrow_book("978-0134685991", "Charlie Brown")

        # Simulate restarting the application with a brand new Library instance
        restarted_library = Library(catalog_path=self.catalog_file)
        self.assertEqual(len(restarted_library.books), 4)

        refact_book = restarted_library.find_book_by_isbn("978-0201485677")
        self.assertIsNotNone(refact_book)
        self.assertEqual(refact_book.title, "Refactoring")

        clean_book = restarted_library.find_book_by_isbn("978-0134685991")
        self.assertTrue(clean_book.is_borrowed)
        self.assertEqual(clean_book.borrowed_by, "Charlie Brown")

    # Case 12: Handle invalid menu selections and empty inputs
    def test_12_handle_invalid_and_empty_inputs(self) -> None:
        # Empty title/author/isbn
        s1, m1 = self.library.add_book("", "Author", "12345")
        self.assertFalse(s1)
        s2, m2 = self.library.add_book("Title", "", "12345")
        self.assertFalse(s2)
        s3, m3 = self.library.add_book("Title", "Author", "   ")
        self.assertFalse(s3)

        # Empty borrow details
        sb1, mb1, _ = self.library.borrow_book("", "Alice")
        self.assertFalse(sb1)
        sb2, mb2, _ = self.library.borrow_book("978-0134685991", "")
        self.assertFalse(sb2)

        # Empty return ISBN
        sr, mr = self.library.return_book("")
        self.assertFalse(sr)

    # Case 13: Handle a missing or malformed JSON file safely
    def test_13_handle_missing_and_malformed_json(self) -> None:
        # 13a: Missing file should create initial sample catalog
        missing_catalog_file = Path(self.temp_dir.name) / "non_existent_catalog.json"
        fresh_library = Library(catalog_path=missing_catalog_file)
        self.assertTrue(missing_catalog_file.exists())
        self.assertEqual(len(fresh_library.books), 3)

        # 13b: Malformed JSON should not crash and NOT overwrite existing file
        corrupt_catalog_file = Path(self.temp_dir.name) / "corrupt_catalog.json"
        corrupt_content = "{ this is completely invalid JSON content! }"
        with open(corrupt_catalog_file, "w", encoding="utf-8") as f:
            f.write(corrupt_content)

        resilient_library = Library(catalog_path=corrupt_catalog_file)
        self.assertEqual(len(resilient_library.books), 0)

        # Verify that corrupt file was NOT overwritten with an empty list
        with open(corrupt_catalog_file, "r", encoding="utf-8") as f:
            saved_content = f.read()
        self.assertEqual(saved_content, corrupt_content)


if __name__ == "__main__":
    unittest.main()
