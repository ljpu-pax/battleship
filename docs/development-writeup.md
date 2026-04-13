# Battleship Work Trial Writeup

## Overview

This project was built as a Battleship implementation with a Python/FastAPI backend and a React frontend. I approached it as a TDD-first codebase: establish a failing test for each behavior slice, implement the smallest working change, then refactor while keeping the suite green.

## Development Approach

The work was split into vertical slices instead of broad subsystems:

1. Core game rules and AI behavior
2. REST API for game lifecycle and gameplay
3. WebSocket foundation for real-time multiplayer updates
4. SQLite persistence for game recovery
5. Multiplayer room join flow and frontend session wiring
6. Event history and player statistics endpoints
7. Replay timeline and analytics spike

This kept the codebase moving toward a playable product while preserving fast feedback through tests.

## AI Usage

AI tooling was used heavily throughout the project.

- AI was used to help design test cases from requirements.
- AI accelerated implementation of small, well-scoped backend and frontend slices.
- AI was used to compare current repo state against the original work-trial requirements and identify missing deliverables.
- Every generated change was validated locally with tests, frontend builds, and pre-commit checks before commit.

The important part was not just generating code, but repeatedly tightening the scope of each task so the generated code matched the repo's actual design and passed local verification.

## Technical Decisions

### Backend

- **FastAPI** was used for the REST API and WebSocket endpoint.
- **In-memory session state** remains the live runtime state for active games.
- **SQLite + SQLAlchemy** was added as the persistence layer for:
  - recovering game sessions after in-memory loss
  - storing event history
  - computing basic player statistics

### Frontend

- **React + Vite + TypeScript** was used for the browser client.
- The frontend now supports:
  - AI mode creation
  - multiplayer room creation
  - multiplayer join by game ID
  - local session restore through `localStorage`
  - WebSocket-driven state refresh

### Persistence Strategy

I chose SQLite for speed of implementation and local development simplicity. It is sufficient for a work-trial submission and easy to inspect. The current schema stores:

- game snapshots
- event history per game

This supports recovery, history inspection, and a straightforward path to replay.

## Spike Feature

The chosen spike combines:

- **Replay system**
- **Basic analytics**

### Replay

The backend exposes replay data derived from chronological shot events. The frontend surfaces this on the completed-game screen as a replay timeline showing turn order, coordinates, shot result, and sink events.

### Basic Analytics

The backend also aggregates lightweight player analytics and recent game summaries. The frontend surfaces:

- hit rate
- win rate
- average turns per game
- recent game summaries

This spike was chosen because it builds directly on the persistence and event-history foundation, demonstrates product thinking, and is straightforward to demo in a live review.

## Anti-Cheat Considerations

The main cheating risks are:

- revealing the opponent ship layout through API responses
- firing out of turn
- firing at the same coordinate multiple times
- tampering with browser state to gain hidden information
- impersonating another player in multiplayer

### ✅ Implemented Mitigations:

- **Server-side authority**: Game state lives on backend, not frontend
- **Hidden opponent state**: Ship positions never sent to opponent until game ends
- **Turn enforcement**: Server validates whose turn it is
- **Shot validation**: Server validates coordinates and prevents duplicates
- **Player token authentication**: Multiplayer sessions use secure tokens
  - Each player receives a unique token on game creation/join
  - Token required for all multiplayer API calls
  - Token validation prevents player impersonation

### 🚧 Future Security Improvements:

- Rate limiting on API endpoints
- Stricter CORS configuration in production
- WSS (secure WebSocket) enforcement
- Session expiration and timeout handling
- Audit logging for suspicious behavior

## Complexity and Scaling

For the current 10x10 game:

- grid storage is `O(n^2)`
- ship placement validation is `O(k)` over the ship length
- hit detection is effectively bounded and small for this board size
- move history grows linearly with the number of actions

If the board scaled much larger:

- full-grid serialization would become expensive
- sparse board representations would become more attractive
- delta-based state updates would be preferable to full snapshots
- event history would need indexing and pagination
- replay should stream moves rather than rely on repeated full-state fetches

## Current Status

### ✅ Implemented Features

**Core Gameplay:**
- Rules-correct game logic (10×10 grid, 5 ships, win detection)
- AI mode with intelligent targeting (hunt/target strategy)
- Multiplayer join flow with game ID sharing
- WebSocket real-time state updates
- Auto-finish feature for AI games

**Persistence & Recovery:**
- SQLite-backed game persistence
- Session recovery after page refresh
- Event history tracking
- Player statistics aggregation

**Frontend UX:**
- Ship placement with visual validation
- Dual-grid battle interface
- Local session restore via localStorage
- Multiplayer room creation/join flow
- **Game ID display with copy button**
- **Player readiness indicators** (shows both players' ship placement progress)
- **Secure multiplayer sessions** with player tokens

**Spike Feature:**
- Interactive replay timeline with time-travel
- Adjustable playback speed (0.5x to 4x)
- Player analytics dashboard (hit rate, win rate, recent games)
- Shot distribution heatmaps

**Testing & Quality:**
- 73 backend tests with 95% coverage
- Frontend component tests
- Pre-commit hooks (black, isort, flake8)
- CI/CD with GitHub Actions

### 🌐 Production Deployment

**Live URLs:**
- **Frontend:** https://battleship-eta-gules.vercel.app/
- **Backend API:** https://battleship-x18k.onrender.com/docs

**Deployment Stack:**
- Frontend: Vercel (automatic deployments from GitHub)
- Backend: Render (Docker container)
- Database: SQLite (persistent volume on Render)
- WebSockets: WSS for secure real-time communication

### 🚧 Future Enhancements (Time Permitting)

- [ ] Mobile-responsive design improvements
- [ ] Enhanced error handling and user feedback
- [ ] Performance monitoring and logging
- [ ] Spectator mode for watching live games
- [ ] Tournament bracket system
- [ ] Advanced AI with ML-based strategies
- [ ] Game history browsing UI
- [ ] Rate limiting and stricter CORS

## Next Steps

**Potential improvements:**
1. End-to-end multiplayer testing across different networks
2. Mobile UI/UX optimization
3. Performance monitoring and analytics
4. Advanced security features (rate limiting, session expiration)
