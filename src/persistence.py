"""
Persistence layer for Battleship game sessions.
"""

from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, create_engine, delete, select
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


class GameEventRecord(Base):
    """Stored event history for a game."""

    __tablename__ = "game_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    player: Mapped[str | None] = mapped_column(String, nullable=True)
    event_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


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
            session.execute(delete(GameEventRecord).where(GameEventRecord.game_id == game_id))
            session.commit()
            return True

    def append_event(
        self,
        game_id: str,
        event_type: str,
        player: str | None,
        payload: dict,
        created_at: datetime,
    ) -> None:
        """Append a history event for a game."""
        with self.session_factory() as session:
            session.add(
                GameEventRecord(
                    game_id=game_id,
                    event_type=event_type,
                    player=player,
                    event_json=json.dumps(payload),
                    created_at=created_at,
                )
            )
            session.commit()

    def get_game_history(self, game_id: str) -> list[dict]:
        """Return chronological history for a game."""
        with self.session_factory() as session:
            records = session.scalars(
                select(GameEventRecord)
                .where(GameEventRecord.game_id == game_id)
                .order_by(GameEventRecord.id.asc())
            ).all()
            return [
                {
                    "event_type": record.event_type,
                    "player": record.player,
                    "created_at": record.created_at.isoformat(),
                    **json.loads(record.event_json),
                }
                for record in records
            ]

    def get_player_stats(self, player_name: str) -> dict:
        """Summarize completed stored games for a player."""
        with self.session_factory() as session:
            records = session.scalars(select(GameRecord)).all()

        games_played = 0
        wins = 0
        losses = 0
        active_games = 0

        for record in records:
            state = json.loads(record.state_json)
            player_names = [state["player1"]["name"], state["player2"]["name"]]
            if player_name not in player_names:
                continue

            games_played += 1
            if state["phase"] == "finished":
                winner_key = state["winner"]
                if winner_key and state[winner_key]["name"] == player_name:
                    wins += 1
                else:
                    losses += 1
            else:
                active_games += 1

        return {
            "player_name": player_name,
            "games_played": games_played,
            "wins": wins,
            "losses": losses,
            "active_games": active_games,
            "win_rate": 0 if games_played == 0 else wins / games_played,
        }

    def delete_all(self) -> None:
        """Clear all stored games, used in tests."""
        with self.session_factory() as session:
            session.execute(delete(GameEventRecord))
            session.execute(delete(GameRecord))
            session.commit()
