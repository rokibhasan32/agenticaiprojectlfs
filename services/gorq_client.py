# services/gorq_client.py
import requests
from config import GROQ_API_KEY, GROQ_API_URL

class GroqClient:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.api_url = GROQ_API_URL

    def query(self, question: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-3.3-70b-versatile",  # Replace with your model
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 200,
        }
        response = requests.post(self.api_url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from Groq API.")
        else:
            raise Exception(f"Groq API error: {response.status_code}, {response.text}")