from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import requests

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./library.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Groq API configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"

# Database models
class Book(Base):
    _tablename_ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    isbn = Column(String, unique=True)
    category = Column(String)
    difficulty_level = Column(String)  # beginner/intermediate/advanced
    available = Column(Integer)  # quantity available

class User(Base):
    _tablename_ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    academic_level = Column(String)

class Borrowing(Base):
    _tablename_ = "borrowings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    borrow_date = Column(Date)
    due_date = Column(Date)
    returned = Column(Integer)  # 0 = not returned, 1 = returned    # 0 = not returned, 1 = returned

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class QueryRequest(BaseModel):
    user_input: str
    user_id: int  # Added user ID for personalization

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    category: str
    difficulty_level: str
    available: int

class UserCreate(BaseModel):
    name: str
    email: str
    academic_level: str

# Database helper functions
def create_sample_data(db: Session):
    # Create sample books
    books = [
        Book(
            title="Python Crash Course",
            author="Eric Matthes",
            isbn="9781593279288",
            category="Programming",
            difficulty_level="beginner",
            available=3
        ),
        Book(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="9780132350884",
            category="Software Engineering",
            difficulty_level="intermediate",
            available=2
        )
    ]
    
    # Create sample users
    users = [
        User(
            name="John Doe",
            email="john@university.edu",
            academic_level="undergraduate"
        ),
        User(
            name="Jane Smith",
            email="jane@university.edu",
            academic_level="graduate"
        )
    ]

    for book in books:
        db.add(book)
    for user in users:
        db.add(user)
    
    db.commit()

# Initialize sample data
db = SessionLocal()
create_sample_data(db)
db.close()

# Groq API integration
def query_groq(user_input: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
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

# Enhanced API endpoints
@app.get("/")
async def read_root():
    return {"message": "Welcome to LibraAIan Library Assistant"}

@app.post("/query/")
async def query_api(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        # Get user information
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's borrowing history
        borrow_history = db.query(Borrowing).filter(
            Borrowing.user_id == request.user_id
        ).all()

        # Get recommended books based on academic level
        recommended_books = db.query(Book).filter(
            Book.difficulty_level == user.academic_level
        ).limit(3).all()

        # Generate Groq response
        groq_response = query_groq(request.user_input)
        
        return {
            "response": groq_response,
            "recommended_books": [
                {"title": book.title, "author": book.author} 
                for book in recommended_books
            ],
            "borrow_status": [
                {"book_id": entry.book_id, "due_date": entry.due_date}
                for entry in borrow_history
            ]
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/books/")
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/books/")
def get_books(db: Session = Depends(get_db)):
    return db.query(Book).all()