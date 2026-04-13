# Battleship Game

Battleship built with **Test-Driven Development (TDD)** using Python, FastAPI, React, WebSockets, and SQLite.

## Project Status

### Implemented
- Rules-correct Battleship game engine
- Single-player mode against an AI opponent with targeted follow-up shots
- FastAPI backend for game lifecycle and gameplay actions
- WebSocket endpoint for real-time game state updates
- Multiplayer join flow for a second player
- SQLite-backed game persistence and recovery
- Queryable game event history and basic player statistics endpoints
- React frontend for menu, ship placement, battle, and end-game screens
- Frontend multiplayer room creation/join and local session restore
- Submission writeup and deployment config scaffolding

### Still Missing
- Replay/spike feature
- Publicly accessible deployed URL

## Validation

Current local validation:
- `73` backend tests passing
- `95%` Python coverage
- Frontend component tests pass
- Frontend production build passes
- Python tests, frontend tests, and frontend build pass locally

Latest full Python coverage snapshot:

```text
Name                  Stmts   Miss  Cover
-----------------------------------------
src/__init__.py           0      0   100%
src/ai.py                72      2    97%
src/game.py              34      1    97%
src/game_manager.py      95      8    92%
src/grid.py              21      0   100%
src/persistence.py       89      4    96%
src/player.py            51      0   100%
src/serializers.py       73      9    88%
src/ship.py              38      0   100%
-----------------------------------------
TOTAL                   473     24    95%
```

## Tech Stack

- Python 3.12
- FastAPI
- Uvicorn
- SQLAlchemy + SQLite
- WebSockets
- React 19
- Vite 8
- TypeScript 6
- pytest + pytest-cov
- black, isort, flake8, pre-commit

## Project Structure

```text
sentience/
├── api/
│   └── main.py               # FastAPI REST + WebSocket app
├── frontend/                 # React frontend
├── src/
│   ├── ai.py                 # AI opponent logic
│   ├── game.py               # Game phases, turns, win detection
│   ├── game_manager.py       # Session management + persistence hooks
│   ├── grid.py               # Grid and cell state
│   ├── persistence.py        # SQLite persistence layer
│   ├── player.py             # Player state and ship placement
│   ├── serializers.py        # API + snapshot serialization
│   └── ship.py               # Ship entities
├── tests/
│   ├── test_ai.py
│   ├── test_api.py
│   ├── test_game.py
│   ├── test_grid.py
│   ├── test_player.py
│   └── test_ship.py
├── REQUIREMENTS.md
├── ORIGINAL_REQUIREMENTS.md
├── WRITEUP.md
├── render.yaml
└── README.md
```

## API

### REST Endpoints
- `GET /` - Health check
- `POST /api/games` - Create a new AI or multiplayer game
- `GET /api/games` - List active games
- `GET /api/games/{game_id}` - Fetch game state
- `GET /api/games/{game_id}/history` - Fetch chronological game history
- `POST /api/games/{game_id}/join` - Join a multiplayer game as player 2
- `POST /api/games/{game_id}/place-ship` - Place a ship
- `POST /api/games/{game_id}/fire` - Fire at the opponent
- `DELETE /api/games/{game_id}` - Delete a game
- `GET /api/players/{player_name}/stats` - Fetch basic player statistics

### WebSocket
- `WS /ws/games/{game_id}?player=player1|player2` - Subscribe to game state updates

## Local Development

### Backend Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Backend

```bash
venv/bin/uvicorn api.main:app --reload
```

Backend docs:
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

### Frontend Setup

```bash
cd frontend
npm install
```

### Run Frontend

```bash
cd frontend
npm run dev
```

## Testing

Run all Python tests:

```bash
venv/bin/pytest tests -q
```

Run a specific test file:

```bash
venv/bin/pytest tests/test_api.py -v
```

Run frontend build verification:

```bash
cd frontend
npm run build
```

Run local quality checks:

```bash
venv/bin/pre-commit run --all-files
```

## Notes

- Game sessions are persisted to SQLite through `GameManager`.
- Multiplayer backend state can be recovered after in-memory session loss.
- `WRITEUP.md` captures the current approach, AI usage, anti-cheat notes, and scaling discussion.
- Deployment configs are scaffolded for Render (`render.yaml`) and Vercel (`frontend/vercel.json`).
- The repo is still short of final submission quality until it has a real public deployment URL and a spike feature.
