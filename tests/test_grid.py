"""
Tests for Grid class - TDD approach
"""

import pytest

from src.grid import CellState, Grid


class TestGrid:
    """Test suite for Grid class"""

    def test_grid_initialization(self):
        """Test that a grid is initialized with correct dimensions"""
        grid = Grid(size=10)
        assert grid.size == 10
        assert len(grid.cells) == 10
        assert len(grid.cells[0]) == 10

    def test_grid_cells_initially_empty(self):
        """Test that all cells are initially empty"""
        grid = Grid(size=10)
        for row in range(10):
            for col in range(10):
                assert grid.get_cell(row, col) == CellState.EMPTY

    def test_mark_cell_as_ship(self):
        """Test marking a cell as containing a ship"""
        grid = Grid(size=10)
        grid.mark_cell(3, 5, CellState.SHIP)
        assert grid.get_cell(3, 5) == CellState.SHIP

    def test_mark_cell_as_hit(self):
        """Test marking a cell as hit"""
        grid = Grid(size=10)
        grid.mark_cell(2, 4, CellState.SHIP)
        grid.mark_cell(2, 4, CellState.HIT)
        assert grid.get_cell(2, 4) == CellState.HIT

    def test_mark_cell_as_miss(self):
        """Test marking a cell as miss"""
        grid = Grid(size=10)
        grid.mark_cell(7, 8, CellState.MISS)
        assert grid.get_cell(7, 8) == CellState.MISS

    def test_is_valid_coordinate(self):
        """Test coordinate validation"""
        grid = Grid(size=10)
        assert grid.is_valid_coordinate(0, 0) == True
        assert grid.is_valid_coordinate(9, 9) == True
        assert grid.is_valid_coordinate(5, 5) == True
        assert grid.is_valid_coordinate(-1, 5) == False
        assert grid.is_valid_coordinate(5, -1) == False
        assert grid.is_valid_coordinate(10, 5) == False
        assert grid.is_valid_coordinate(5, 10) == False

    def test_get_cell_invalid_coordinate_raises_error(self):
        """Test that getting an invalid coordinate raises ValueError"""
        grid = Grid(size=10)
        with pytest.raises(ValueError):
            grid.get_cell(-1, 5)
        with pytest.raises(ValueError):
            grid.get_cell(5, 10)

    def test_mark_cell_invalid_coordinate_raises_error(self):
        """Test that marking an invalid coordinate raises ValueError"""
        grid = Grid(size=10)
        with pytest.raises(ValueError):
            grid.mark_cell(10, 10, CellState.SHIP)
