# University Library Management System

An Object-Oriented, terminal-based Library Management System built in Python 3.10+ that provides robust catalog operations, intelligent search algorithms, automated due date calculations, and resilient JSON file persistence.

Developed as a demonstration of clean code, Object-Oriented Programming (OOP) principles, defensive programming, and standard library best practices for Tech Internship assignments.

---

## Table of Contents

- [Objectives & Key Features](#objectives--key-features)
- [Technologies Used](#technologies-used)
- [Project File Structure](#project-file-structure)
- [Python Installation Requirements](#python-installation-requirements)
- [Setup & How to Run](#setup--how-to-run)
- [Menu Options & Usage Examples](#menu-options--usage-examples)
- [JSON Persistence Architecture](#json-persistence-architecture)
- [Example Terminal Output](#example-terminal-output)
- [Automated & Manual Testing](#automated--manual-testing)
- [Author Profile](#author-profile)

---

## Objectives & Key Features

The primary objective of this project is to model an interactive, production-ready library catalog system that is intuitive for students and administrators alike while illustrating core software engineering patterns:

- **Object-Oriented Design (OOP)**: Clear separation of concerns between domain entities (`Book`), collection management (`Library`), and command-line user interaction (`main.py`).
- **Encapsulation & Validation**: Strict field validations (non-empty strings, distinct ISBN checking, borrowing state consistency).
- **Automated Due Date Calculation**: Built-in 14-day loan window automatically computed using Python's standard `datetime` module.
- **Robust Multi-Criteria Search**:
  - Exact or partial ISBN matching.
  - Case-insensitive, partial substring title matching.
  - Case-insensitive, partial substring author matching.
  - Universal search spanning title, author, and ISBN simultaneously.
- **Fail-Safe JSON Persistence**:
  - Automatically loads on application launch.
  - Automatically commits changes whenever books are added, borrowed, or returned.
  - Auto-saves cleanly upon exit or unexpected interrupts (`Ctrl+C` / `EOF`).
  - Employs safe path resolution anchored to the Python source file directory rather than the variable terminal working directory.
  - **Zero Data Loss Guarantee**: If an existing catalog file contains malformed or corrupt JSON, the system alerts the administrator and does **not** overwrite the damaged file.
- **Pre-loaded Sample Data**: Bootstraps with 3 curated books if no catalog file is detected.
- **Zero Third-Party Dependencies**: Powered exclusively by the Python Standard Library.

---

## Technologies Used

- **Language**: Python 3.10 or newer (tested with Python 3.10, 3.11, 3.12, 3.13)
- **Standard Library Modules**:
  - `json`: Data serialization and deserialization.
  - `datetime` & `timedelta`: Dynamic loan duration and due date generation.
  - `pathlib.Path`: Cross-platform, reliable filesystem path resolution.
  - `typing`: Static type annotations (`str | None`, `list[Book]`, `Any`).
  - `unittest`: Automated regression test suite.

---

## Project File Structure

```
Library-Management-System/
├── main.py                 # Menu-driven CLI interface and input handling
├── book.py                 # Domain entity class representing a Book
├── library.py              # Collection manager, search engine, and JSON handler
├── library_catalog.json    # Persistent JSON storage for catalog records
├── test_library.py         # Automated unit test suite (13 test cases)
├── README.md               # Project documentation and guide
└── .gitignore              # Git ignore rules for Python caches and environments
```

---

## Python Installation Requirements

Ensure you have **Python 3.10** or higher installed on your computer.

Verify your installed Python version by running:

```bash
python --version
# Output should show: Python 3.10.x, 3.11.x, 3.12.x, or 3.13.x
```

If `python` is not recognized, try `python3` (on macOS/Linux) or `py` (on Windows).

---

## Setup & How to Run

### 1. Clone or Open the Project

Navigate into the project directory:

```bash
cd Library-Management-System
```

### 2. Run the Application

Launch the interactive console system:

```bash
python main.py
```

*(On macOS/Linux, if needed: `python3 main.py`)*

---

## Menu Options & Usage Examples

When launched, the application presents the following menu:

```
=== UNIVERSITY LIBRARY MANAGEMENT SYSTEM ===

1. View All Books
2. Borrow a Book
3. Return a Book
4. Add New Book (Admin)
5. Search Book
6. Exit

Select Option:
```

### 1. View All Books
Displays all books currently registered in the catalog in a formatted ASCII table showing ISBN, Title, Author, Availability Status, Current Borrower, and Due Date.

### 2. Borrow a Book
- Prompts for the book's **ISBN** and the **Student's Name**.
- Verifies the book exists and is currently available.
- Automatically calculates a return deadline **14 days** into the future.
- Updates the catalog and persists changes immediately.

### 3. Return a Book
- Prompts for the book's **ISBN**.
- Verifies that the book is currently marked as borrowed.
- Clears the borrower name and due date, restoring the status to `Available`.
- Persists changes immediately.

### 4. Add New Book (Admin)
- Prompts for **Title**, **Author**, and **ISBN**.
- Rejects blank inputs or duplicate ISBNs.
- Instantiates a new `Book` and saves it to `library_catalog.json`.

### 5. Search Book
Provides an intuitive submenu with 4 search modes:
1. **Search by Title**: Case-insensitive substring match (e.g., searching `clean` finds `Clean Code`).
2. **Search by Author**: Case-insensitive substring match (e.g., searching `beazley` finds `David Beazley`).
3. **Search by ISBN**: Exact or substring ISBN matching.
4. **Universal Search**: Searches across Title, Author, and ISBN simultaneously.

### 6. Exit
Saves all pending records to `library_catalog.json` and cleanly terminates the program.

---

## JSON Persistence Architecture

The catalog records are persistently stored in `library_catalog.json` as a standardized array of JSON objects:

```json
[
  {
    "title": "Clean Code",
    "author": "Robert Martin",
    "isbn": "978-0134685991",
    "is_borrowed": false,
    "borrowed_by": null,
    "due_date": null
  },
  {
    "title": "Python Cookbook",
    "author": "David Beazley",
    "isbn": "978-0596517748",
    "is_borrowed": true,
    "borrowed_by": "Jane Doe",
    "due_date": "2026-11-05"
  },
  {
    "title": "The Pragmatic Programmer",
    "author": "Andy Hunt",
    "isbn": "978-0132350884",
    "is_borrowed": false,
    "borrowed_by": null,
    "due_date": null
  }
]
```

### Key Safety Guarantees:
1. **Location Invariance**: File operations use `Path(__file__).resolve().parent / "library_catalog.json"`. Whether the user launches the script from the root, their home directory, or a nested folder, the data file will always be found and updated in the project folder.
2. **Crash & Corruption Safety**: If `library_catalog.json` is manually corrupted with invalid syntax, the loader traps the `json.JSONDecodeError`, displays an explicit error message, and retains the damaged file on disk rather than wiping it with an empty array.

---

## Example Terminal Output

### Catalog View (Option 1)

```
+----------------+--------------------------+-----------------+-----------+-------------+------------+
| ISBN           | Title                    | Author          | Status    | Borrowed By | Due Date   |
+----------------+--------------------------+-----------------+-----------+-------------+------------+
| 978-0134685991 | Clean Code               | Robert Martin   | Available | -           | -          |
| 978-0596517748 | Python Cookbook          | David Beazley   | Borrowed  | Jane Doe    | 2026-11-05 |
| 978-0132350884 | The Pragmatic Programmer | Andy Hunt       | Available | -           | -          |
+----------------+--------------------------+-----------------+-----------+-------------+------------+
Total Books: 3
```

### Borrowing a Book (Option 2)

```
--- BORROW A BOOK ---
Enter Book ISBN: 978-0134685991
Enter Student Name: Alex Johnson

[+] Success: 'Clean Code' borrowed by Alex Johnson.
Return Due Date (14 Days): 2026-11-05
```

### Returning a Book (Option 3)

```
--- RETURN A BOOK ---
Enter Book ISBN to return: 978-0134685991

[+] Success: 'Clean Code' has been successfully returned (previously borrowed by Alex Johnson).
```

---

## Automated & Manual Testing

### Automated Test Suite
An automated test suite is provided in `test_library.py` covering all 13 core requirements using Python's built-in `unittest` framework:

```bash
python -m unittest test_library.py -v
```

**Verification Results:**
```
test_01_add_book_success ... ok
test_02_reject_duplicate_isbn ... ok
test_03_display_books_table ... ok
test_04_search_by_exact_isbn ... ok
test_05_search_by_partial_title ... ok
test_06_search_by_author_case_insensitive ... ok
test_07_borrow_available_book ... ok
test_08_prevent_borrowing_already_borrowed_book ... ok
test_09_return_borrowed_book ... ok
test_10_prevent_returning_available_book ... ok
test_11_preserve_catalog_after_restart ... ok
test_12_handle_invalid_and_empty_inputs ... ok
test_13_handle_missing_and_malformed_json ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.096s

OK
```

### Manual Testing Checklist

| Test # | Objective | Input / Action | Expected Result | Status |
|:---:|:---|:---|:---|:---:|
| 1 | Add Book | Title: "Fluent Python", Author: "Luciano Ramalho", ISBN: "978-1491946008" | Book successfully added to catalog | Pass |
| 2 | Reject Duplicate ISBN | Add book with existing ISBN `978-0134685991` | Rejected with duplicate ISBN error | Pass |
| 3 | Display Catalog | Option 1 | Neatly formatted table displaying all books | Pass |
| 4 | Search by ISBN | Option 5 -> Search by ISBN -> `978-0134685991` | Returns "Clean Code" | Pass |
| 5 | Search by Title | Option 5 -> Search by Title -> `pragmatic` | Returns "The Pragmatic Programmer" | Pass |
| 6 | Search by Author | Option 5 -> Search by Author -> `david` | Returns "Python Cookbook" | Pass |
| 7 | Borrow Available Book | Option 2 -> ISBN: `978-0134685991`, Name: "Sarah Connor" | Marked borrowed, due date = today + 14 days | Pass |
| 8 | Prevent Double Borrowing | Option 2 -> Attempt to borrow `978-0596517748` | Rejected: already borrowed by Jane Doe | Pass |
| 9 | Return Borrowed Book | Option 3 -> ISBN: `978-0596517748` | Return processed, status becomes Available | Pass |
| 10 | Prevent Returning Available Book | Option 3 -> Attempt to return `978-0132350884` | Rejected: book is not currently borrowed | Pass |
| 11 | Catalog Persistence | Add/borrow a book, exit (Option 6), restart program | Modified records remain intact in catalog | Pass |
| 12 | Input Validation | Empty inputs or invalid menu choices | Friendly prompt, no unhandled exceptions | Pass |
| 13 | Corrupt File Safety | Corrupt `library_catalog.json` syntax manually | Error printed, corrupted file preserved on disk | Pass |

---

## Author Profile

* **Student / Developer Name**: [Your Name Here]
* **University / College**: [Your University / College Name]
* **Course / Degree**: B.Tech / B.S. in Computer Science & Engineering
* **Roll / Student ID**: [Your Student ID / Roll Number]
* **Email**: [your.email@example.com]
* **GitHub**: [https://github.com/your-username](https://github.com/your-username)
* **LinkedIn**: [https://linkedin.com/in/your-profile](https://linkedin.com/in/your-profile)

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
