"""
Tests for Player class - TDD approach
"""
import pytest
from src.player import Player
from src.ship import ShipType, Orientation
from src.grid import CellState


class TestPlayer:
    """Test suite for Player class"""

    def test_player_initialization(self):
        """Test player initialization"""
        player = Player("Player 1")
        assert player.name == "Player 1"
        assert player.grid.size == 10
        assert len(player.ships) == 0

    def test_can_place_ship_valid_horizontal(self):
        """Test that valid horizontal ship placement is allowed"""
        player = Player("Player 1")
        result = player.can_place_ship(ShipType.DESTROYER, 0, 0, Orientation.HORIZONTAL)
        assert result == True

    def test_can_place_ship_valid_vertical(self):
        """Test that valid vertical ship placement is allowed"""
        player = Player("Player 1")
        result = player.can_place_ship(ShipType.CRUISER, 2, 5, Orientation.VERTICAL)
        assert result == True

    def test_cannot_place_ship_out_of_bounds_horizontal(self):
        """Test that ship going out of bounds horizontally is rejected"""
        player = Player("Player 1")
        # Carrier is length 5, starting at col 8 would go to col 12 (out of bounds)
        result = player.can_place_ship(ShipType.CARRIER, 0, 8, Orientation.HORIZONTAL)
        assert result == False

    def test_cannot_place_ship_out_of_bounds_vertical(self):
        """Test that ship going out of bounds vertically is rejected"""
        player = Player("Player 1")
        # Battleship is length 4, starting at row 7 would go to row 10 (out of bounds)
        result = player.can_place_ship(ShipType.BATTLESHIP, 7, 0, Orientation.VERTICAL)
        assert result == False

    def test_cannot_place_overlapping_ships(self):
        """Test that overlapping ships are rejected"""
        player = Player("Player 1")
        # Place first ship horizontally at (0, 0)
        player.place_ship(ShipType.CRUISER, 0, 0, Orientation.HORIZONTAL)
        # Try to place another ship that would overlap at (0, 2)
        result = player.can_place_ship(ShipType.DESTROYER, 0, 2, Orientation.HORIZONTAL)
        assert result == False

    def test_can_place_adjacent_ships(self):
        """Test that adjacent (non-overlapping) ships are allowed"""
        player = Player("Player 1")
        # Place first ship horizontally at (0, 0) - occupies (0,0), (0,1), (0,2)
        player.place_ship(ShipType.CRUISER, 0, 0, Orientation.HORIZONTAL)
        # Place another ship at (1, 0) - should be allowed
        result = player.can_place_ship(ShipType.DESTROYER, 1, 0, Orientation.HORIZONTAL)
        assert result == True

    def test_place_ship_success(self):
        """Test successful ship placement"""
        player = Player("Player 1")
        ship = player.place_ship(ShipType.DESTROYER, 5, 5, Orientation.HORIZONTAL)
        assert ship is not None
        assert len(player.ships) == 1
        assert player.grid.get_cell(5, 5) == CellState.SHIP
        assert player.grid.get_cell(5, 6) == CellState.SHIP

    def test_place_ship_failure(self):
        """Test that invalid placement returns None"""
        player = Player("Player 1")
        ship = player.place_ship(ShipType.CARRIER, 0, 9, Orientation.HORIZONTAL)
        assert ship is None
        assert len(player.ships) == 0

    def test_all_ships_placed(self):
        """Test checking if all 5 ships are placed"""
        player = Player("Player 1")
        assert player.all_ships_placed() == False

        player.place_ship(ShipType.CARRIER, 0, 0, Orientation.HORIZONTAL)
        player.place_ship(ShipType.BATTLESHIP, 1, 0, Orientation.HORIZONTAL)
        player.place_ship(ShipType.CRUISER, 2, 0, Orientation.HORIZONTAL)
        player.place_ship(ShipType.SUBMARINE, 3, 0, Orientation.HORIZONTAL)
        assert player.all_ships_placed() == False

        player.place_ship(ShipType.DESTROYER, 4, 0, Orientation.HORIZONTAL)
        assert player.all_ships_placed() == True

    def test_all_ships_sunk(self):
        """Test checking if all ships are sunk"""
        player = Player("Player 1")
        player.place_ship(ShipType.DESTROYER, 0, 0, Orientation.HORIZONTAL)

        assert player.all_ships_sunk() == False

        # Sink the destroyer (length 2)
        ship = player.ships[0]
        ship.hit(0, 0)
        assert player.all_ships_sunk() == False
        ship.hit(0, 1)
        assert player.all_ships_sunk() == True

    def test_receive_shot_miss(self):
        """Test receiving a shot that misses"""
        player = Player("Player 1")
        player.place_ship(ShipType.DESTROYER, 5, 5, Orientation.HORIZONTAL)

        result = player.receive_shot(0, 0)
        assert result["result"] == "miss"
        assert result["ship_sunk"] is None
        assert player.grid.get_cell(0, 0) == CellState.MISS

    def test_receive_shot_hit(self):
        """Test receiving a shot that hits"""
        player = Player("Player 1")
        player.place_ship(ShipType.DESTROYER, 5, 5, Orientation.HORIZONTAL)

        result = player.receive_shot(5, 5)
        assert result["result"] == "hit"
        assert result["ship_sunk"] is None
        assert player.grid.get_cell(5, 5) == CellState.HIT

    def test_receive_shot_sunk(self):
        """Test receiving a shot that sinks a ship"""
        player = Player("Player 1")
        player.place_ship(ShipType.DESTROYER, 5, 5, Orientation.HORIZONTAL)

        # Hit first position
        result1 = player.receive_shot(5, 5)
        assert result1["result"] == "hit"
        assert result1["ship_sunk"] is None

        # Hit second position - should sink
        result2 = player.receive_shot(5, 6)
        assert result2["result"] == "hit"
        assert result2["ship_sunk"] == ShipType.DESTROYER

    def test_cannot_shoot_same_position_twice(self):
        """Test that shooting same position raises error"""
        player = Player("Player 1")
        player.receive_shot(3, 3)

        with pytest.raises(ValueError):
            player.receive_shot(3, 3)
