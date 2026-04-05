from __future__ import annotations

import sqlite3
from pathlib import Path


class NotesRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL
                )
                """,
            )

    def list_notes(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, title, content FROM notes ORDER BY id ASC",
            ).fetchall()
        return [self._row_to_note(row) for row in rows]

    def create_note(self, title: str, content: str) -> dict:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO notes(title, content) VALUES(?, ?)",
                (title, content),
            )
            note_id = int(cursor.lastrowid)
        note = self.get_note(note_id)
        if note is None:
            raise RuntimeError("Created note was not found")
        return note

    def get_note(self, note_id: int) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, title, content FROM notes WHERE id = ?",
                (note_id,),
            ).fetchone()
        return None if row is None else self._row_to_note(row)

    def update_note(self, note_id: int, title: str, content: str) -> dict | None:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE notes SET title = ?, content = ? WHERE id = ?",
                (title, content, note_id),
            )
        if cursor.rowcount == 0:
            return None
        return self.get_note(note_id)

    def delete_note(self, note_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return cursor.rowcount > 0

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _row_to_note(row: sqlite3.Row) -> dict:
        return {"id": row["id"], "title": row["title"], "content": row["content"]}
