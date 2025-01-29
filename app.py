from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

# Groq API endpoint and API key
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"  # Replace with actual Groq API endpoint
GROQ_API_KEY = "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"  # Replace with your Groq API key

app = FastAPI()

# Define request body format
class QueryRequest(BaseModel):
    user_input: str

def query_groq(user_input: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",  # Replace with the model you want to use
        "messages": [{"role": "user", "content": user_input}],
        "max_tokens": 200,
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No content available.")
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Groq API error: {response.status_code}, {response.text}",
        )

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Groq API integration!"}

@app.post("/query/")
async def query_api(request: QueryRequest):
    try:
        response = query_groq(request.user_input)  # Extract user_input from request
        return {"response": response}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))