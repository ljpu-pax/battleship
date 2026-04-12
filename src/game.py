"""
Game module for Battleship
Manages game state and rules
"""

from enum import Enum
from typing import Any, Dict, Optional

from src.player import Player


class GamePhase(Enum):
    """Game phases"""

    PLACEMENT = "placement"
    BATTLE = "battle"
    FINISHED = "finished"


class Game:
    """Manages a Battleship game"""

    def __init__(self, player1_name: str, player2_name: str):
        """
        Initialize a new game

        Args:
            player1_name: Name of player 1
            player2_name: Name of player 2
        """
        self.player1 = Player(player1_name)
        self.player2 = Player(player2_name)
        self.current_player = self.player1
        self.phase = GamePhase.PLACEMENT
        self.winner: Optional[Player] = None

    def get_opponent(self, player: Player) -> Player:
        """
        Get the opponent of a given player

        Args:
            player: The player whose opponent to get

        Returns:
            The opponent player
        """
        return self.player2 if player == self.player1 else self.player1

    def both_players_ready(self) -> bool:
        """
        Check if both players have placed all their ships

        Returns:
            True if both players are ready, False otherwise
        """
        return self.player1.all_ships_placed() and self.player2.all_ships_placed()

    def start_battle(self) -> None:
        """Start the battle phase"""
        if not self.both_players_ready():
            raise ValueError("Both players must place all ships before starting battle")
        self.phase = GamePhase.BATTLE

    def fire_shot(self, player: Player, row: int, col: int) -> Dict[str, Any]:
        """
        Fire a shot from one player to opponent

        Args:
            player: The player firing the shot
            row: Target row
            col: Target column

        Returns:
            Result of the shot (hit/miss/sunk info)

        Raises:
            ValueError: If not player's turn or wrong game phase
        """
        if self.phase != GamePhase.BATTLE:
            raise ValueError("Cannot fire shots during placement phase")

        if player != self.current_player:
            raise ValueError("Not your turn")

        opponent = self.get_opponent(player)
        result = opponent.receive_shot(row, col)

        # Check if game is over
        if opponent.all_ships_sunk():
            self.phase = GamePhase.FINISHED
            self.winner = player

        # Switch turns
        self.current_player = opponent

        return result
