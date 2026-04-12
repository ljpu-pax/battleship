"""
FastAPI application for Battleship game
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.ai import AIPlayer
from src.game_manager import GameManager
from src.serializers import (
    deserialize_orientation,
    deserialize_ship_type,
    serialize_game_state,
)

app = FastAPI(
    title="Battleship API",
    description="REST API for Battleship game with AI and multiplayer support",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game manager instance
game_manager = GameManager()


# Request/Response models
class CreateGameRequest(BaseModel):
    player_name: str
    mode: str = "ai"  # "ai" or "multiplayer"


class CreateGameResponse(BaseModel):
    game_id: str
    message: str


class PlaceShipRequest(BaseModel):
    ship_type: str  # "CARRIER", "BATTLESHIP", etc.
    row: int
    col: int
    orientation: str  # "horizontal" or "vertical"


class FireShotRequest(BaseModel):
    row: int
    col: int


class FireShotResponse(BaseModel):
    result: str  # "hit", "miss"
    ship_sunk: str | None
    game_over: bool
    winner: str | None


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Battleship API is running"}


@app.post("/api/games", response_model=CreateGameResponse)
def create_game(request: CreateGameRequest):
    """Create a new game session"""
    if request.mode not in ["ai", "multiplayer"]:
        raise HTTPException(status_code=400, detail="Mode must be 'ai' or 'multiplayer'")

    game_id = game_manager.create_game(request.player_name, request.mode)

    return CreateGameResponse(game_id=game_id, message=f"Game created in {request.mode} mode")


@app.get("/api/games")
def list_games():
    """List all active games"""
    return {"games": game_manager.list_games()}


@app.get("/api/games/{game_id}")
def get_game(game_id: str, player: str = "player1"):
    """Get game state for a specific player"""
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    game_state = serialize_game_state(session.game, player)
    return {
        "game_id": game_id,
        "mode": session.mode,
        "state": game_state,
    }


@app.post("/api/games/{game_id}/place-ship")
def place_ship(game_id: str, request: PlaceShipRequest, player: str = "player1"):
    """Place a ship on the board"""
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    game = session.game
    current_player = game.player1 if player == "player1" else game.player2

    try:
        ship_type = deserialize_ship_type(request.ship_type)
        orientation = deserialize_orientation(request.orientation)

        ship = current_player.place_ship(ship_type, request.row, request.col, orientation)

        if ship is None:
            raise HTTPException(
                status_code=400, detail="Invalid ship placement (overlapping or out of bounds)"
            )

        # Check if both players are ready to start battle
        if game.both_players_ready() and game.phase.value == "placement":
            game.start_battle()

        session.update_timestamp()

        return {
            "message": "Ship placed successfully",
            "ship": {
                "type": ship.ship_type.name,
                "coordinates": ship.get_coordinates(),
            },
            "all_ships_placed": current_player.all_ships_placed(),
            "game_phase": game.phase.value,
        }

    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid ship type: {request.ship_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/games/{game_id}/fire", response_model=FireShotResponse)
def fire_shot(game_id: str, request: FireShotRequest, player: str = "player1"):
    """Fire a shot at opponent's board"""
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    game = session.game
    current_player = game.player1 if player == "player1" else game.player2

    try:
        result = game.fire_shot(current_player, request.row, request.col)

        # Handle AI turn in AI mode
        if session.mode == "ai" and game.phase.value == "battle":
            ai_player = game.player2
            if isinstance(ai_player, AIPlayer) and game.current_player == ai_player:
                # AI takes its turn
                ai_row, ai_col = ai_player.get_next_shot()
                ai_result = game.fire_shot(ai_player, ai_row, ai_col)
                # Record shot result for AI learning
                ai_player.record_shot(ai_row, ai_col, ai_result["result"])

        session.update_timestamp()

        return FireShotResponse(
            result=result["result"],
            ship_sunk=result["ship_sunk"].name if result["ship_sunk"] else None,
            game_over=game.phase.value == "finished",
            winner=(
                "player1"
                if game.winner == game.player1
                else ("player2" if game.winner == game.player2 else None)
            ),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/games/{game_id}")
def delete_game(game_id: str):
    """Delete a game session"""
    if game_manager.delete_game(game_id):
        return {"message": "Game deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Game not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
