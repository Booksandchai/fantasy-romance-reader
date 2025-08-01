import asyncio
from sqlalchemy.exc import IntegrityError

from db import engine, SessionLocal
from models import Book
from data_fetch_google import populate_from_google  # non-relative
import httpx

OPENLIB_BASE = "https://openlibrary.org"
SUBJECTS = ["fantasy", "romance"]

# ---------- Open Library helpers ----------
async def fetch_books_for_subject(subject: str, limit: int = 50):
    url = f"{OPENLIB_BASE}/subjects/{subject}.json?limit={limit}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()

def normalize_book(raw) -> dict:
    olid = raw.get("key", "").split("/")[-1]
    title = raw.get("title", "Unknown")
    authors = []
    for a in raw.get("authors", []):
        name = a.get("name") or a.get("author", {}).get("key", "")
        authors.append(name)
    subjects = raw.get("subject", []) or raw.get("subjects", [])
    cover_id = raw.get("cover_id")
    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
    return {
        "olid": olid,
        "title": title,
        "authors": ", ".join(authors),
        "subjects": ", ".join(subjects),
        "cover_url": cover_url,
    }

# ---------- Hybrid population ----------
async def populate_initial_books():
    from models import Base  # ensure Base is available

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    seen = set()

    # seed from Open Library
    for subj in SUBJECTS:
        try:
            data = await fetch_books_for_subject(subj, limit=50)
        except Exception as e:
            print(f"[OpenLibrary] failed to fetch {subj}: {e}")
            continue
        works = data.get("works", [])
        for w in works:
            b = normalize_book(w)
            if b["olid"] in seen:
                continue
            seen.add(b["olid"])
            session.merge(Book(**b))
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
    finally:
        session.close()

    # augment with Google Books
    try:
        await populate_from_google(subjects=SUBJECTS, per_subject=30)
    except Exception as e:
        print(f"[Hybrid] Google Books seeding failed: {e}")
