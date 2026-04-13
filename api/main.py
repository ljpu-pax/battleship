"""
FastAPI application for Battleship game
"""

from collections import defaultdict

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.ai import AIPlayer
from src.game_manager import GameManager
from src.serializers import deserialize_orientation, deserialize_ship_type, serialize_game_state

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


class WebSocketManager:
    """Track active websocket clients per game and broadcast state updates."""

    def __init__(self):
        self.connections: dict[str, list[tuple[WebSocket, str]]] = defaultdict(list)

    async def connect(self, game_id: str, websocket: WebSocket, player: str) -> None:
        await websocket.accept()
        self.connections[game_id].append((websocket, player))

    def disconnect(self, game_id: str, websocket: WebSocket) -> None:
        game_connections = self.connections.get(game_id, [])
        self.connections[game_id] = [
            (active_websocket, player)
            for active_websocket, player in game_connections
            if active_websocket != websocket
        ]
        if not self.connections[game_id]:
            self.connections.pop(game_id, None)

    async def broadcast_game_state(self, game_id: str) -> None:
        session = game_manager.get_game(game_id)
        if not session:
            return

        stale_connections: list[WebSocket] = []

        for websocket, player in self.connections.get(game_id, []):
            try:
                await websocket.send_json(
                    {
                        "type": "game_state",
                        "game_id": game_id,
                        "mode": session.mode,
                        "created_at": session.created_at.isoformat(),
                        **serialize_game_state(session.game, player),
                    }
                )
            except RuntimeError:
                stale_connections.append(websocket)

        for websocket in stale_connections:
            self.disconnect(game_id, websocket)


websocket_manager = WebSocketManager()


# Request/Response models
class CreateGameRequest(BaseModel):
    player_name: str
    mode: str = "ai"  # "ai" or "multiplayer"


class CreateGameResponse(BaseModel):
    game_id: str
    message: str


class JoinGameRequest(BaseModel):
    player_name: str


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


def _winner_key(game) -> str | None:
    if game.winner == game.player1:
        return "player1"
    if game.winner == game.player2:
        return "player2"
    return None


def _record_shot_event(
    game_id: str, acting_player: str, row: int, col: int, result: dict, session
) -> None:
    game_manager.record_event(
        game_id,
        "shot_fired",
        acting_player,
        {
            "row": row,
            "col": col,
            "result": result["result"],
            "ship_sunk": result["ship_sunk"].name if result["ship_sunk"] else None,
            "winner": _winner_key(session.game),
        },
        session.updated_at,
    )


def _build_auto_player(game_id: str, session) -> AIPlayer:
    strategist = AIPlayer("Auto Finish")
    opponent_grid = session.game.player2.grid.cells

    for row_index, row in enumerate(opponent_grid):
        for col_index, cell in enumerate(row):
            if cell.value == "miss":
                strategist._shot_positions.add((row_index, col_index))

    history = game_manager.get_history(game_id)
    for event in history:
        if event["event_type"] != "shot_fired" or event["player"] != "player1":
            continue

        strategist.record_shot(
            int(event["row"]),
            int(event["col"]),
            str(event["result"]),
        )

    return strategist


def _resolve_request_player(session, player: str | None = None, token: str | None = None) -> str:
    """Resolve the acting player, enforcing token-based identity in multiplayer."""
    if session.mode == "multiplayer":
        resolved_player = game_manager.resolve_player_from_token(session, token)
        if resolved_player is None:
            raise HTTPException(status_code=403, detail="Valid multiplayer token required")
        return resolved_player

    return player or "player1"


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Battleship API is running"}


@app.post("/api/games")
def create_game(request: CreateGameRequest):
    """Create a new game session"""
    if request.mode not in ["ai", "multiplayer"]:
        raise HTTPException(status_code=400, detail="Mode must be 'ai' or 'multiplayer'")

    game_id = game_manager.create_game(request.player_name, request.mode)

    # Return full game state
    session = game_manager.get_game(game_id)
    game_state = serialize_game_state(session.game, "player1")

    return {
        "game_id": game_id,
        "mode": session.mode,
        "created_at": session.created_at.isoformat(),
        "player_token": session.player_tokens.get("player1"),
        **game_state,
    }


@app.get("/api/games")
def list_games():
    """List all active games"""
    return {"games": game_manager.list_games()}


@app.get("/api/games/{game_id}")
def get_game(game_id: str, player: str | None = None, token: str | None = None):
    """Get game state for a specific player"""
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    resolved_player = _resolve_request_player(session, player, token)
    game_state = serialize_game_state(session.game, resolved_player)
    return {
        "game_id": game_id,
        "mode": session.mode,
        "created_at": session.created_at.isoformat(),
        **game_state,
    }


@app.get("/api/games/{game_id}/history")
def get_game_history(game_id: str):
    """Get chronological event history for a game."""
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    return {"game_id": game_id, "events": game_manager.get_history(game_id)}


@app.get("/api/games/{game_id}/replay")
def get_game_replay(game_id: str):
    """Get replay steps and summary for a game."""
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    return game_manager.get_replay(game_id)


@app.get("/api/players/{player_name}/stats")
def get_player_stats(player_name: str):
    """Get aggregate player statistics from persisted games."""
    return game_manager.get_player_stats(player_name)


@app.get("/api/players/{player_name}/analytics")
def get_player_analytics(player_name: str):
    """Get richer analytics for a player."""
    return game_manager.get_player_analytics(player_name)


