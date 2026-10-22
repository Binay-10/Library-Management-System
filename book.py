"""
book.py
=======
Defines the Book class representing an individual book in the library catalog.

Attributes:
    title (str): Title of the book.
    author (str): Author of the book.
    isbn (str): International Standard Book Number (unique identifier).
    is_borrowed (bool): Borrowing status (True if currently borrowed, False if available).
    borrowed_by (str | None): Name of the student currently borrowing the book.
    due_date (str | None): Due date for return in 'YYYY-MM-DD' format.
"""

from __future__ import annotations
from typing import Any


class Book:
    """Represents a book in the University Library catalog.

    Encapsulates book metadata, borrowing status, borrower details,
    and serialization methods for persistent JSON storage.
    """

    def __init__(
        self,
        title: str,
        author: str,
        isbn: str,
        is_borrowed: bool = False,
        borrowed_by: str | None = None,
        due_date: str | None = None,
    ) -> None:
        """Initialize a Book instance with validation.

        Args:
            title: Book title (non-empty string).
            author: Book author (non-empty string).
            isbn: Unique ISBN string (non-empty string).
            is_borrowed: True if borrowed, False if available.
            borrowed_by: Student name if borrowed, else None.
            due_date: Due date string (YYYY-MM-DD) if borrowed, else None.

        Raises:
            ValueError: If title, author, or isbn are invalid or empty strings.
        """
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Book title must be a non-empty string.")
        if not isinstance(author, str) or not author.strip():
            raise ValueError("Book author must be a non-empty string.")
        if not isinstance(isbn, str) or not isbn.strip():
            raise ValueError("Book ISBN must be a non-empty string.")

        self.title: str = title.strip()
        self.author: str = author.strip()
        self.isbn: str = isbn.strip()
        self.is_borrowed: bool = bool(is_borrowed)
        self.borrowed_by: str | None = borrowed_by.strip() if (borrowed_by and isinstance(borrowed_by, str)) else None
        self.due_date: str | None = due_date.strip() if (due_date and isinstance(due_date, str)) else None

    def borrow(self, student_name: str, due_date: str) -> None:
        """Mark the book as borrowed by a student with a designated due date.

        Args:
            student_name: Name of the borrowing student.
            due_date: Return due date (e.g., 'YYYY-MM-DD').

        Raises:
            ValueError: If the book is already borrowed or student_name/due_date is blank.
        """
        if self.is_borrowed:
            raise ValueError(
                f"'{self.title}' (ISBN: {self.isbn}) is already borrowed by {self.borrowed_by}."
            )
        if not isinstance(student_name, str) or not student_name.strip():
            raise ValueError("Student name must be provided to borrow a book.")
        if not isinstance(due_date, str) or not due_date.strip():
            raise ValueError("A valid due date must be provided.")

        self.is_borrowed = True
        self.borrowed_by = student_name.strip()
        self.due_date = due_date.strip()

    def return_book(self) -> None:
        """Mark the book as returned and reset borrowing metadata.

        Raises:
            ValueError: If the book is not currently borrowed.
        """
        if not self.is_borrowed:
            raise ValueError(
                f"'{self.title}' (ISBN: {self.isbn}) is not currently borrowed."
            )

        self.is_borrowed = False
        self.borrowed_by = None
        self.due_date = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the Book instance into a dictionary suitable for JSON serialization.

        Returns:
            Dictionary matching the JSON catalog schema.
        """
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "is_borrowed": self.is_borrowed,
            "borrowed_by": self.borrowed_by,
            "due_date": self.due_date,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Book:
        """Construct a Book instance from a dictionary record.

        Args:
            data: Dictionary containing book attributes.

        Returns:
            A new Book instance.

        Raises:
            KeyError: If mandatory keys ('title', 'author', 'isbn') are missing.
            ValueError: If data values fail validation.
        """
        if not isinstance(data, dict):
            raise ValueError(f"Expected a dictionary for Book record, got {type(data).__name__}.")

        for key in ("title", "author", "isbn"):
            if key not in data:
                raise KeyError(f"Missing required book attribute: '{key}'.")

        return cls(
            title=str(data["title"]),
            author=str(data["author"]),
            isbn=str(data["isbn"]),
            is_borrowed=bool(data.get("is_borrowed", False)),
            borrowed_by=data.get("borrowed_by"),
            due_date=data.get("due_date"),
        )

    def __str__(self) -> str:
        """User-friendly string representation of the book."""
        status = "Available" if not self.is_borrowed else f"Borrowed by {self.borrowed_by} (Due: {self.due_date})"
        return f"[{self.isbn}] \"{self.title}\" by {self.author} — {status}"

    def __repr__(self) -> str:
        """Developer-friendly string representation of the Book object."""
        return (
            f"Book(title={self.title!r}, author={self.author!r}, isbn={self.isbn!r}, "
            f"is_borrowed={self.is_borrowed!r}, borrowed_by={self.borrowed_by!r}, due_date={self.due_date!r})"
        )
