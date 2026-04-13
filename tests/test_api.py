"""
Tests for FastAPI endpoints - TDD approach
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app, game_manager


class TestAPI:
    """Test suite for API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test client and clear games before each test"""
        game_manager.configure_storage(f"sqlite:///{tmp_path / 'test.db'}")
        self.client = TestClient(app)
        game_manager.games.clear()
        yield
        game_manager.games.clear()
        if game_manager.repository:
            game_manager.repository.delete_all()

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_create_game_ai_mode(self):
        """Test creating a game in AI mode"""
        response = self.client.post("/api/games", json={"player_name": "TestPlayer", "mode": "ai"})
        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert data["mode"] == "ai"
        assert data["phase"] == "placement"
        assert "player1" in data
        assert "player2" in data

    def test_create_game_multiplayer_mode(self):
        """Test creating a game in multiplayer mode"""
        response = self.client.post(
            "/api/games", json={"player_name": "Player1", "mode": "multiplayer"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert data["mode"] == "multiplayer"
        assert data["phase"] == "placement"
        assert "player1" in data
        assert "player2" in data
        assert data["player2"]["name"] == "Waiting for player 2"

    def test_create_game_invalid_mode(self):
        """Test creating game with invalid mode"""
        response = self.client.post(
            "/api/games", json={"player_name": "TestPlayer", "mode": "invalid"}
        )
        assert response.status_code == 400

    def test_list_games(self):
        """Test listing all games"""
        # Create two games
        self.client.post("/api/games", json={"player_name": "Player1", "mode": "ai"})
        self.client.post("/api/games", json={"player_name": "Player2", "mode": "multiplayer"})

        response = self.client.get("/api/games")
        assert response.status_code == 200
        data = response.json()
        assert len(data["games"]) == 2

    def test_get_game(self):
        """Test getting game state"""
        # Create game
        create_response = self.client.post(
            "/api/games", json={"player_name": "TestPlayer", "mode": "ai"}
        )
        game_id = create_response.json()["game_id"]

        # Get game
        response = self.client.get(f"/api/games/{game_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["game_id"] == game_id
        assert data["mode"] == "ai"
        assert "phase" in data
        assert "player1" in data
        assert "player2" in data

    def test_get_game_recovers_multiplayer_session_from_database(self):
        """Test multiplayer game state persists beyond in-memory session cache"""
        create_response = self.client.post(
            "/api/games", json={"player_name": "Host", "mode": "multiplayer"}
        )
        game_id = create_response.json()["game_id"]

        self.client.post(f"/api/games/{game_id}/join", json={"player_name": "Guest"})
        self.client.post(
            f"/api/games/{game_id}/place-ship?player=player1",
            json={
                "ship_type": "CARRIER",
                "row": 0,
                "col": 0,
                "orientation": "horizontal",
            },
        )

        game_manager.games.clear()

        response = self.client.get(f"/api/games/{game_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["player1"]["name"] == "Host"
        assert data["player2"]["name"] == "Guest"
        assert data["player1"]["grid"][0][0] == "ship"

    def test_game_history_records_multiplayer_events(self):
        """Test history endpoint returns join, placement, and shot events."""
        create_response = self.client.post(
            "/api/games", json={"player_name": "Host", "mode": "multiplayer"}
        )
        game_id = create_response.json()["game_id"]

        self.client.post(f"/api/games/{game_id}/join", json={"player_name": "Guest"})

        player1_ships = [
            ("CARRIER", 0, 0, "horizontal"),
            ("BATTLESHIP", 1, 0, "horizontal"),
            ("CRUISER", 2, 0, "horizontal"),
            ("SUBMARINE", 3, 0, "horizontal"),
            ("DESTROYER", 4, 0, "horizontal"),
        ]
        player2_ships = [
            ("CARRIER", 0, 0, "horizontal"),
            ("BATTLESHIP", 1, 0, "horizontal"),
            ("CRUISER", 2, 0, "horizontal"),
            ("SUBMARINE", 3, 0, "horizontal"),
            ("DESTROYER", 4, 0, "horizontal"),
        ]

        for ship_type, row, col, orientation in player1_ships:
            self.client.post(
                f"/api/games/{game_id}/place-ship?player=player1",
                json={
                    "ship_type": ship_type,
                    "row": row,
                    "col": col,
                    "orientation": orientation,
                },
            )

        for ship_type, row, col, orientation in player2_ships:
            self.client.post(
                f"/api/games/{game_id}/place-ship?player=player2",
                json={
                    "ship_type": ship_type,
                    "row": row,
                    "col": col,
                    "orientation": orientation,
                },
            )

        fire_response = self.client.post(
            f"/api/games/{game_id}/fire?player=player1", json={"row": 9, "col": 9}
        )
        assert fire_response.status_code == 200

        history_response = self.client.get(f"/api/games/{game_id}/history")
        assert history_response.status_code == 200

        history = history_response.json()
        event_types = [event["event_type"] for event in history["events"]]
        assert "game_created" in event_types
        assert "player_joined" in event_types
        assert "ship_placed" in event_types
        assert "shot_fired" in event_types
        assert history["events"][-1]["player"] == "player1"
        assert history["events"][-1]["result"] == "miss"

    def test_player_stats_include_completed_games(self):
        """Test player stats endpoint summarizes completed outcomes."""
        create_response = self.client.post(
            "/api/games", json={"player_name": "TestPlayer", "mode": "ai"}
        )
        game_id = create_response.json()["game_id"]

        ships = [
            ("CARRIER", 0, 0, "horizontal"),
            ("BATTLESHIP", 1, 0, "horizontal"),
            ("CRUISER", 2, 0, "horizontal"),
            ("SUBMARINE", 3, 0, "horizontal"),
            ("DESTROYER", 4, 0, "horizontal"),
        ]
        for ship_type, row, col, orientation in ships:
            self.client.post(
                f"/api/games/{game_id}/place-ship",
                json={
                    "ship_type": ship_type,
                    "row": row,
                    "col": col,
                    "orientation": orientation,
                },
            )

        game_manager.games[game_id].game.winner = game_manager.games[game_id].game.player1
        game_manager.games[game_id].game.phase = game_manager.games[game_id].game.phase.FINISHED
        game_manager.games[game_id].update_timestamp()
        game_manager.persist_game(game_id)

        response = self.client.get("/api/players/TestPlayer/stats")
        assert response.status_code == 200
        stats = response.json()
        assert stats["player_name"] == "TestPlayer"
        assert stats["games_played"] >= 1
        assert stats["wins"] >= 1

    def test_replay_endpoint_returns_turn_sequence_and_summary(self):
        """Test replay endpoint returns ordered shot events and summary metrics."""
        create_response = self.client.post(
            "/api/games", json={"player_name": "Host", "mode": "multiplayer"}
        )
        game_id = create_response.json()["game_id"]
        self.client.post(f"/api/games/{game_id}/join", json={"player_name": "Guest"})

        ships = [
            ("CARRIER", 0, 0, "horizontal"),
            ("BATTLESHIP", 1, 0, "horizontal"),
            ("CRUISER", 2, 0, "horizontal"),
            ("SUBMARINE", 3, 0, "horizontal"),
            ("DESTROYER", 4, 0, "horizontal"),
        ]

        for ship_type, row, col, orientation in ships:
            self.client.post(
                f"/api/games/{game_id}/place-ship?player=player1",
                json={
                    "ship_type": ship_type,
                    "row": row,
                    "col": col,
                    "orientation": orientation,
                },
            )
            self.client.post(
                f"/api/games/{game_id}/place-ship?player=player2",
                json={
                    "ship_type": ship_type,
                    "row": row,
                    "col": col,
                    "orientation": orientation,
                },
            )

        self.client.post(f"/api/games/{game_id}/fire?player=player1", json={"row": 0, "col": 0})
        self.client.post(f"/api/games/{game_id}/fire?player=player2", json={"row": 9, "col": 9})

        response = self.client.get(f"/api/games/{game_id}/replay")
        assert response.status_code == 200
        data = response.json()

        assert data["game_id"] == game_id
        assert data["summary"]["total_turns"] == 2
        assert data["summary"]["player1_hits"] == 1
        assert data["summary"]["player2_hits"] == 0
        assert len(data["steps"]) == 2
        assert data["steps"][0]["turn_number"] == 1
        assert data["steps"][1]["turn_number"] == 2

    def test_player_analytics_returns_hit_rate_recent_games_and_turns(self):
        """Test analytics endpoint exposes hit rate, win rate, and recent games."""
        create_response = self.client.post(
            "/api/games", json={"player_name": "Analyst", "mode": "ai"}
        )
        game_id = create_response.json()["game_id"]

        ships = [
            ("CARRIER", 0, 0, "horizontal"),
            ("BATTLESHIP", 1, 0, "horizontal"),
            ("CRUISER", 2, 0, "horizontal"),
            ("SUBMARINE", 3, 0, "horizontal"),
            ("DESTROYER", 4, 0, "horizontal"),
        ]

        for ship_type, row, col, orientation in ships:
            self.client.post(
                f"/api/games/{game_id}/place-ship",
                json={
                    "ship_type": ship_type,
                    "row": row,
                    "col": col,
                    "orientation": orientation,
                },
            )

        self.client.post(f"/api/games/{game_id}/fire", json={"row": 0, "col": 0})

        game_manager.games[game_id].game.winner = game_manager.games[game_id].game.player1
        game_manager.games[game_id].game.phase = game_manager.games[game_id].game.phase.FINISHED
        game_manager.games[game_id].update_timestamp()
        game_manager.persist_game(game_id)
        game_manager.record_event(
            game_id,
            "game_finished",
            "player1",
            {"winner": "player1"},
            game_manager.games[game_id].updated_at,
        )

        response = self.client.get("/api/players/Analyst/analytics")
        assert response.status_code == 200
        data = response.json()

        assert data["player_name"] == "Analyst"
        assert data["games_played"] >= 1
        assert data["win_rate"] >= 1
        assert data["hit_rate"] >= 0
        assert data["average_turns_per_game"] >= 1
        assert len(data["recent_games"]) >= 1

    def test_get_nonexistent_game(self):
        """Test getting a game that doesn't exist"""
        response = self.client.get("/api/games/nonexistent-id")
        assert response.status_code == 404

    def test_join_multiplayer_game_as_player2(self):
        """Test joining an existing multiplayer game"""
        create_response = self.client.post(
            "/api/games", json={"player_name": "Host", "mode": "multiplayer"}
        )
        game_id = create_response.json()["game_id"]

        response = self.client.post(f"/api/games/{game_id}/join", json={"player_name": "Guest"})

        assert response.status_code == 200
        data = response.json()
        assert data["game_id"] == game_id
        assert data["player2"]["name"] == "Guest"
        assert data["player1"]["name"] == "Host"

    def test_cannot_join_ai_game(self):
        """Test AI games cannot be joined by another player"""
        create_response = self.client.post("/api/games", json={"player_name": "Host", "mode": "ai"})
        game_id = create_response.json()["game_id"]

        response = self.client.post(f"/api/games/{game_id}/join", json={"player_name": "Guest"})

        assert response.status_code == 400

    def test_cannot_join_full_multiplayer_game(self):
        """Test a second join is rejected once player2 is assigned"""
        create_response = self.client.post(
            "/api/games", json={"player_name": "Host", "mode": "multiplayer"}
        )
        game_id = create_response.json()["game_id"]

        first_join = self.client.post(f"/api/games/{game_id}/join", json={"player_name": "Guest"})
        assert first_join.status_code == 200

        second_join = self.client.post(
            f"/api/games/{game_id}/join", json={"player_name": "LatePlayer"}
        )

        assert second_join.status_code == 400

    def test_place_ship_valid(self):
        """Test placing a ship successfully"""
        # Create game
        create_response = self.client.post(
            "/api/games", json={"player_name": "TestPlayer", "mode": "ai"}
        )
        game_id = create_response.json()["game_id"]

        # Place ship
        response = self.client.post(
            f"/api/games/{game_id}/place-ship",
            json={
                "ship_type": "CARRIER",
                "row": 0,
                "col": 0,
                "orientation": "horizontal",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Ship placed successfully"
        assert data["ship"]["type"] == "CARRIER"

    def test_place_ship_invalid_position(self):
        """Test placing ship at invalid position"""
        # Create game
        create_response = self.client.post(
            "/api/games", json={"player_name": "TestPlayer", "mode": "ai"}
        )
        game_id = create_response.json()["game_id"]

        # Try to place ship out of bounds
        response = self.client.post(
            f"/api/games/{game_id}/place-ship",
            json={
                "ship_type": "CARRIER",
                "row": 0,
                "col": 8,
                "orientation": "horizontal",
            },
        )
        assert response.status_code == 400

    def test_place_overlapping_ships(self):
        """Test that overlapping ships are rejected"""
        # Create game
        create_response = self.client.post(
            "/api/games", json={"player_name": "TestPlayer", "mode": "ai"}
        )
        game_id = create_response.json()["game_id"]

        # Place first ship
        self.client.post(
            f"/api/games/{game_id}/place-ship",
            json={
                "ship_type": "CARRIER",
                "row": 0,
                "col": 0,
                "orientation": "horizontal",
            },
        )

        # Try to place overlapping ship
        response = self.client.post(
            f"/api/games/{game_id}/place-ship",
            json={
                "ship_type": "BATTLESHIP",
                "row": 0,
                "col": 2,
                "orientation": "horizontal",
            },
        )
        assert response.status_code == 400

    def test_fire_shot_valid(self):
        """Test firing a valid shot"""
        # Create and setup game
        game_id = self._setup_complete_game()

        # Fire shot
        response = self.client.post(f"/api/games/{game_id}/fire", json={"row": 5, "col": 5})
        assert response.status_code == 200
        data = response.json()
        assert data["result"] in ["hit", "miss"]
        assert "game_over" in data

    def test_fire_shot_during_placement(self):
        """Test that firing during placement phase is rejected"""
        # Create game (still in placement phase)
        create_response = self.client.post(
            "/api/games", json={"player_name": "TestPlayer", "mode": "ai"}
        )
        game_id = create_response.json()["game_id"]

        # Try to fire shot
        response = self.client.post(f"/api/games/{game_id}/fire", json={"row": 0, "col": 0})
        assert response.status_code == 400

    def test_delete_game(self):
        """Test deleting a game"""
        # Create game
        create_response = self.client.post(
            "/api/games", json={"player_name": "TestPlayer", "mode": "ai"}
        )
        game_id = create_response.json()["game_id"]

        # Delete game
        response = self.client.delete(f"/api/games/{game_id}")
        assert response.status_code == 200

        # Verify deleted
        response = self.client.get(f"/api/games/{game_id}")
        assert response.status_code == 404

    def test_websocket_returns_initial_game_state_for_multiplayer_game(self):
        """Test websocket sends current game state immediately after connect"""
        create_response = self.client.post(
            "/api/games", json={"player_name": "Player1", "mode": "multiplayer"}
        )
        game_id = create_response.json()["game_id"]

        with self.client.websocket_connect(f"/ws/games/{game_id}?player=player1") as websocket:
            message = websocket.receive_json()

        assert message["type"] == "game_state"
        assert message["game_id"] == game_id
        assert message["mode"] == "multiplayer"
        assert message["phase"] == "placement"

    def test_websocket_broadcasts_game_state_after_ship_placement(self):
        """Test websocket broadcasts updated state after a mutating action"""
        create_response = self.client.post(
            "/api/games", json={"player_name": "Player1", "mode": "multiplayer"}
        )
        game_id = create_response.json()["game_id"]

        with self.client.websocket_connect(f"/ws/games/{game_id}?player=player1") as websocket:
            initial = websocket.receive_json()
            assert initial["type"] == "game_state"

            self.client.post(
                f"/api/games/{game_id}/place-ship?player=player1",
                json={
                    "ship_type": "CARRIER",
                    "row": 0,
                    "col": 0,
                    "orientation": "horizontal",
                },
            )

            update = websocket.receive_json()

        assert update["type"] == "game_state"
        assert update["player1"]["all_ships_placed"] is False
        assert update["player1"]["grid"][0][0] == "ship"

    def test_complete_ai_game_flow(self):
        """Test a complete AI game flow"""
        # Create game
        create_response = self.client.post(
            "/api/games", json={"player_name": "TestPlayer", "mode": "ai"}
        )
        game_id = create_response.json()["game_id"]

        # Place all 5 ships
        ships = [
            ("CARRIER", 0, 0, "horizontal"),
            ("BATTLESHIP", 1, 0, "horizontal"),
            ("CRUISER", 2, 0, "horizontal"),
            ("SUBMARINE", 3, 0, "horizontal"),
            ("DESTROYER", 4, 0, "horizontal"),
        ]

        for ship_type, row, col, orientation in ships:
            response = self.client.post(
                f"/api/games/{game_id}/place-ship",
                json={
                    "ship_type": ship_type,
                    "row": row,
                    "col": col,
                    "orientation": orientation,
                },
            )
            assert response.status_code == 200

        # Game should transition to battle phase
        get_response = self.client.get(f"/api/games/{game_id}")
        assert get_response.json()["phase"] == "battle"

        # Fire a shot
        fire_response = self.client.post(f"/api/games/{game_id}/fire", json={"row": 5, "col": 5})
        assert fire_response.status_code == 200

    def test_fire_shot_records_ai_counterattack_in_history(self):
        """Test AI responses are persisted as shot events too."""
        game_id = self._setup_complete_game()

        fire_response = self.client.post(f"/api/games/{game_id}/fire", json={"row": 5, "col": 5})
        assert fire_response.status_code == 200

        history_response = self.client.get(f"/api/games/{game_id}/history")
        assert history_response.status_code == 200

        shot_events = [
            event
            for event in history_response.json()["events"]
            if event["event_type"] == "shot_fired"
        ]
        assert len(shot_events) == 2
        assert shot_events[0]["player"] == "player1"
        assert shot_events[1]["player"] == "player2"

    def test_auto_finish_endpoint_finishes_ai_game(self):
        """Test server-side auto finish completes an AI game."""
        game_id = self._setup_complete_game()

        response = self.client.post(f"/api/games/{game_id}/auto-finish")
        assert response.status_code == 200

        data = response.json()
        assert data["game_id"] == game_id
        assert data["phase"] == "finished"
        assert data["winner"] in ["player1", "player2"]

        history_response = self.client.get(f"/api/games/{game_id}/history")
        shot_events = [
            event
            for event in history_response.json()["events"]
            if event["event_type"] == "shot_fired"
        ]
        assert len(shot_events) > 2
        assert {"player1", "player2"}.issubset({event["player"] for event in shot_events})

    def test_auto_finish_rejects_multiplayer_games(self):
        """Test auto finish is AI-only."""
        create_response = self.client.post(
            "/api/games", json={"player_name": "Host", "mode": "multiplayer"}
        )
        game_id = create_response.json()["game_id"]

        response = self.client.post(f"/api/games/{game_id}/auto-finish")
        assert response.status_code == 400

    def _setup_complete_game(self) -> str:
        """Helper to setup a complete game ready for battle"""
        # Create game
        create_response = self.client.post(
            "/api/games", json={"player_name": "TestPlayer", "mode": "ai"}
        )
        game_id = create_response.json()["game_id"]

        # Place all ships
        ships = [
            ("CARRIER", 0, 0, "horizontal"),
            ("BATTLESHIP", 1, 0, "horizontal"),
            ("CRUISER", 2, 0, "horizontal"),
            ("SUBMARINE", 3, 0, "horizontal"),
            ("DESTROYER", 4, 0, "horizontal"),
        ]

        for ship_type, row, col, orientation in ships:
            self.client.post(
                f"/api/games/{game_id}/place-ship",
                json={
                    "ship_type": ship_type,
                    "row": row,
                    "col": col,
                    "orientation": orientation,
                },
            )

        return game_id
