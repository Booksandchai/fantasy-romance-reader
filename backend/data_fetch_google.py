import os
import asyncio
import httpx
from typing import List
from db import SessionLocal
from models import Book
from sqlalchemy.exc import IntegrityError
import time
import random

GOOGLE_URL = "https://www.googleapis.com/books/v1/volumes"

# Simple exponential backoff wrapper
async def fetch_with_backoff(client, url, params, max_retries=3):
    delay = 1.0
    for attempt in range(max_retries):
        try:
            r = await client.get(url, params=params, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(delay + random.uniform(0, 0.3))
            delay *= 2
    raise RuntimeError("Unreachable")

def normalize_google_volume(volume) -> dict:
    info = volume.get("volumeInfo", {})
    olid = volume.get("id")
    title = info.get("title", "Unknown")
    authors = info.get("authors", [])
    categories = info.get("categories", [])
    # Choose thumbnail if available (convert to https if needed)
    cover_url = None
    image_links = info.get("imageLinks", {})
    if image_links:
        cover_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")
        if cover_url and cover_url.startswith("http:"):
            cover_url = cover_url.replace("http:", "https:")
    return {
        "olid": olid,
        "title": title,
        "authors": ", ".join(authors),
        "subjects": ", ".join(categories),
        "cover_url": cover_url,
    }

async def fetch_google_books_for_subject(subject: str, limit: int = 40):
    key = os.environ.get("GOOGLE_BOOKS_KEY")
    if not key:
        raise RuntimeError("Missing GOOGLE_BOOKS_KEY environment variable")
    params = {
        "q": f"subject:{subject}",
        "maxResults": min(limit, 40),  # API allows up to 40 per request
        "key": key,
    }
    async with httpx.AsyncClient() as client:
        data = await fetch_with_backoff(client, GOOGLE_URL, params)
        return data

async def populate_from_google(subjects: List[str] = ["fantasy", "romance"], per_subject: int = 30):
    from db import engine
    from models import Base
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    seen = set()

    for subj in subjects:
        try:
            data = await fetch_google_books_for_subject(subj, limit=per_subject)
        except Exception as e:
            print(f"[GoogleBooks] failed to fetch subject {subj}: {e}")
            continue
        items = data.get("items", [])
        for item in items:
            b = normalize_google_volume(item)
            if not b["olid"] or b["olid"] in seen:
                continue
            seen.add(b["olid"])
            book = Book(**b)
            session.add(book)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
    finally:
        session.close()
