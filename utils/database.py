import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "yeonseotheca.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            author      TEXT,
            translator  TEXT,
            publisher   TEXT,
            isbn        TEXT,
            cover_url   TEXT,
            location    TEXT,
            keywords    TEXT,
            memo        TEXT,
            added_at    TEXT DEFAULT (datetime('now','localtime')),
            updated_at  TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    c.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS books_fts
        USING fts5(
            title, author, translator, publisher, keywords, memo,
            content='books', content_rowid='id'
        )
    """)

    # FTS 자동 동기화 트리거
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS books_ai AFTER INSERT ON books BEGIN
            INSERT INTO books_fts(rowid, title, author, translator, publisher, keywords, memo)
            VALUES (new.id, new.title, new.author, new.translator, new.publisher, new.keywords, new.memo);
        END
    """)
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS books_au AFTER UPDATE ON books BEGIN
            INSERT INTO books_fts(books_fts, rowid, title, author, translator, publisher, keywords, memo)
            VALUES ('delete', old.id, old.title, old.author, old.translator, old.publisher, old.keywords, old.memo);
            INSERT INTO books_fts(rowid, title, author, translator, publisher, keywords, memo)
            VALUES (new.id, new.title, new.author, new.translator, new.publisher, new.keywords, new.memo);
        END
    """)
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS books_ad AFTER DELETE ON books BEGIN
            INSERT INTO books_fts(books_fts, rowid, title, author, translator, publisher, keywords, memo)
            VALUES ('delete', old.id, old.title, old.author, old.translator, old.publisher, old.keywords, old.memo);
        END
    """)

    # 기존 DB에 컬럼이 없을 때만 추가 (마이그레이션)
    existing_cols = {row[1] for row in c.execute("PRAGMA table_info(books)").fetchall()}
    if "status" not in existing_cols:
        c.execute("ALTER TABLE books ADD COLUMN status TEXT DEFAULT '읽고싶음'")
    if "rating" not in existing_cols:
        c.execute("ALTER TABLE books ADD COLUMN rating INTEGER DEFAULT NULL")
    if "review" not in existing_cols:
        c.execute("ALTER TABLE books ADD COLUMN review TEXT DEFAULT ''")

    conn.commit()
    conn.close()


def add_book(title, author="", translator="", publisher="", isbn="",
             cover_url="", location="", keywords="", memo="",
             status="읽고싶음", rating=None, review=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO books (title, author, translator, publisher, isbn, cover_url, location, keywords, memo, status, rating, review)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, author, translator, publisher, isbn, cover_url, location, keywords, memo, status, rating, review))
    book_id = c.lastrowid
    conn.commit()
    conn.close()
    return book_id


def update_book(book_id, **fields):
    allowed = {"title", "author", "translator", "publisher", "isbn",
               "cover_url", "location", "keywords", "memo",
               "status", "rating", "review"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    updates["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [book_id]
    conn = get_connection()
    conn.execute(f"UPDATE books SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def delete_book(book_id):
    conn = get_connection()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()


def get_book_by_id(book_id: int) -> dict | None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def search_books(query="", location_filter=""):
    conn = get_connection()
    c = conn.cursor()

    if query.strip():
        c.execute("""
            SELECT b.* FROM books b
            JOIN books_fts f ON b.id = f.rowid
            WHERE books_fts MATCH ?
            ORDER BY b.added_at DESC
        """, (query,))
    else:
        c.execute("SELECT * FROM books ORDER BY added_at DESC")

    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    if location_filter:
        rows = [r for r in rows if location_filter in (r["location"] or "")]
    return rows


def get_all_books():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM books ORDER BY added_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total FROM books")
    total = c.fetchone()["total"]
    c.execute("SELECT COUNT(*) as cnt FROM books WHERE status = '읽음'")
    read_count = c.fetchone()["cnt"]
    c.execute("SELECT location, COUNT(*) as cnt FROM books WHERE location != '' GROUP BY location ORDER BY cnt DESC")
    by_location = [dict(r) for r in c.fetchall()]
    c.execute("SELECT publisher, COUNT(*) as cnt FROM books WHERE publisher != '' GROUP BY publisher ORDER BY cnt DESC LIMIT 10")
    by_publisher = [dict(r) for r in c.fetchall()]
    c.execute("SELECT status, COUNT(*) as cnt FROM books GROUP BY status")
    by_status = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"total": total, "read_count": read_count, "by_location": by_location,
            "by_publisher": by_publisher, "by_status": by_status}
