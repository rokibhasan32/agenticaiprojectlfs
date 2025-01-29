import json
from datetime import datetime, timedelta
from services.gorq_client import GroqClient 
from services.phidata_client import PhiDataClient
from models.library_db import LibraryDB

class LibraryAgent:
    def __init__(self):
        self.groq = GroqClient()
        self.phidata = PhiDataClient()
        self.db = LibraryDB()
        self.auto_renew_days = 7

    def process_query(self, user_input: str, student_id: str = None):
        # Basic intent recognition
        if "renew" in user_input.lower():
            return self.handle_renewal(user_input, student_id)
        elif "location" in user_input.lower() or "shelf" in user_input.lower():
            return self.handle_location(user_input)
        elif "prerequisite" in user_input.lower():
            return self.handle_prerequisites(user_input)
        elif "available" in user_input.lower():
            return self.handle_availability(user_input)
        else:
            return self.general_query(user_input)

    def handle_renewal(self, query: str, student_id: str):
        book_title = query.split("renew")[-1].strip()
        book_info = self.db.search_books(book_title)
        if book_info:
            return self.auto_renew_book(student_id, book_info[0][0])
        return "Book not found in our records."

    def auto_renew_book(self, student_id: str, book_id: int):
        due_date = datetime.now() + timedelta(days=self.auto_renew_days)
        self.db.update_due_date(book_id, due_date)
        return f"Book renewed successfully! New due date: {due_date.strftime('%Y-%m-%d')}"

    def handle_location(self, query: str):
        book_title = query.split("location")[-1].strip()
        book_info = self.db.get_book_details(book_title)
        return f"Located at: {book_info.get('shelf_location', 'Section A3, Shelf 42')}"

    def handle_prerequisites(self, query: str):
        book_title = query.split("prerequisite")[-1].strip()
        response = self.phidata.search_books(book_title)
        return response.get('prerequisites', 'No prerequisites listed.')

    def handle_availability(self, query: str):
        book_title = query.split("available")[-1].strip()
        books = self.db.search_books(book_title)
        if not books:
            alternatives = self.db.find_alternatives(book_title)
            return f"Book not available. Suggestions: {', '.join(alternatives[:3])}"
        return f"Available copies: {len(books)}"

    def general_query(self, query: str):
        return self.groq.query(query)