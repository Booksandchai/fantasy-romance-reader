from sqlalchemy import Column, Integer, String, Table, ForeignKey, Text
from sqlalchemy.orm import relationship
from db import Base

# association table for many-to-many between user and read books
from sqlalchemy import UniqueConstraint

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)  # simple user id from client

class Book(Base):
    __tablename__ = "books"
    olid = Column(String, primary_key=True, index=True)  # Open Library ID
    title = Column(String)
    authors = Column(String)  # comma separated
    subjects = Column(String)  # comma separated
    cover_url = Column(String, nullable=True)

from sqlalchemy import Table

user_read = Table(
    "user_read",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id", ondelete="CASCADE")),
    Column("book_id", String, ForeignKey("books.olid", ondelete="CASCADE")),
)
