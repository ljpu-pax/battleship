# Battleship Game - TDD Implementation

A complete Battleship game implementation built using **Test-Driven Development (TDD)** with Python, pytest, FastAPI, and React.

## 🎯 Project Status

### ✅ Core Game Logic (Complete - TDD)
- **51 tests passing**
- **98% code coverage**
- All core game mechanics implemented with test-first approach

### 🚧 Remaining Work
- FastAPI backend with WebSocket support
- React frontend
- Multiplayer rooms
- Persistence layer
- Deployment

## 📊 Test Coverage Summary

```
Name              Stmts   Miss  Cover
-------------------------------------
src/__init__.py       0      0   100%
src/ai.py            72      2    97%
src/game.py          34      1    97%
src/grid.py          21      0   100%
src/player.py        51      1    98%
src/ship.py          38      0   100%
-------------------------------------
TOTAL               216      4    98%
```

## 🧪 TDD Approach

### Test-First Development Process

1. **Write Test First** → 2. **Watch It Fail** → 3. **Write Minimal Code** → 4. **Pass Test** → 5. **Refactor** → Repeat

### Implementation Order

#### 1. Grid Class (`src/grid.py`)
**Tests:** `tests/test_grid.py` - 8 tests
- ✅ Grid initialization (10x10)
- ✅ Cell state management (empty, ship, hit, miss)
- ✅ Coordinate validation
- ✅ Error handling for invalid coordinates
- **Coverage:** 100%

#### 2. Ship Class (`src/ship.py`)
**Tests:** `tests/test_ship.py` - 10 tests
- ✅ Ship types with correct lengths (Carrier-5, Battleship-4, Cruiser-3, Submarine-3, Destroyer-2)
- ✅ Horizontal and vertical orientations
- ✅ Coordinate calculation
- ✅ Hit detection and tracking
- ✅ Sinking logic (all positions hit)
- ✅ Prevent duplicate hits on same position
- **Coverage:** 100%

#### 3. Player Class (`src/player.py`)
**Tests:** `tests/test_player.py` - 15 tests
- ✅ Ship placement validation
  - Out of bounds detection
  - Overlap prevention
  - Adjacent ships allowed
- ✅ Shot receiving mechanics
  - Hit/miss/sunk feedback
  - Grid state updates
  - Prevent shooting same position twice
- ✅ Win condition (all ships sunk)
- **Coverage:** 98%

#### 4. Game Class (`src/game.py`)
**Tests:** `tests/test_game.py` - 9 tests
- ✅ Game phases (Placement → Battle → Finished)
- ✅ Turn management
- ✅ Shot validation (correct turn, correct phase)
- ✅ Win detection
- ✅ Opponent tracking
- **Coverage:** 97%

#### 5. AI Player (`src/ai.py`)
**Tests:** `tests/test_ai.py` - 9 tests
- ✅ Random ship placement (valid, no overlaps, within bounds)
- ✅ Intelligent targeting algorithm:
  - Random shots initially
  - Adjacent cell targeting after hit
  - Directional continuation after consecutive hits
  - Target clearing after ship sunk
- ✅ No duplicate shots
- **Coverage:** 97%

## 🏗️ Architecture

### Core Classes

```
Grid
├── 10x10 cell matrix
├── Cell states: EMPTY, SHIP, HIT, MISS
└── Coordinate validation

Ship
├── Ship types (enum with lengths)
├── Orientation (horizontal/vertical)
├── Hit tracking
└── Sunk detection

Player
├── Grid instance
├── Ships list (max 5)
├── Ship placement logic
├── Shot receiving
└── Shot history tracking

AIPlayer (extends Player)
├── Random ship placement
├── Intelligent targeting
│   ├── Hunt mode (random)
│   ├── Target mode (after hit)
│   └── Directional continuation
└── Shot history

Game
├── Two players (Player1, Player2)
├── Phase management
├── Turn management
├── Win condition checking
└── Game flow orchestration
```

