from models import Book
from db import SessionLocal
from sqlalchemy import select
from collections import Counter

def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = a & b
    union = a | b
    return len(inter) / len(union)

def recommend_for_user(user_id: str, top_k: int = 10):
    session = SessionLocal()
    # fetch read book IDs
    user_read_stmt = f"""
        SELECT book_id FROM user_read WHERE user_id = :uid
    """
    result = session.execute(user_read_stmt, {"uid": user_id})
    read_ids = {row[0] for row in result.fetchall()}

    # fetch all books
    all_books = session.query(Book).all()
    # build subject sets
    book_subjects = {}
    for b in all_books:
        subjects = set(s.strip().lower() for s in (b.subjects or "").split(",") if s.strip())
        book_subjects[b.olid] = subjects

    # collect subjects from read books
    read_subjects = set()
    for rid in read_ids:
        read_subjects |= book_subjects.get(rid, set())

    # score unread books
    scores = []
    for b in all_books:
        if b.olid in read_ids:
            continue
        score = jaccard(read_subjects, book_subjects.get(b.olid, set()))
        scores.append((score, b))
    # sort
    scores.sort(reverse=True, key=lambda x: x[0])
    # take top_k with nonzero score, fallback to popular (first ones) if none
    recommendations = [b for score, b in scores if score > 0][:top_k]
    if not recommendations:
        # just give first top_k
        recommendations = [b for _, b in scores[:top_k]]
    session.close()
    return recommendations
