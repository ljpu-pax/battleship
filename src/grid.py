"""
Grid module for Battleship game
Represents the game board
"""
from enum import Enum
from typing import List


class CellState(Enum):
    """Possible states for a grid cell"""
    EMPTY = "empty"
    SHIP = "ship"
    HIT = "hit"
    MISS = "miss"


class Grid:
    """Represents a game grid/board"""

    def __init__(self, size: int = 10):
        """
        Initialize a grid with given size

        Args:
            size: The dimension of the square grid (default 10x10)
        """
        self.size = size
        self.cells: List[List[CellState]] = [
            [CellState.EMPTY for _ in range(size)]
            for _ in range(size)
        ]

    def is_valid_coordinate(self, row: int, col: int) -> bool:
        """
        Check if a coordinate is within grid bounds

        Args:
            row: Row index
            col: Column index

        Returns:
            True if coordinate is valid, False otherwise
        """
        return 0 <= row < self.size and 0 <= col < self.size

    def get_cell(self, row: int, col: int) -> CellState:
        """
        Get the state of a cell at given coordinates

        Args:
            row: Row index
            col: Column index

        Returns:
            The CellState at the given position

        Raises:
            ValueError: If coordinates are out of bounds
        """
        if not self.is_valid_coordinate(row, col):
            raise ValueError(f"Invalid coordinate: ({row}, {col})")
        return self.cells[row][col]

    def mark_cell(self, row: int, col: int, state: CellState) -> None:
        """
        Mark a cell with a given state

        Args:
            row: Row index
            col: Column index
            state: The CellState to set

        Raises:
            ValueError: If coordinates are out of bounds
        """
        if not self.is_valid_coordinate(row, col):
            raise ValueError(f"Invalid coordinate: ({row}, {col})")
        self.cells[row][col] = state
