"""
AI player module for Battleship
Implements intelligent AI opponent
"""

import random
from collections import deque
from typing import List, Optional, Set, Tuple

from src.player import Player
from src.ship import Orientation, ShipType


class AIPlayer(Player):
    """AI player with intelligent targeting"""

    def __init__(self, name: str = "AI", grid_size: int = 10):
        """
        Initialize AI player

        Args:
            name: AI player name
            grid_size: Size of game grid
        """
        super().__init__(name, grid_size)
        self._shot_positions: Set[Tuple[int, int]] = set()
        self._targets: deque = deque()  # Queue of positions to target
        self._hit_sequence: List[Tuple[int, int]] = []  # Consecutive hits

    def place_ships_randomly(self) -> None:
        """Randomly place all ships on the grid"""
        ship_types = [
            ShipType.CARRIER,
            ShipType.BATTLESHIP,
            ShipType.CRUISER,
            ShipType.SUBMARINE,
            ShipType.DESTROYER,
        ]

        for ship_type in ship_types:
            placed = False
            max_attempts = 1000
            attempts = 0

            while not placed and attempts < max_attempts:
                row = random.randint(0, self.grid.size - 1)
                col = random.randint(0, self.grid.size - 1)
                orientation = random.choice([Orientation.HORIZONTAL, Orientation.VERTICAL])

                if self.can_place_ship(ship_type, row, col, orientation):
                    self.place_ship(ship_type, row, col, orientation)
                    placed = True

                attempts += 1

            if not placed:
                raise RuntimeError(
                    f"Failed to place {ship_type.name} after {max_attempts} attempts"
                )

    def get_next_shot(self) -> Tuple[int, int]:
        """
        Get next shot coordinates using intelligent targeting

        Returns:
            Tuple of (row, col) for next shot
        """
        # If we have specific targets (from hits), use those
        if self._targets:
            while self._targets:
                target = self._targets.popleft()
                if target not in self._shot_positions:
                    return target

        # Otherwise, make a random shot
        return self._get_random_shot()

    def _get_random_shot(self) -> Tuple[int, int]:
        """
        Get a random shot that hasn't been fired yet

        Returns:
            Tuple of (row, col)
        """
        while True:
            row = random.randint(0, self.grid.size - 1)
            col = random.randint(0, self.grid.size - 1)

            if (row, col) not in self._shot_positions:
                return row, col

    def record_shot(self, row: int, col: int, result: str) -> None:
        """
        Record the result of a shot and update targeting strategy

        Args:
            row: Row that was shot
            col: Column that was shot
            result: Result of shot ("hit", "miss", or "sunk")
        """
        self._shot_positions.add((row, col))

        if result == "hit":
            self._hit_sequence.append((row, col))

            # If we have consecutive hits, try to continue in that direction
            if len(self._hit_sequence) >= 2:
                self._add_directional_targets()
            else:
                # First hit, add adjacent cells
                self._add_adjacent_targets(row, col)

        elif result == "sunk":
            # Ship is sunk, clear targets and hit sequence
            self._targets.clear()
            self._hit_sequence.clear()

        # If result is "miss", don't add targets

    def _add_adjacent_targets(self, row: int, col: int) -> None:
        """
        Add adjacent cells to target queue

        Args:
            row: Center row
            col: Center column
        """
        # Add cells above, below, left, right
        adjacent = [
            (row - 1, col),  # up
            (row + 1, col),  # down
            (row, col - 1),  # left
            (row, col + 1),  # right
        ]

        for r, c in adjacent:
            if self._is_valid_target(r, c):
                self._targets.append((r, c))

    def _add_directional_targets(self) -> None:
        """Add targets in the direction of consecutive hits"""
        if len(self._hit_sequence) < 2:
            return

        # Get last two hits to determine direction
        last = self._hit_sequence[-1]
        prev = self._hit_sequence[-2]

        row_diff = last[0] - prev[0]
        col_diff = last[1] - prev[1]

        # Clear existing targets and add directional ones
        self._targets.clear()

        # Continue in the same direction
        next_pos = (last[0] + row_diff, last[1] + col_diff)
        if self._is_valid_target(next_pos[0], next_pos[1]):
            self._targets.append(next_pos)

        # Also try the opposite direction from the first hit
        first = self._hit_sequence[0]
        opposite_pos = (first[0] - row_diff, first[1] - col_diff)
        if self._is_valid_target(opposite_pos[0], opposite_pos[1]):
            self._targets.append(opposite_pos)

    def _is_valid_target(self, row: int, col: int) -> bool:
        """
        Check if a position is a valid target

        Args:
            row: Row to check
            col: Column to check

        Returns:
            True if valid target, False otherwise
        """
        return (
            0 <= row < self.grid.size
            and 0 <= col < self.grid.size
            and (row, col) not in self._shot_positions
        )
