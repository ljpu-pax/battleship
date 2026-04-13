# Battleship Game

A fully-featured Battleship game built with **Test-Driven Development (TDD)** using Python, FastAPI, React, WebSockets, and SQLite.

🎮 **[Play Live Game](https://battleship-eta-gules.vercel.app/)** | 📚 **[API Docs](https://battleship-x18k.onrender.com/docs)**

## Documentation

- **[Product Requirements](docs/product-requirements.md)** - Complete feature specifications and game rules
- **[Development Writeup](docs/development-writeup.md)** - Development approach, AI usage, and technical decisions
- **[Work Trial Brief](docs/work-trial-brief.md)** - Original project assignment

## Project Status

### ✅ Fully Implemented
- Core game rules and mechanics (10×10 grid, 5 ships, turn-based)
- Single-player mode with intelligent AI opponent
- Multiplayer mode with real-time WebSocket updates
- Game ID sharing and player readiness indicators
- Secure multiplayer sessions with player tokens
- SQLite-backed persistence and session recovery
- Event history and player analytics
- **Spike feature:** Interactive replay timeline + analytics dashboard
- **Deployed live:** [Frontend (Vercel)](https://battleship-eta-gules.vercel.app/) + [Backend (Render)](https://battleship-x18k.onrender.com/docs)

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
├── docs/
│   ├── product-requirements.md
│   ├── development-writeup.md
│   └── work-trial-brief.md
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
- `GET /api/games/{game_id}/replay` - Fetch replay steps and summary
- `POST /api/games/{game_id}/join` - Join a multiplayer game as player 2
- `POST /api/games/{game_id}/place-ship` - Place a ship
- `POST /api/games/{game_id}/fire` - Fire at the opponent
- `DELETE /api/games/{game_id}` - Delete a game
- `GET /api/players/{player_name}/stats` - Fetch basic player statistics
- `GET /api/players/{player_name}/analytics` - Fetch hit rate, win rate, recent games, and turn metrics

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
- [Development writeup](docs/development-writeup.md) captures the development approach, AI usage, anti-cheat notes, and scaling discussion.
- Deployment configs are scaffolded for Render (`render.yaml`) and Vercel (`frontend/vercel.json`).
- Replay and analytics are implemented as the current spike.
