from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from .db import engine, SessionLocal
from .models import Base, User, Book, user_read
from .data_fetch import populate_initial_books
from .recommender import recommend_for_user

from sqlalchemy import insert

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    await populate_initial_books()

class AddReadRequest(BaseModel):
    user_id: str
    olid: str

class BookOut(BaseModel):
    olid: str
    title: str
    authors: str
    subjects: str
    cover_url: str | None

@app.post("/user/{user_id}/read", response_model=dict)
def add_read_book(user_id: str, body: AddReadRequest):
    session = SessionLocal()
    if not session.get(User, user_id):
        session.add(User(id=user_id))
    book = session.get(Book, body.olid)
    if not book:
        session.close()
        raise HTTPException(404, "Book not found")
    stmt = insert(user_read).prefix_with("OR IGNORE").values(user_id=user_id, book_id=body.olid)
    session.execute(stmt)
    session.commit()
    session.close()
    return {"status": "added"}

@app.get("/user/{user_id}/read", response_model=List[BookOut])
def get_read_books(user_id: str):
    session = SessionLocal()
    q = session.query(Book).join(user_read, Book.olid == user_read.c.book_id).filter(user_read.c.user_id == user_id)
    books = q.all()
    session.close()
    return [BookOut(
        olid=b.olid,
        title=b.title,
        authors=b.authors,
        subjects=b.subjects,
        cover_url=b.cover_url
    ) for b in books]

@app.get("/books", response_model=List[BookOut])
def list_all_books():
    session = SessionLocal()
    books = session.query(Book).limit(200).all()
    session.close()
    return [BookOut(
        olid=b.olid,
        title=b.title,
        authors=b.authors,
        subjects=b.subjects,
        cover_url=b.cover_url
    ) for b in books]

@app.get("/user/{user_id}/recommendations", response_model=List[BookOut])
def recommendations(user_id: str):
    recs = recommend_for_user(user_id, top_k=12)
    out = []
    for b in recs:
        out.append(BookOut(
            olid=b.olid,
            title=b.title,
            authors=b.authors,
            subjects=b.subjects,
            cover_url=b.cover_url
        ))
    return out

