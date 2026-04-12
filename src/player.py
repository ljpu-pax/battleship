"""
Player module for Battleship game
Represents a player with their grid and ships
"""
from typing import List, Optional, Dict, Any
from src.grid import Grid, CellState
from src.ship import Ship, ShipType, Orientation


class Player:
    """Represents a player in the game"""

    def __init__(self, name: str, grid_size: int = 10):
        """
        Initialize a player

        Args:
            name: Player's name
            grid_size: Size of the game grid (default 10x10)
        """
        self.name = name
        self.grid = Grid(grid_size)
        self.ships: List[Ship] = []
        self._shot_history: set = set()

    def can_place_ship(
        self,
        ship_type: ShipType,
        row: int,
        col: int,
        orientation: Orientation
    ) -> bool:
        """
        Check if a ship can be placed at the given position

        Args:
            ship_type: Type of ship to place
            row: Starting row
            col: Starting column
            orientation: Ship orientation

        Returns:
            True if placement is valid, False otherwise
        """
        ship_length = ship_type.value

        # Check if ship would go out of bounds
        if orientation == Orientation.HORIZONTAL:
            if col + ship_length > self.grid.size:
                return False
        else:  # VERTICAL
            if row + ship_length > self.grid.size:
                return False

        # Check if any position is already occupied
        temp_ship = Ship(ship_type, row, col, orientation)
        for r, c in temp_ship.get_coordinates():
            if self.grid.get_cell(r, c) == CellState.SHIP:
                return False

        return True

    def place_ship(
        self,
        ship_type: ShipType,
        row: int,
        col: int,
        orientation: Orientation
    ) -> Optional[Ship]:
        """
        Place a ship on the grid

        Args:
            ship_type: Type of ship to place
            row: Starting row
            col: Starting column
            orientation: Ship orientation

        Returns:
            The placed Ship object if successful, None otherwise
        """
        if not self.can_place_ship(ship_type, row, col, orientation):
            return None

        ship = Ship(ship_type, row, col, orientation)
        self.ships.append(ship)

        # Mark grid cells as occupied by ship
        for r, c in ship.get_coordinates():
            self.grid.mark_cell(r, c, CellState.SHIP)

        return ship

    def all_ships_placed(self) -> bool:
        """
        Check if all 5 ships have been placed

        Returns:
            True if all ships are placed, False otherwise
        """
        return len(self.ships) == 5

    def all_ships_sunk(self) -> bool:
        """
        Check if all ships are sunk

        Returns:
            True if all ships are sunk, False otherwise
        """
        if len(self.ships) == 0:
            return False
        return all(ship.is_sunk() for ship in self.ships)

    def receive_shot(self, row: int, col: int) -> Dict[str, Any]:
        """
        Process an incoming shot

        Args:
            row: Row being shot at
            col: Column being shot at

        Returns:
            Dict with result information:
                - result: "hit", "miss"
                - ship_sunk: ShipType if a ship was sunk, None otherwise

        Raises:
            ValueError: If position has already been shot
        """
        if (row, col) in self._shot_history:
            raise ValueError(f"Position ({row}, {col}) has already been shot")

        self._shot_history.add((row, col))

        # Check if any ship is hit
        hit_ship = None
        for ship in self.ships:
            if ship.contains(row, col):
                hit_ship = ship
                break

        if hit_ship:
            hit_ship.hit(row, col)
            self.grid.mark_cell(row, col, CellState.HIT)

            # Check if ship is sunk
            ship_sunk = hit_ship.ship_type if hit_ship.is_sunk() else None

            return {
                "result": "hit",
                "ship_sunk": ship_sunk
            }
        else:
            self.grid.mark_cell(row, col, CellState.MISS)
            return {
                "result": "miss",
                "ship_sunk": None
            }
