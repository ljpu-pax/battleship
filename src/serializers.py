"""
Serializers for converting game objects to/from JSON
"""

from typing import Any, Dict, List

from src.ai import AIPlayer
from src.game import Game
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
    # Determine if opponent is AI
    from src.ai import AIPlayer

    player2_is_ai = isinstance(game.player2, AIPlayer)

    if current_player_id == "player2":
        player1_data = serialize_player(game.player1, hide_ships=True)
        player2_data = serialize_player(game.player2, hide_ships=False, is_ai=player2_is_ai)
    else:
        player1_data = serialize_player(game.player1, hide_ships=False)
        player2_data = serialize_player(game.player2, hide_ships=True, is_ai=player2_is_ai)

    return {
        "phase": game.phase.value,
        "current_turn": "player1" if game.current_player == game.player1 else "player2",
        "winner": (
            None
            if game.winner is None
            else ("player1" if game.winner == game.player1 else "player2")
        ),
        "player1": player1_data,
        "player2": player2_data,
    }


def deserialize_orientation(orientation_str: str) -> Orientation:
    """Deserialize orientation from string"""
    return Orientation.HORIZONTAL if orientation_str == "horizontal" else Orientation.VERTICAL


def deserialize_ship_type(ship_type_str: str) -> ShipType:
    """Deserialize ship type from string"""
    return ShipType[ship_type_str.upper()]


def serialize_player_snapshot(player: Player) -> Dict[str, Any]:
    """Serialize full player state for persistence."""
    snapshot = {
        "name": player.name,
        "grid": [[cell.value for cell in row] for row in player.grid.cells],
        "ships": [
            {
                "type": ship.ship_type.name,
                "row": ship.row,
                "col": ship.col,
                "orientation": ship.orientation.value,
                "hits": ship.hits,
                "hit_positions": [list(position) for position in ship._hit_positions],
            }
            for ship in player.ships
        ],
        "shot_history": [list(position) for position in player._shot_history],
        "is_ai": isinstance(player, AIPlayer),
    }

    if isinstance(player, AIPlayer):
        snapshot["ai_state"] = {
            "shot_positions": [list(position) for position in player._shot_positions],
            "targets": [list(position) for position in player._targets],
            "hit_sequence": [list(position) for position in player._hit_sequence],
        }

    return snapshot


def deserialize_player_snapshot(snapshot: Dict[str, Any]) -> Player:
    """Rebuild a player from a persisted snapshot."""
    player = AIPlayer(snapshot["name"]) if snapshot.get("is_ai") else Player(snapshot["name"])

    player.grid = Grid(len(snapshot["grid"]))
    player.grid.cells = [[CellState(cell_state) for cell_state in row] for row in snapshot["grid"]]

    player.ships = []
    for ship_snapshot in snapshot["ships"]:
        ship = Ship(
            ShipType[ship_snapshot["type"]],
            ship_snapshot["row"],
            ship_snapshot["col"],
            Orientation(ship_snapshot["orientation"]),
        )
        ship.hits = ship_snapshot["hits"]
        ship._hit_positions = {
            (position[0], position[1]) for position in ship_snapshot["hit_positions"]
        }
        player.ships.append(ship)

    player._shot_history = {
        (position[0], position[1]) for position in snapshot.get("shot_history", [])
    }

    if isinstance(player, AIPlayer):
        ai_state = snapshot.get("ai_state", {})
        player._shot_positions = {
            (position[0], position[1]) for position in ai_state.get("shot_positions", [])
        }
        player._targets.clear()
        for position in ai_state.get("targets", []):
            player._targets.append((position[0], position[1]))
        player._hit_sequence = [
            (position[0], position[1]) for position in ai_state.get("hit_sequence", [])
        ]

    return player


def serialize_game_snapshot(game: Game, player2_joined: bool) -> Dict[str, Any]:
    """Serialize full game state for persistence."""
    return {
        "phase": game.phase.value,
        "current_turn": "player1" if game.current_player == game.player1 else "player2",
        "winner": (
            None
            if game.winner is None
            else ("player1" if game.winner == game.player1 else "player2")
        ),
        "player2_joined": player2_joined,
        "player1": serialize_player_snapshot(game.player1),
        "player2": serialize_player_snapshot(game.player2),
    }


def deserialize_game_snapshot(snapshot: Dict[str, Any]) -> tuple[Game, bool]:
    """Rebuild game state from a persisted snapshot."""
    game = Game(snapshot["player1"]["name"], snapshot["player2"]["name"])
    game.player1 = deserialize_player_snapshot(snapshot["player1"])
    game.player2 = deserialize_player_snapshot(snapshot["player2"])
    game.phase = game.phase.__class__(snapshot["phase"])
    game.current_player = game.player1 if snapshot["current_turn"] == "player1" else game.player2
    if snapshot["winner"] == "player1":
        game.winner = game.player1
    elif snapshot["winner"] == "player2":
        game.winner = game.player2
    else:
        game.winner = None

    return game, snapshot.get("player2_joined", False)
