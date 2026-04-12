"""
Game Manager for handling multiple game sessions
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from src.ai import AIPlayer
from src.game import Game


class GameSession:
    """Represents a game session with metadata"""

    def __init__(self, game_id: str, game: Game, mode: str):
        self.game_id = game_id
        self.game = game
        self.mode = mode  # "ai" or "multiplayer"
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.now(timezone.utc)


class GameManager:
    """Manages multiple game sessions"""

    def __init__(self):
        self.games: Dict[str, GameSession] = {}

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

        game = Game(player1_name, player1_name if mode != "ai" else "AI")

        if mode == "ai":
            # Replace player2 with AIPlayer and place ships automatically
            game.player2 = AIPlayer("AI")
            game.player2.place_ships_randomly()

        session = GameSession(game_id, game, mode)
        self.games[game_id] = session

        return game_id

    def get_game(self, game_id: str) -> Optional[GameSession]:
        """
        Get a game session by ID

        Args:
            game_id: The game ID

        Returns:
            GameSession or None if not found
        """
        return self.games.get(game_id)

    def delete_game(self, game_id: str) -> bool:
        """
        Delete a game session

        Args:
            game_id: The game ID

        Returns:
            True if deleted, False if not found
        """
        if game_id in self.games:
            del self.games[game_id]
            return True
        return False

    def list_games(self) -> list:
        """
        List all active games

        Returns:
            List of game sessions
        """
        return [
            {
                "game_id": session.game_id,
                "mode": session.mode,
                "phase": session.game.phase.value,
                "created_at": session.created_at.isoformat(),
            }
            for session in self.games.values()
        ]
