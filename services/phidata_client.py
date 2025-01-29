# services/phidata_client.py
import requests
from config import PHI_API_KEY

class PhiDataClient:
    BASE_URL = "https://api.phidata.com"

    def __init__(self):
        self.api_key = PHI_API_KEY

    def search_books(self, query):
        url = f"{self.BASE_URL}/search/books"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(url, json={"query": query}, headers=headers)
        return response.json()

    def add_book(self, book_data):
        url = f"{self.BASE_URL}/books"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(url, json=book_data, headers=headers)
        return response.json()
