"""
Game Manager for handling multiple game sessions
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from src.ai import AIPlayer
from src.game import Game
from src.persistence import SQLiteGameRepository
from src.serializers import deserialize_game_snapshot, serialize_game_snapshot


class GameSession:
    """Represents a game session with metadata"""

    def __init__(
        self,
        game_id: str,
        game: Game,
        mode: str,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        player2_joined: bool | None = None,
    ):
        self.game_id = game_id
        self.game = game
        self.mode = mode  # "ai" or "multiplayer"
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self.player2_joined = player2_joined if player2_joined is not None else mode == "ai"

    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.now(timezone.utc)


class GameManager:
    """Manages multiple game sessions"""

    def __init__(self):
        self.games: Dict[str, GameSession] = {}
        self.repository: SQLiteGameRepository | None = None
        self.configure_storage(os.getenv("BATTLESHIP_DB_URL", "sqlite:///./battleship.db"))

    def configure_storage(self, database_url: str) -> None:
        """Configure backing storage."""
        self.repository = SQLiteGameRepository(database_url)

    def _save_session(self, session: GameSession) -> None:
        """Persist a session snapshot."""
        if not self.repository:
            return

        self.repository.save_game(
            game_id=session.game_id,
            mode=session.mode,
            state=serialize_game_snapshot(session.game, session.player2_joined),
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    def persist_game(self, game_id: str) -> None:
        """Persist a known session after mutation."""
        session = self.games.get(game_id)
        if session:
            self._save_session(session)

    def create_game(self, player1_name: str, mode: str = "ai") -> str:
        """
        Create a new game session

        Args:
            player1_name: Name of the first player
            mode: "ai" or "multiplayer"

        Returns:
            Game ID
        """
        game_id = str(uuid.uuid4())
        game = Game(player1_name, "Waiting for player 2" if mode == "multiplayer" else "AI")

        if mode == "ai":
            game.player2 = AIPlayer("AI")
            game.player2.place_ships_randomly()

        session = GameSession(game_id, game, mode)
        self.games[game_id] = session
        self._save_session(session)
        return game_id

    def join_game(self, game_id: str, player2_name: str) -> Optional[GameSession]:
        """
        Join an existing multiplayer game as player 2.
        """
        session = self.get_game(game_id)
        if not session:
            return None

        if session.mode != "multiplayer":
            raise ValueError("Only multiplayer games can be joined")

        if session.player2_joined:
            raise ValueError("Game already has two players")

        session.game.player2.name = player2_name
        session.player2_joined = True
        session.update_timestamp()
        self._save_session(session)
        return session

    def get_game(self, game_id: str) -> Optional[GameSession]:
        """
        Get a game session by ID
        """
        session = self.games.get(game_id)
        if session:
            return session

        if not self.repository:
            return None

        stored = self.repository.get_game(game_id)
        if not stored:
            return None

        game, player2_joined = deserialize_game_snapshot(stored["state"])
        session = GameSession(
            game_id=game_id,
            game=game,
            mode=stored["mode"],
            created_at=stored["created_at"],
            updated_at=stored["updated_at"],
            player2_joined=player2_joined,
        )
        self.games[game_id] = session
        return session

    def delete_game(self, game_id: str) -> bool:
        """
        Delete a game session
        """
        in_memory_deleted = game_id in self.games
        self.games.pop(game_id, None)
        persisted_deleted = self.repository.delete_game(game_id) if self.repository else False
        return in_memory_deleted or persisted_deleted

    def list_games(self) -> list:
        """
        List all active games
        """
        if self.repository:
            for stored in self.repository.list_games():
                if stored["game_id"] not in self.games:
                    game, player2_joined = deserialize_game_snapshot(stored["state"])
                    self.games[stored["game_id"]] = GameSession(
                        game_id=stored["game_id"],
                        game=game,
                        mode=stored["mode"],
                        created_at=stored["created_at"],
                        updated_at=stored["updated_at"],
                        player2_joined=player2_joined,
                    )

        return [
            {
                "game_id": session.game_id,
                "mode": session.mode,
                "phase": session.game.phase.value,
                "created_at": session.created_at.isoformat(),
            }
            for session in self.games.values()
        ]