## 🚀 Running Tests

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_grid.py -v
pytest tests/test_ship.py -v
pytest tests/test_player.py -v
pytest tests/test_game.py -v
pytest tests/test_ai.py -v
```

### Run with Coverage Report
```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html to view detailed coverage
```

## 💡 Key TDD Benefits Demonstrated

### 1. **Confidence in Refactoring**
- Can safely refactor knowing tests will catch regressions
- Example: AI targeting algorithm was refined multiple times

### 2. **Clear Requirements**
- Tests serve as executable specifications
- Each test name describes expected behavior

### 3. **Minimal Code**
- Only wrote code needed to pass tests
- No speculative features

### 4. **Bug Prevention**
- Edge cases caught early (e.g., duplicate shots, out of bounds)
- Error handling tested explicitly

### 5. **Documentation**
- Tests document how to use each class
- Examples of valid/invalid inputs

## 🎮 Game Rules (As Tested)

### Ship Placement Phase
- 5 ships per player: Carrier(5), Battleship(4), Cruiser(3), Submarine(3), Destroyer(2)
- Ships placed horizontally or vertically
- No overlapping
- Must be within 10x10 grid bounds

### Battle Phase
- Players alternate turns
- Select coordinates to fire
- Feedback: "hit", "miss", or "sunk" (with ship type)
- Cannot fire at same position twice

### Win Condition
- First player to sink all opponent ships wins

### AI Behavior
- **Hunt Mode:** Random shots across the grid
- **Target Mode:** After a hit, targets adjacent cells (up, down, left, right)
- **Directional Mode:** After consecutive hits, continues in that direction
- **Reset:** Returns to hunt mode after sinking a ship

## 🔧 Technologies Used

- **Language:** Python 3.12
- **Testing:** pytest 7.4.3
- **Coverage:** pytest-cov 4.1.0
- **Backend (planned):** FastAPI 0.109.0
- **WebSocket (planned):** websockets 12.0
- **Database (planned):** SQLAlchemy 2.0.25 + aiosqlite

## 📁 Project Structure

```
sentience/
├── src/
│   ├── __init__.py
│   ├── grid.py          # 100% coverage
│   ├── ship.py          # 100% coverage
│   ├── player.py        # 98% coverage
│   ├── game.py          # 97% coverage
│   └── ai.py            # 97% coverage
├── tests/
│   ├── __init__.py
│   ├── test_grid.py     # 8 tests
│   ├── test_ship.py     # 10 tests
│   ├── test_player.py   # 15 tests
│   ├── test_game.py     # 9 tests
│   └── test_ai.py       # 9 tests
├── requirements.txt
├── pytest.ini
├── .gitignore
├── REQUIREMENTS.md      # Full project requirements
└── README.md            # This file
```

## 🎯 Next Steps

1. **Backend API** - FastAPI with WebSocket support
2. **Frontend** - React with ship placement UI
3. **Multiplayer** - Room-based game sessions
4. **Persistence** - SQLite/PostgreSQL for game history
5. **Deployment** - Deploy to Render/Railway/Vercel
6. **Spike Feature** - Choose unique feature to showcase

## 📝 Example Test Output

```bash
$ pytest -v

tests/test_ai.py::TestAIPlayer::test_ai_can_place_ships_randomly PASSED
tests/test_ai.py::TestAIPlayer::test_ai_targets_adjacent_after_hit PASSED
tests/test_game.py::TestGame::test_game_ends_when_all_ships_sunk PASSED
tests/test_grid.py::TestGrid::test_grid_initialization PASSED
tests/test_player.py::TestPlayer::test_cannot_place_overlapping_ships PASSED
tests/test_ship.py::TestShip::test_ship_sinks_when_all_positions_hit PASSED

============================== 51 passed in 0.11s ===============================
```

## 🤖 AI Usage

This project was built with heavy assistance from **Claude Code** (Anthropic's CLI tool) using TDD methodology:

1. **Test Writing:** Claude helped design comprehensive test cases
2. **Implementation:** Minimal code written to pass tests
3. **Refactoring:** Iterative improvements while maintaining green tests
4. **Coverage:** Ensured high code coverage (98%)

## 📜 License

This is a work trial project for Sentience.

---

**Built with ❤️ using Test-Driven Development**