@app.post("/api/games/{game_id}/join")
async def join_game(game_id: str, request: JoinGameRequest):
    """Join an existing multiplayer game as player 2."""
    try:
        session = game_manager.join_game(game_id, request.player_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    await websocket_manager.broadcast_game_state(game_id)

    return {
        "game_id": game_id,
        "mode": session.mode,
        "created_at": session.created_at.isoformat(),
        "player_token": session.player_tokens.get("player2"),
        **serialize_game_state(session.game, "player2"),
    }


@app.post("/api/games/{game_id}/place-ship")
async def place_ship(
    game_id: str,
    request: PlaceShipRequest,
    player: str | None = None,
    token: str | None = None,
):
    """Place a ship on the board"""
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    game = session.game
    resolved_player = _resolve_request_player(session, player, token)
    current_player = game.player1 if resolved_player == "player1" else game.player2

    try:
        ship_type = deserialize_ship_type(request.ship_type)
        orientation = deserialize_orientation(request.orientation)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid ship type: {request.ship_type}")

    ship = current_player.place_ship(ship_type, request.row, request.col, orientation)

    if ship is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid ship placement (overlapping or out of bounds)",
        )

    # Check if both players are ready to start battle
    if game.both_players_ready() and game.phase.value == "placement":
        game.start_battle()

    session.update_timestamp()
    game_manager.persist_game(game_id)
    game_manager.record_event(
        game_id,
        "ship_placed",
        resolved_player,
        {
            "ship_type": ship.ship_type.name,
            "row": request.row,
            "col": request.col,
            "orientation": request.orientation,
        },
        session.updated_at,
    )

    await websocket_manager.broadcast_game_state(game_id)

    return {
        "message": "Ship placed successfully",
        "ship": {
            "type": ship.ship_type.name,
            "coordinates": ship.get_coordinates(),
        },
        "all_ships_placed": current_player.all_ships_placed(),
        "game_phase": game.phase.value,
    }


@app.post("/api/games/{game_id}/fire", response_model=FireShotResponse)
async def fire_shot(
    game_id: str,
    request: FireShotRequest,
    player: str | None = None,
    token: str | None = None,
):
    """Fire a shot at opponent's board"""
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    game = session.game
    resolved_player = _resolve_request_player(session, player, token)
    current_player = game.player1 if resolved_player == "player1" else game.player2

    try:
        result = game.fire_shot(current_player, request.row, request.col)
        session.update_timestamp()
        _record_shot_event(game_id, resolved_player, request.row, request.col, result, session)

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
                _record_shot_event(game_id, "player2", ai_row, ai_col, ai_result, session)

        game_manager.persist_game(game_id)
        await websocket_manager.broadcast_game_state(game_id)

        return FireShotResponse(
            result=result["result"],
            ship_sunk=result["ship_sunk"].name if result["ship_sunk"] else None,
            game_over=game.phase.value == "finished",
            winner=_winner_key(game),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/games/{game_id}/auto-finish")
async def auto_finish_ai_game(game_id: str, player: str | None = None, token: str | None = None):
    """Finish an AI game on the server using targeted move selection."""
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    if session.mode != "ai":
        raise HTTPException(status_code=400, detail="Auto finish is only available in AI mode")

    resolved_player = _resolve_request_player(session, player, token)

    if resolved_player != "player1":
        raise HTTPException(status_code=400, detail="Auto finish is only supported for player1")

    game = session.game
    if game.phase.value != "battle":
        raise HTTPException(status_code=400, detail="Game must be in battle phase")

    strategist = _build_auto_player(game_id, session)

    while game.phase.value == "battle":
        if game.current_player == game.player1:
            row, col = strategist.get_next_shot()
            result = game.fire_shot(game.player1, row, col)
            strategist.record_shot(row, col, result["result"])
            session.update_timestamp()
            _record_shot_event(game_id, "player1", row, col, result, session)
        else:
            ai_player = game.player2
            if not isinstance(ai_player, AIPlayer):
                raise HTTPException(status_code=500, detail="AI player unavailable")

            row, col = ai_player.get_next_shot()
            result = game.fire_shot(ai_player, row, col)
            ai_player.record_shot(row, col, result["result"])
            session.update_timestamp()
            _record_shot_event(game_id, "player2", row, col, result, session)

    game_manager.persist_game(game_id)
    await websocket_manager.broadcast_game_state(game_id)

    return {
        "game_id": game_id,
        "mode": session.mode,
        "created_at": session.created_at.isoformat(),
        **serialize_game_state(game, resolved_player),
    }


@app.delete("/api/games/{game_id}")
def delete_game(game_id: str):
    """Delete a game session"""
    if game_manager.delete_game(game_id):
        return {"message": "Game deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Game not found")


@app.websocket("/ws/games/{game_id}")
async def game_websocket(
    websocket: WebSocket,
    game_id: str,
    player: str | None = None,
    token: str | None = None,
):
    """WebSocket endpoint for real-time game state updates."""
    session = game_manager.get_game(game_id)
    if not session:
        await websocket.close(code=1008, reason="Game not found")
        return

    try:
        resolved_player = _resolve_request_player(session, player, token)
    except HTTPException:
        await websocket.close(code=1008, reason="Valid multiplayer token required")
        return

    await websocket_manager.connect(game_id, websocket, resolved_player)

    try:
        await websocket.send_json(
            {
                "type": "game_state",
                "game_id": game_id,
                "mode": session.mode,
                "created_at": session.created_at.isoformat(),
                **serialize_game_state(session.game, resolved_player),
            }
        )

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(game_id, websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
