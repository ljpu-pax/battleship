"""
Serializers for converting game objects to/from JSON
"""

from typing import Any, Dict, List, Optional

from src.game import Game, GamePhase
from src.grid import CellState, Grid
from src.player import Player
from src.ship import Orientation, Ship, ShipType


def serialize_cell_state(state: CellState) -> str:
    """Serialize a cell state to string"""
    return state.value


def serialize_grid(grid: Grid, hide_ships: bool = False) -> List[List[str]]:
    """
    Serialize a grid to 2D array

    Args:
        grid: The grid to serialize
        hide_ships: If True, hide ship positions (for opponent view)

    Returns:
        2D array of cell states
    """
    result = []
    for row in grid.cells:
        serialized_row = []
        for cell in row:
            if hide_ships and cell == CellState.SHIP:
                # Hide unhit ships from opponent
                serialized_row.append(CellState.EMPTY.value)
            else:
                serialized_row.append(cell.value)
        result.append(serialized_row)
    return result


def serialize_ship(ship: Ship) -> Dict[str, Any]:
    """Serialize a ship to dictionary"""
    return {
        "type": ship.ship_type.name,
        "length": ship.length,
        "row": ship.row,
        "col": ship.col,
        "orientation": ship.orientation.value,
        "hits": ship.hits,
        "is_sunk": ship.is_sunk(),
    }


def serialize_player(
    player: Player, hide_ships: bool = False, is_ai: bool = False
) -> Dict[str, Any]:
    """
    Serialize a player to dictionary

    Args:
        player: The player to serialize
        hide_ships: If True, hide ship positions in grid
        is_ai: If True, mark as AI player

    Returns:
        Dictionary representation of player
    """
    return {
        "name": player.name,
        "is_ai": is_ai,
        "grid": serialize_grid(player.grid, hide_ships),
        "ships": [serialize_ship(ship) for ship in player.ships] if not hide_ships else [],
        "all_ships_placed": player.all_ships_placed(),
        "all_ships_sunk": player.all_ships_sunk(),
    }


def serialize_game_state(game: Game, current_player_id: str = "player1") -> Dict[str, Any]:
    """
    Serialize game state from perspective of current player

    Args:
        game: The game to serialize
        current_player_id: "player1" or "player2"

    Returns:
        Dictionary representation of game state
    """
    is_player1 = current_player_id == "player1"
    current_player = game.player1 if is_player1 else game.player2
    opponent = game.player2 if is_player1 else game.player1

    # Determine if opponent is AI
    from src.ai import AIPlayer

    opponent_is_ai = isinstance(opponent, AIPlayer)

    return {
        "phase": game.phase.value,
        "current_turn": "player1" if game.current_player == game.player1 else "player2",
        "winner": (
            None
            if game.winner is None
            else ("player1" if game.winner == game.player1 else "player2")
        ),
        "your_board": serialize_player(current_player, hide_ships=False),
        "opponent_board": serialize_player(opponent, hide_ships=True, is_ai=opponent_is_ai),
    }


def deserialize_orientation(orientation_str: str) -> Orientation:
    """Deserialize orientation from string"""
    return Orientation.HORIZONTAL if orientation_str == "horizontal" else Orientation.VERTICAL


def deserialize_ship_type(ship_type_str: str) -> ShipType:
    """Deserialize ship type from string"""
    return ShipType[ship_type_str.upper()]
