"""
Tests for Ship class - TDD approach
"""

import pytest

from src.ship import Orientation, Ship, ShipType


class TestShip:
    """Test suite for Ship class"""

    def test_ship_initialization(self):
        """Test ship initialization with proper attributes"""
        ship = Ship(ShipType.DESTROYER, 3, 4, Orientation.HORIZONTAL)
        assert ship.ship_type == ShipType.DESTROYER
        assert ship.length == 2
        assert ship.row == 3
        assert ship.col == 4
        assert ship.orientation == Orientation.HORIZONTAL

    def test_ship_types_have_correct_lengths(self):
        """Test that ship types have correct lengths"""
        assert ShipType.CARRIER.value == 5
        assert ShipType.BATTLESHIP.value == 4
        assert ShipType.CRUISER.value == 3
        assert ShipType.SUBMARINE.value == 3
        assert ShipType.DESTROYER.value == 2

    def test_get_coordinates_horizontal(self):
        """Test getting coordinates for horizontal ship"""
        ship = Ship(ShipType.CRUISER, 2, 3, Orientation.HORIZONTAL)
        coords = ship.get_coordinates()
        assert coords == [(2, 3), (2, 4), (2, 5)]

    def test_get_coordinates_vertical(self):
        """Test getting coordinates for vertical ship"""
        ship = Ship(ShipType.BATTLESHIP, 1, 5, Orientation.VERTICAL)
        coords = ship.get_coordinates()
        assert coords == [(1, 5), (2, 5), (3, 5), (4, 5)]

    def test_ship_not_sunk_initially(self):
        """Test that ship is not sunk when created"""
        ship = Ship(ShipType.DESTROYER, 0, 0, Orientation.HORIZONTAL)
        assert ship.is_sunk() == False

    def test_hit_ship(self):
        """Test hitting a ship"""
        ship = Ship(ShipType.DESTROYER, 0, 0, Orientation.HORIZONTAL)
        result = ship.hit(0, 0)
        assert result == True
        assert ship.hits == 1

    def test_hit_ship_invalid_coordinate(self):
        """Test hitting a ship at invalid coordinate"""
        ship = Ship(ShipType.DESTROYER, 0, 0, Orientation.HORIZONTAL)
        # Ship is at (0,0) and (0,1), so (0,2) is invalid
        result = ship.hit(0, 2)
        assert result == False
        assert ship.hits == 0

    def test_ship_sinks_when_all_positions_hit(self):
        """Test that ship sinks when all positions are hit"""
        ship = Ship(ShipType.DESTROYER, 5, 5, Orientation.HORIZONTAL)
        # Destroyer length is 2
        assert ship.is_sunk() == False
        ship.hit(5, 5)
        assert ship.is_sunk() == False
        ship.hit(5, 6)
        assert ship.is_sunk() == True

    def test_cannot_hit_same_position_twice(self):
        """Test that hitting same position twice only counts once"""
        ship = Ship(ShipType.CRUISER, 2, 2, Orientation.VERTICAL)
        ship.hit(2, 2)
        assert ship.hits == 1
        ship.hit(2, 2)
        assert ship.hits == 1  # Should still be 1

    def test_contains_coordinate(self):
        """Test checking if ship contains a coordinate"""
        ship = Ship(ShipType.SUBMARINE, 4, 3, Orientation.HORIZONTAL)
        # Submarine is at (4,3), (4,4), (4,5)
        assert ship.contains(4, 3) == True
        assert ship.contains(4, 4) == True
        assert ship.contains(4, 5) == True
        assert ship.contains(4, 6) == False
        assert ship.contains(3, 3) == False
