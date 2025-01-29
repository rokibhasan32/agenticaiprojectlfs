import sqlite3
from typing import List, Dict

class LibraryDB:
    def __init__(self, db_path: str = "library.db"):
        self.db_path = db_path
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Add new columns for agentic features
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            published_year INTEGER,
            available INTEGER DEFAULT 1,
            shelf_location TEXT,
            due_date DATE,
            prerequisites TEXT
        )
        """)
        conn.commit()
        conn.close()

    def get_book_details(self, book_title: str) -> Dict:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Books WHERE title LIKE ?", (f"%{book_title}%",))
        book = cursor.fetchone()
        conn.close()
        return dict(book) if book else {}

    def find_alternatives(self, book_title: str) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT title FROM Books 
        WHERE genre = (SELECT genre FROM Books WHERE title LIKE ? LIMIT 1)
        ORDER BY RANDOM() LIMIT 3
        """, (f"%{book_title}%",))
        alternatives = [row[0] for row in cursor.fetchall()]
        conn.close()
        return alternatives

    def update_due_date(self, book_id: int, new_due_date: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE BorrowedBooks 
        SET return_date = ?
        WHERE book_id = ?
        """, (new_due_date, book_id))
        conn.commit()
        conn.close()