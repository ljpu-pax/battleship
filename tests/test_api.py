"""
Tests for FastAPI endpoints - TDD approach
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app, game_manager


class TestAPI:
    """Test suite for API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client and clear games before each test"""
        self.client = TestClient(app)
        game_manager.games.clear()
        yield
        game_manager.games.clear()

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
        assert data["message"] == "Game created in ai mode"

    def test_create_game_multiplayer_mode(self):
        """Test creating a game in multiplayer mode"""
        response = self.client.post(
            "/api/games", json={"player_name": "Player1", "mode": "multiplayer"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert data["message"] == "Game created in multiplayer mode"

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
        assert "state" in data

    def test_get_nonexistent_game(self):
        """Test getting a game that doesn't exist"""
        response = self.client.get("/api/games/nonexistent-id")
        assert response.status_code == 404

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
        assert get_response.json()["state"]["phase"] == "battle"

        # Fire a shot
        fire_response = self.client.post(f"/api/games/{game_id}/fire", json={"row": 5, "col": 5})
        assert fire_response.status_code == 200

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
