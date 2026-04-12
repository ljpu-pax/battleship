"""
Tests for Game class - TDD approach
"""

import pytest

from src.game import Game, GamePhase
from src.ship import Orientation, ShipType


class TestGame:
    """Test suite for Game class"""

    def test_game_initialization(self):
        """Test game initialization"""
        game = Game("Player 1", "Player 2")
        assert game.player1.name == "Player 1"
        assert game.player2.name == "Player 2"
        assert game.current_player == game.player1
        assert game.phase == GamePhase.PLACEMENT
        assert game.winner is None

    def test_get_opponent(self):
        """Test getting opponent player"""
        game = Game("Player 1", "Player 2")
        assert game.get_opponent(game.player1) == game.player2
        assert game.get_opponent(game.player2) == game.player1

    def test_phase_transitions_to_battle_when_both_ready(self):
        """Test that game transitions to battle phase when both players ready"""
        game = Game("Player 1", "Player 2")

        # Place all ships for player 1
        game.player1.place_ship(ShipType.CARRIER, 0, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.BATTLESHIP, 1, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.CRUISER, 2, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.SUBMARINE, 3, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.DESTROYER, 4, 0, Orientation.HORIZONTAL)

        # Still in placement phase
        assert game.phase == GamePhase.PLACEMENT

        # Place all ships for player 2
        game.player2.place_ship(ShipType.CARRIER, 0, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.BATTLESHIP, 1, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.CRUISER, 2, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.SUBMARINE, 3, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.DESTROYER, 4, 0, Orientation.HORIZONTAL)

        # Check if ready to start
        if game.both_players_ready():
            game.start_battle()

        assert game.phase == GamePhase.BATTLE

    def test_both_players_ready(self):
        """Test checking if both players are ready"""
        game = Game("Player 1", "Player 2")
        assert game.both_players_ready() == False

        # Place all ships for player 1
        game.player1.place_ship(ShipType.CARRIER, 0, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.BATTLESHIP, 1, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.CRUISER, 2, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.SUBMARINE, 3, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.DESTROYER, 4, 0, Orientation.HORIZONTAL)

        assert game.both_players_ready() == False

        # Place all ships for player 2
        game.player2.place_ship(ShipType.CARRIER, 0, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.BATTLESHIP, 1, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.CRUISER, 2, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.SUBMARINE, 3, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.DESTROYER, 4, 0, Orientation.HORIZONTAL)

        assert game.both_players_ready() == True

    def test_fire_shot_switches_turn(self):
        """Test that firing a shot switches the current player"""
        game = self._setup_game_in_battle()

        assert game.current_player == game.player1

        # Player 1 fires
        game.fire_shot(game.player1, 0, 0)

        # Turn should switch to player 2
        assert game.current_player == game.player2

    def test_fire_shot_returns_result(self):
        """Test that firing a shot returns correct result"""
        game = self._setup_game_in_battle()

        # Player 1 fires at empty position
        result = game.fire_shot(game.player1, 5, 5)
        assert result["result"] == "miss"

        # Player 2 fires at player 1's ship (at 0,0)
        result = game.fire_shot(game.player2, 0, 0)
        assert result["result"] == "hit"

    def test_cannot_fire_when_not_your_turn(self):
        """Test that players cannot fire when it's not their turn"""
        game = self._setup_game_in_battle()

        # Current player is player1, so player2 cannot fire
        with pytest.raises(ValueError):
            game.fire_shot(game.player2, 0, 0)

    def test_cannot_fire_during_placement_phase(self):
        """Test that players cannot fire during placement phase"""
        game = Game("Player 1", "Player 2")

        with pytest.raises(ValueError):
            game.fire_shot(game.player1, 0, 0)

    def test_game_ends_when_all_ships_sunk(self):
        """Test that game ends when all opponent ships are sunk"""
        game = self._setup_game_in_battle()

        # Sink all of player 2's ships (just destroyer at 4,0-4,1 for simplicity)
        # Player 2 only has a destroyer
        # Actually need to sink all ships, let me simplify the setup
        game = Game("Player 1", "Player 2")

        # Only place destroyers for quick test
        game.player1.place_ship(ShipType.DESTROYER, 0, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.DESTROYER, 5, 5, Orientation.HORIZONTAL)

        game.player1.place_ship(ShipType.CARRIER, 1, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.BATTLESHIP, 2, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.CRUISER, 3, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.SUBMARINE, 4, 0, Orientation.HORIZONTAL)

        game.player2.place_ship(ShipType.CARRIER, 6, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.BATTLESHIP, 7, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.CRUISER, 8, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.SUBMARINE, 9, 0, Orientation.HORIZONTAL)

        game.start_battle()

        assert game.phase == GamePhase.BATTLE
        assert game.winner is None

        # Player 1 sinks all of player 2's ships
        # Player 2's carrier at 6,0-6,4
        game.fire_shot(game.player1, 6, 0)
        game.fire_shot(game.player2, 0, 0)  # dummy
        game.fire_shot(game.player1, 6, 1)
        game.fire_shot(game.player2, 0, 1)  # dummy
        game.fire_shot(game.player1, 6, 2)
        game.fire_shot(game.player2, 1, 0)  # dummy
        game.fire_shot(game.player1, 6, 3)
        game.fire_shot(game.player2, 1, 1)  # dummy
        game.fire_shot(game.player1, 6, 4)

        # Battleship at 7,0-7,3
        game.fire_shot(game.player2, 1, 2)  # dummy
        game.fire_shot(game.player1, 7, 0)
        game.fire_shot(game.player2, 1, 3)  # dummy
        game.fire_shot(game.player1, 7, 1)
        game.fire_shot(game.player2, 1, 4)  # dummy
        game.fire_shot(game.player1, 7, 2)
        game.fire_shot(game.player2, 2, 0)  # dummy
        game.fire_shot(game.player1, 7, 3)

        # Cruiser at 8,0-8,2
        game.fire_shot(game.player2, 2, 1)  # dummy
        game.fire_shot(game.player1, 8, 0)
        game.fire_shot(game.player2, 2, 2)  # dummy
        game.fire_shot(game.player1, 8, 1)
        game.fire_shot(game.player2, 2, 3)  # dummy
        game.fire_shot(game.player1, 8, 2)

        # Submarine at 9,0-9,2
        game.fire_shot(game.player2, 3, 0)  # dummy
        game.fire_shot(game.player1, 9, 0)
        game.fire_shot(game.player2, 3, 1)  # dummy
        game.fire_shot(game.player1, 9, 1)
        game.fire_shot(game.player2, 3, 2)  # dummy
        game.fire_shot(game.player1, 9, 2)

        # Destroyer at 5,5-5,6
        game.fire_shot(game.player2, 4, 0)  # dummy
        game.fire_shot(game.player1, 5, 5)
        game.fire_shot(game.player2, 4, 1)  # dummy
        result = game.fire_shot(game.player1, 5, 6)

        # Game should be over
        assert game.phase == GamePhase.FINISHED
        assert game.winner == game.player1

    def _setup_game_in_battle(self):
        """Helper to set up a game in battle phase"""
        game = Game("Player 1", "Player 2")

        # Place all ships for both players
        game.player1.place_ship(ShipType.CARRIER, 0, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.BATTLESHIP, 1, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.CRUISER, 2, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.SUBMARINE, 3, 0, Orientation.HORIZONTAL)
        game.player1.place_ship(ShipType.DESTROYER, 4, 0, Orientation.HORIZONTAL)

        game.player2.place_ship(ShipType.CARRIER, 0, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.BATTLESHIP, 1, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.CRUISER, 2, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.SUBMARINE, 3, 0, Orientation.HORIZONTAL)
        game.player2.place_ship(ShipType.DESTROYER, 4, 0, Orientation.HORIZONTAL)

        game.start_battle()
        return game
