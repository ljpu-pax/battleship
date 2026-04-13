"""
Game Manager for handling multiple game sessions
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from src.ai import AIPlayer
from src.game import Game
from src.persistence import SQLiteGameRepository
from src.serializers import deserialize_game_snapshot, serialize_game_snapshot
from src.ship import Orientation, Ship, ShipType


class GameSession:
    """Represents a game session with metadata"""

    def __init__(
        self,
        game_id: str,
        game: Game,
        mode: str,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        player2_joined: bool | None = None,
    ):
        self.game_id = game_id
        self.game = game
        self.mode = mode  # "ai" or "multiplayer"
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self.player2_joined = player2_joined if player2_joined is not None else mode == "ai"

    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.now(timezone.utc)


class GameManager:
    """Manages multiple game sessions"""

    def __init__(self):
        self.games: Dict[str, GameSession] = {}
        self.repository: SQLiteGameRepository | None = None
        self.configure_storage(os.getenv("BATTLESHIP_DB_URL", "sqlite:///./battleship.db"))

    def configure_storage(self, database_url: str) -> None:
        """Configure backing storage."""
        self.repository = SQLiteGameRepository(database_url)

    def _save_session(self, session: GameSession) -> None:
        """Persist a session snapshot."""
        if not self.repository:
            return

        self.repository.save_game(
            game_id=session.game_id,
            mode=session.mode,
            state=serialize_game_snapshot(session.game, session.player2_joined),
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    def persist_game(self, game_id: str) -> None:
        """Persist a known session after mutation."""
        session = self.games.get(game_id)
        if session:
            self._save_session(session)

    def record_event(
        self,
        game_id: str,
        event_type: str,
        player: str | None,
        payload: dict,
        created_at: datetime | None = None,
    ) -> None:
        """Append a persisted history event."""
        if not self.repository:
            return

        self.repository.append_event(
            game_id=game_id,
            event_type=event_type,
            player=player,
            payload=payload,
            created_at=created_at or datetime.now(timezone.utc),
        )

    def create_game(self, player1_name: str, mode: str = "ai") -> str:
        """
        Create a new game session

        Args:
            player1_name: Name of the first player
            mode: "ai" or "multiplayer"

        Returns:
            Game ID
        """
        game_id = str(uuid.uuid4())
        game = Game(player1_name, "Waiting for player 2" if mode == "multiplayer" else "AI")

        if mode == "ai":
            game.player2 = AIPlayer("AI")
            game.player2.place_ships_randomly()

        session = GameSession(game_id, game, mode)
        self.games[game_id] = session
        self._save_session(session)
        self.record_event(
            game_id,
            "game_created",
            "player1",
            {"mode": mode, "player_name": player1_name},
            session.created_at,
        )
        return game_id

    def join_game(self, game_id: str, player2_name: str) -> Optional[GameSession]:
        """
        Join an existing multiplayer game as player 2.
        """
        session = self.get_game(game_id)
        if not session:
            return None

        if session.mode != "multiplayer":
            raise ValueError("Only multiplayer games can be joined")

        if session.player2_joined:
            raise ValueError("Game already has two players")

        session.game.player2.name = player2_name
        session.player2_joined = True
        session.update_timestamp()
        self._save_session(session)
        self.record_event(
            game_id,
            "player_joined",
            "player2",
            {"player_name": player2_name},
            session.updated_at,
        )
        return session

    def get_game(self, game_id: str) -> Optional[GameSession]:
        """
        Get a game session by ID
        """
        session = self.games.get(game_id)
        if session:
            return session

        if not self.repository:
            return None

        stored = self.repository.get_game(game_id)
        if not stored:
            return None

        game, player2_joined = deserialize_game_snapshot(stored["state"])
        session = GameSession(
            game_id=game_id,
            game=game,
            mode=stored["mode"],
            created_at=stored["created_at"],
            updated_at=stored["updated_at"],
            player2_joined=player2_joined,
        )
        self.games[game_id] = session
        return session

    def delete_game(self, game_id: str) -> bool:
        """
        Delete a game session
        """
        in_memory_deleted = game_id in self.games
        self.games.pop(game_id, None)
        persisted_deleted = self.repository.delete_game(game_id) if self.repository else False
        return in_memory_deleted or persisted_deleted

    def list_games(self) -> list:
        """
        List all active games
        """
        if self.repository:
            for stored in self.repository.list_games():
                if stored["game_id"] not in self.games:
                    game, player2_joined = deserialize_game_snapshot(stored["state"])
                    self.games[stored["game_id"]] = GameSession(
                        game_id=stored["game_id"],
                        game=game,
                        mode=stored["mode"],
                        created_at=stored["created_at"],
                        updated_at=stored["updated_at"],
                        player2_joined=player2_joined,
                    )

        return [
            {
                "game_id": session.game_id,
                "mode": session.mode,
                "phase": session.game.phase.value,
                "created_at": session.created_at.isoformat(),
            }
            for session in self.games.values()
        ]

    def get_history(self, game_id: str) -> list[dict]:
        """Fetch persisted history for a game."""
        if not self.repository:
            return []
        return self.repository.get_game_history(game_id)

    def get_player_stats(self, player_name: str) -> dict:
        """Fetch persisted player stats."""
        if not self.repository:
            return {
                "player_name": player_name,
                "games_played": 0,
                "wins": 0,
                "losses": 0,
                "active_games": 0,
                "win_rate": 0,
            }
        return self.repository.get_player_stats(player_name)

    def get_replay(self, game_id: str) -> dict:
        """Build replay steps and summary for a game."""
        history = self.get_history(game_id)
        shot_events = [event for event in history if event["event_type"] == "shot_fired"]
        placement_events = [event for event in history if event["event_type"] == "ship_placed"]

        steps = []
        player_hits = {"player1": 0, "player2": 0}

        for turn_number, event in enumerate(shot_events, start=1):
            player = event["player"] or "unknown"
            if event.get("result") in {"hit", "sunk"} and player in player_hits:
                player_hits[player] += 1

            steps.append(
                {
                    "turn_number": turn_number,
                    "player": player,
                    "row": event.get("row"),
                    "col": event.get("col"),
                    "result": event.get("result"),
                    "ship_sunk": event.get("ship_sunk"),
                    "winner": event.get("winner"),
                    "created_at": event["created_at"],
                }
            )

        player1_fleet = [["empty" for _ in range(10)] for _ in range(10)]
        player2_fleet = [["empty" for _ in range(10)] for _ in range(10)]

        for event in placement_events:
            player = event["player"]
            ship_type = ShipType[event["ship_type"]]
            orientation = Orientation(event["orientation"])
            ship = Ship(ship_type, int(event["row"]), int(event["col"]), orientation)
            target_grid = player1_fleet if player == "player1" else player2_fleet

            for row, col in ship.get_coordinates():
                target_grid[row][col] = "ship"

        return {
            "game_id": game_id,
            "steps": steps,
            "fleets": {
                "player1": player1_fleet,
                "player2": player2_fleet,
            },
            "summary": {
                "total_turns": len(steps),
                "player1_hits": player_hits["player1"],
                "player2_hits": player_hits["player2"],
            },
        }

    def get_player_analytics(self, player_name: str) -> dict:
        """Aggregate hit rate, turn counts, and recent games for a player."""
        stats = self.get_player_stats(player_name)
        if not self.repository:
            return {
                **stats,
                "hit_rate": 0,
                "average_turns_per_game": 0,
                "recent_games": [],
            }

        relevant_games = []
        total_shots = 0
        total_hits = 0
        total_turns = 0

        for stored in self.repository.list_games():
            state = stored["state"]
            if player_name not in (state["player1"]["name"], state["player2"]["name"]):
                continue

            history = self.repository.get_game_history(stored["game_id"])
            shot_events = [event for event in history if event["event_type"] == "shot_fired"]
            player_key = "player1" if state["player1"]["name"] == player_name else "player2"
            player_shots = [event for event in shot_events if event["player"] == player_key]
            player_hit_count = sum(
                1 for event in player_shots if event.get("result") in {"hit", "sunk"}
            )

            total_shots += len(player_shots)
            total_hits += player_hit_count
            total_turns += len(shot_events)

            relevant_games.append(
                {
                    "game_id": stored["game_id"],
                    "mode": stored["mode"],
                    "phase": state["phase"],
                    "winner": (state[state["winner"]]["name"] if state.get("winner") else None),
                    "turns": len(shot_events),
                    "hit_rate": 0 if not player_shots else player_hit_count / len(player_shots),
                    "updated_at": stored["updated_at"].isoformat(),
                }
            )

        relevant_games.sort(key=lambda game: game["updated_at"], reverse=True)

        games_played = stats["games_played"]
        return {
            **stats,
            "hit_rate": 0 if total_shots == 0 else total_hits / total_shots,
            "average_turns_per_game": 0 if games_played == 0 else total_turns / games_played,
            "recent_games": relevant_games[:5],
        }
