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

## Anti-Cheat Considerations

The main cheating risks are:

- revealing the opponent ship layout through API responses
- firing out of turn
- firing at the same coordinate multiple times
- tampering with browser state to gain hidden information

Current mitigations:

- opponent ship positions are hidden in serialized opponent views
- turn enforcement happens server-side
- shot validation happens server-side
- duplicate targeting is rejected server-side
- game state authority lives on the backend, not in the frontend

Still worth improving for a production submission:

- explicit session tokens/player authentication for multiplayer rooms
- rate limiting
- stronger room ownership and reconnect identity checks
- stricter production CORS and WSS deployment

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

Implemented:

- rules-correct game logic
- AI mode
- multiplayer join flow
- WebSocket state updates
- SQLite persistence and recovery
- event history endpoint
- player statistics endpoint
- frontend local restore and multiplayer room join

Still incomplete for final submission:

- public deployment URL
- polished end-to-end multiplayer UX validation in two real browsers
- replay/spike feature
- richer game history browsing UI

## Next Steps

If continuing toward a final submission, I would do this next:

1. Deploy backend and frontend publicly
2. Validate real multiplayer play across two browsers
3. Build replay UI from stored event history
4. Expand stats/history browsing
5. Tighten production security settings
