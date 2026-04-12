"""
Ship module for Battleship game
Represents ships and their states
"""

from enum import Enum
from typing import List, Set, Tuple


class ShipType(Enum):
    """Ship types with their lengths"""

    CARRIER = 5
    BATTLESHIP = 4
    CRUISER = 3
    SUBMARINE = 3
    DESTROYER = 2


class Orientation(Enum):
    """Ship orientation"""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Ship:
    """Represents a ship on the game board"""

    def __init__(self, ship_type: ShipType, row: int, col: int, orientation: Orientation):
        """
        Initialize a ship

        Args:
            ship_type: The type of ship
            row: Starting row position
            col: Starting column position
            orientation: Ship orientation (horizontal or vertical)
        """
        self.ship_type = ship_type
        self.length = ship_type.value
        self.row = row
        self.col = col
        self.orientation = orientation
        self.hits = 0
        self._hit_positions: Set[Tuple[int, int]] = set()

    def get_coordinates(self) -> List[Tuple[int, int]]:
        """
        Get all coordinates occupied by this ship

        Returns:
            List of (row, col) tuples
        """
        coordinates = []
        for i in range(self.length):
            if self.orientation == Orientation.HORIZONTAL:
                coordinates.append((self.row, self.col + i))
            else:  # VERTICAL
                coordinates.append((self.row + i, self.col))
        return coordinates

    def contains(self, row: int, col: int) -> bool:
        """
        Check if this ship occupies a given coordinate

        Args:
            row: Row to check
            col: Column to check

        Returns:
            True if ship occupies this coordinate, False otherwise
        """
        return (row, col) in self.get_coordinates()

    def hit(self, row: int, col: int) -> bool:
        """
        Register a hit on this ship

        Args:
            row: Row that was hit
            col: Column that was hit

        Returns:
            True if hit was valid (ship occupies this position), False otherwise
        """
        if not self.contains(row, col):
            return False

        # Only count the hit if this position hasn't been hit before
        if (row, col) not in self._hit_positions:
            self._hit_positions.add((row, col))
            self.hits += 1

        return True

    def is_sunk(self) -> bool:
        """
        Check if this ship is sunk

        Returns:
            True if all positions have been hit, False otherwise
        """
        return self.hits >= self.length
