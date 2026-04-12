"""
Tests for AI player - TDD approach
"""
import pytest
from src.ai import AIPlayer
from src.ship import ShipType, Orientation


class TestAIPlayer:
    """Test suite for AI player"""

    def test_ai_can_place_ships_randomly(self):
        """Test that AI can place all ships randomly"""
        ai = AIPlayer("AI")
        ai.place_ships_randomly()

        assert ai.all_ships_placed() == True
        assert len(ai.ships) == 5

    def test_ai_ships_dont_overlap(self):
        """Test that randomly placed ships don't overlap"""
        ai = AIPlayer("AI")
        ai.place_ships_randomly()

        # Get all coordinates occupied by ships
        all_coords = []
        for ship in ai.ships:
            all_coords.extend(ship.get_coordinates())

        # Check no duplicates
        assert len(all_coords) == len(set(all_coords))

    def test_ai_ships_within_bounds(self):
        """Test that all AI ships are within grid bounds"""
        ai = AIPlayer("AI")
        ai.place_ships_randomly()

        for ship in ai.ships:
            for row, col in ship.get_coordinates():
                assert 0 <= row < 10
                assert 0 <= col < 10

    def test_ai_makes_valid_shot(self):
        """Test that AI makes a valid shot"""
        ai = AIPlayer("AI")
        row, col = ai.get_next_shot()

        assert 0 <= row < 10
        assert 0 <= col < 10

    def test_ai_doesnt_repeat_shots(self):
        """Test that AI doesn't shoot same position twice"""
        ai = AIPlayer("AI")

        shots = set()
        for _ in range(20):
            row, col = ai.get_next_shot()
            coord = (row, col)
            assert coord not in shots
            shots.add(coord)
            # Simulate shot being taken
            ai.record_shot(row, col, "miss")

    def test_ai_targets_adjacent_after_hit(self):
        """Test that AI targets adjacent cells after a hit"""
        ai = AIPlayer("AI")

        # Simulate a hit at position (5, 5)
        ai.record_shot(5, 5, "hit")

        # AI should target adjacent cells
        # Get next few shots
        adjacent_coords = {(4, 5), (6, 5), (5, 4), (5, 6)}
        shots_taken = set()

        for _ in range(10):
            if not ai._targets:  # If no more targets, stop
                break
            row, col = ai.get_next_shot()
            shots_taken.add((row, col))
            # If it's a hit, record it
            if (row, col) in adjacent_coords:
                ai.record_shot(row, col, "hit")
            else:
                ai.record_shot(row, col, "miss")

        # At least one of the adjacent cells should have been targeted
        assert len(shots_taken.intersection(adjacent_coords)) > 0

    def test_ai_continues_in_direction_after_consecutive_hits(self):
        """Test that AI continues in same direction after consecutive hits"""
        ai = AIPlayer("AI")

        # Simulate hits at (5, 5) and (5, 6)
        ai.record_shot(5, 5, "hit")
        ai.record_shot(5, 6, "hit")

        # AI should target (5, 4) or (5, 7) to continue the line
        expected_targets = {(5, 4), (5, 7)}

        shots_taken = set()
        for _ in range(5):
            if not ai._targets:
                break
            row, col = ai.get_next_shot()
            shots_taken.add((row, col))
            ai.record_shot(row, col, "miss")

        # One of the line continuation shots should be taken
        assert len(shots_taken.intersection(expected_targets)) > 0

    def test_ai_clears_targets_after_ship_sunk(self):
        """Test that AI clears target queue after sinking a ship"""
        ai = AIPlayer("AI")

        # Simulate hitting and sinking a ship
        ai.record_shot(5, 5, "hit")
        ai.record_shot(5, 6, "hit")

        # There should be targets queued
        assert len(ai._targets) > 0

        # Now sink the ship
        ai.record_shot(5, 7, "sunk")

        # Targets should be cleared
        assert len(ai._targets) == 0

    def test_ai_random_mode_after_sinking(self):
        """Test that AI returns to random targeting after sinking ship"""
        ai = AIPlayer("AI")

        # Simulate sinking a ship
        ai.record_shot(5, 5, "hit")
        ai.record_shot(5, 6, "sunk")

        # Should be back in random mode
        assert len(ai._targets) == 0
        assert len(ai._hit_sequence) == 0

        # Next shot should be random (not adjacent to previous)
        row, col = ai.get_next_shot()
        assert 0 <= row < 10
        assert 0 <= col < 10
