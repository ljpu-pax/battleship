"""
Persistence layer for Battleship game sessions.
"""

from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import DateTime, String, Text, create_engine, delete, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class GameRecord(Base):
    """Stored game session snapshot."""

    __tablename__ = "games"

    game_id: Mapped[str] = mapped_column(String, primary_key=True)
    mode: Mapped[str] = mapped_column(String, nullable=False)
    state_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SQLiteGameRepository:
    """Persist game sessions in SQLite using SQLAlchemy."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.session_factory = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def save_game(
        self,
        game_id: str,
        mode: str,
        state: dict,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        """Insert or update a stored game snapshot."""
        payload = json.dumps(state)

        with self.session_factory() as session:
            record = session.get(GameRecord, game_id)
            if record is None:
                record = GameRecord(
                    game_id=game_id,
                    mode=mode,
                    state_json=payload,
                    created_at=created_at,
                    updated_at=updated_at,
                )
                session.add(record)
            else:
                record.mode = mode
                record.state_json = payload
                record.updated_at = updated_at

            session.commit()

    def get_game(self, game_id: str) -> dict | None:
        """Fetch a stored game snapshot."""
        with self.session_factory() as session:
            record = session.get(GameRecord, game_id)
            if record is None:
                return None

            return {
                "game_id": record.game_id,
                "mode": record.mode,
                "state": json.loads(record.state_json),
                "created_at": record.created_at,
                "updated_at": record.updated_at,
            }

    def list_games(self) -> list[dict]:
        """List stored games."""
        with self.session_factory() as session:
            records = session.scalars(select(GameRecord)).all()
            return [
                {
                    "game_id": record.game_id,
                    "mode": record.mode,
                    "state": json.loads(record.state_json),
                    "created_at": record.created_at,
                    "updated_at": record.updated_at,
                }
                for record in records
            ]

    def delete_game(self, game_id: str) -> bool:
        """Delete a stored game."""
        with self.session_factory() as session:
            record = session.get(GameRecord, game_id)
            if record is None:
                return False

            session.delete(record)
            session.commit()
            return True

    def delete_all(self) -> None:
        """Clear all stored games, used in tests."""
        with self.session_factory() as session:
            session.execute(delete(GameRecord))
            session.commit()
