from data_fetch_google import populate_from_google

async def populate_initial_books():
    from db import engine
    from models import Book, Base
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    # First seed from Open Library (existing logic)
    seen = set()
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
            session.merge(Book(**b))  # merge avoids duplicates
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
    finally:
        session.close()

    # Then augment/enrich with Google Books for broader modern coverage
    try:
        await populate_from_google(subjects=SUBJECTS, per_subject=30)
    except Exception as e:
        print(f"[Hybrid] Google Books seeding failed: {e}")

