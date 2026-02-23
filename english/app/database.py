"""
SQLite repository for English vocabulary words.
Handles all CRUD operations with parameterized queries.
"""

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Word:
    """Represents a vocabulary word with examples and translations."""

    id: int | None
    word: str
    word_type: str
    translation: str
    example1: str
    example1_tr: str
    example2: str
    example2_tr: str
    example3: str
    example3_tr: str


class WordRepository:
    """SQLite-backed repository for vocabulary words."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    word_type TEXT NOT NULL,
                    translation TEXT NOT NULL,
                    example1 TEXT NOT NULL,
                    example1_tr TEXT NOT NULL,
                    example2 TEXT NOT NULL,
                    example2_tr TEXT NOT NULL,
                    example3 TEXT NOT NULL,
                    example3_tr TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_words_word ON words(word)
            """)

    def _row_to_word(self, row: sqlite3.Row) -> Word:
        return Word(
            id=row["id"],
            word=row["word"],
            word_type=row["word_type"],
            translation=row["translation"],
            example1=row["example1"],
            example1_tr=row["example1_tr"],
            example2=row["example2"],
            example2_tr=row["example2_tr"],
            example3=row["example3"],
            example3_tr=row["example3_tr"],
        )

    def get_all(self) -> list[Word]:
        """Retrieve all words ordered by word alphabetically."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM words ORDER BY word ASC"
            ).fetchall()
            return [self._row_to_word(row) for row in rows]

    def get_by_id(self, word_id: int) -> Word | None:
        """Retrieve a single word by its ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM words WHERE id = ?", (word_id,)
            ).fetchone()
            return self._row_to_word(row) if row else None

    def search(self, query: str) -> list[Word]:
        """Search words by word or translation (case-insensitive)."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM words
                WHERE word LIKE ? OR translation LIKE ?
                ORDER BY word ASC
                """,
                (f"%{query}%", f"%{query}%"),
            ).fetchall()
            return [self._row_to_word(row) for row in rows]

    def create(self, word: Word) -> int:
        """Insert a new word and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO words (
                    word, word_type, translation,
                    example1, example1_tr,
                    example2, example2_tr,
                    example3, example3_tr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    word.word, word.word_type, word.translation,
                    word.example1, word.example1_tr,
                    word.example2, word.example2_tr,
                    word.example3, word.example3_tr,
                ),
            )
            row_id = cursor.lastrowid
            if row_id is None:
                raise RuntimeError("Failed to insert word — no row ID returned")
            return row_id

    def update(self, word: Word) -> bool:
        """Update an existing word. Returns True if a row was updated."""
        if word.id is None:
            return False

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE words SET
                    word = ?, word_type = ?, translation = ?,
                    example1 = ?, example1_tr = ?,
                    example2 = ?, example2_tr = ?,
                    example3 = ?, example3_tr = ?
                WHERE id = ?
                """,
                (
                    word.word, word.word_type, word.translation,
                    word.example1, word.example1_tr,
                    word.example2, word.example2_tr,
                    word.example3, word.example3_tr,
                    word.id,
                ),
            )
            return cursor.rowcount > 0

    def delete(self, word_id: int) -> bool:
        """Delete a word by ID. Returns True if a row was deleted."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM words WHERE id = ?", (word_id,)
            )
            return cursor.rowcount > 0

    def count(self) -> int:
        """Return total number of words."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM words").fetchone()
            return row["cnt"]
