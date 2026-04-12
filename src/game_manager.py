"""
Game Manager for handling multiple game sessions
"""

import uuid
from datetime import datetime
from typing import Dict, Optional

from src.ai import AIPlayer
from src.game import Game, GamePhase
from src.player import Player


class GameSession:
    """Represents a game session with metadata"""

    def __init__(self, game_id: str, game: Game, mode: str):
        self.game_id = game_id
        self.game = game
        self.mode = mode  # "ai" or "multiplayer"
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.utcnow()


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

        if mode == "ai":
            player1 = Player(player1_name)
            player2 = AIPlayer("AI")
            # AI places ships automatically
            player2.place_ships_randomly()
        else:
            player1 = Player(player1_name)
            player2 = Player("Player 2")

        game = Game(player1.name, player2.name)
        game.player1 = player1
        game.player2 = player2

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
