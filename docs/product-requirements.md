# Battleship Game - Requirements Document

## Project Overview

Build a fully functional, web-based Battleship game with both single-player (vs AI) and multiplayer (vs Human) modes. The application must be deployed publicly and demonstrate technical sophistication in game logic, state management, and real-time communication.

## Implementation Status

### ✅ Completed Features
- Core game rules and mechanics (10×10 grid, 5 ships, turn-based gameplay)
- Ship placement UI with validation and visual feedback
- Battle phase with dual-grid display
- Single-player mode with intelligent AI opponent
- Multiplayer mode with real-time WebSocket updates
- Game state persistence (SQLite + session recovery)
- Game history and replay system
- Player analytics dashboard
- Anti-cheat measures (server-side validation, hidden opponent state)
- Game ID sharing and player readiness indicators
- Secure multiplayer sessions with player tokens

### 🌐 Live Deployment
- **Frontend:** https://battleship-eta-gules.vercel.app/
- **Backend API:** https://battleship-x18k.onrender.com/docs

### 🚧 Future Enhancements (Time Permitting)
- Mobile-responsive design improvements
- Spectator mode for watching live games
- Tournament bracket system
- Advanced AI with machine learning
- Performance monitoring and analytics

---

## 1. Core Game Rules

### 1.1 Game Setup
- **Grid Size**: 10×10 grid for each player
- **Ships**: 5 ships with specific lengths:
  - Carrier: 5 cells
  - Battleship: 4 cells
  - Cruiser: 3 cells
  - Submarine: 3 cells
  - Destroyer: 2 cells

### 1.2 Ship Placement Phase
- Ships can be placed horizontally or vertically
- Ships cannot overlap
- Ships must fit entirely within grid boundaries
- Each player's ship positions are hidden from opponent

### 1.3 Firing Phase
- Players alternate turns
- Each turn: select a coordinate to fire at
- Feedback provided: "hit", "miss", or "sunk" (with ship name)
- Hit/miss history visible to both players

### 1.4 Win Condition
- First player to sink all 5 opponent ships wins
- Game announces winner and offers rematch/menu options

---

## 2. Functional Requirements

### 2.1 Ship Placement UI
**Must Have:**
- Interactive grid for placing ships
- Rotate ship orientation (horizontal/vertical)
- Visual validation of valid/invalid positions
- Clear indication of placed ships
- Confirmation button to lock in placements
- Ability to reset/reposition ships before confirming

**Acceptance Criteria:**
- Ships cannot be placed off-grid
- Ships cannot overlap
- All 5 ships must be placed before proceeding
- Clear visual feedback for placement errors

### 2.2 Firing Phase UI
**Must Have:**
- Two grid display:
  1. **Your Fleet Grid**: Shows your ships and incoming opponent hits/misses
  2. **Targeting Grid**: Shows your shots (hits/misses) on opponent's grid
- Turn indicator showing whose turn it is
- Click-to-fire interaction on targeting grid
- Immediate visual feedback for each shot result
- Shot history/log visible to player

**Acceptance Criteria:**
- Cannot fire at same coordinate twice
- Clear visual distinction between hits and misses
- Sunk ships announced with ship name
- Cannot fire during opponent's turn (multiplayer)

### 2.3 Game Flow
**Must Have:**
1. Main menu/landing page
2. Game mode selection (vs AI / vs Human)
3. Ship placement phase
4. Battle phase
5. End game screen with winner announcement
6. Options: Rematch or Return to Menu

---

## 3. Game Modes

### 3.1 Single Player (vs AI)
**Requirements:**
- AI ships placed randomly but validly
- AI shot logic must be intelligent, not purely random
- **Minimum AI Intelligence:**
  - After hitting a ship, probe adjacent cells (up, down, left, right)
  - Continue along hit direction until ship sunk
  - Return to random targeting after sinking ship

**Acceptance Criteria:**
- AI makes strategic decisions after scoring hits
- AI doesn't fire at previously targeted cells
- Game feels challenging but fair

### 3.2 Multiplayer (vs Human)
**Requirements:**
- Two players in separate browser sessions
- Real-time updates without manual refresh
- Both players see game state changes immediately
- Turn-based gameplay enforced server-side
- Players cannot see opponent's ship positions

**Technical Considerations:**
- WebSocket or Server-Sent Events for real-time communication
- Room/lobby system for player matching
- Handle disconnections gracefully
- Prevent simultaneous shots from both players

**Acceptance Criteria:**
- Players can join game via shareable link or room code
- Updates appear instantly in both browsers
- Turn enforcement prevents out-of-turn actions
- Disconnected player scenario handled appropriately

---

## 4. Persistence Requirements

### 4.1 Game State Persistence
**Must Have:**
- Game state survives page refresh mid-game
- Minimum for multiplayer; recommended for single-player
- Restore exact game state:
  - Ship placements
  - All shots taken
  - Current turn
  - Hit/miss history

**Implementation Options:**
- Browser localStorage (single-player)
- Database (multiplayer - required)
- Session storage with server sync

### 4.2 Game History
**Must Have:**
- Store completed games permanently
- Queryable data structure

**Data to Store:**
- Game ID
- Players (user IDs or identifiers)
- Complete move history (chronological)
- Game outcome (winner)
- Timestamps (start, end, each move)
- Game mode (AI vs Human)

**Query Capabilities:**
- Retrieve game by ID
- List games by player
- Filter by date range
- Replay game from history

**Storage Options:**
- SQL database (PostgreSQL, MySQL)
- NoSQL database (MongoDB, DynamoDB)
- Document justification in writeup

---

## 5. Deployment Requirements

### 5.1 Hosting
**Must Have:**
- Publicly accessible URL
- No authentication required to access/play
- Stable, production-ready deployment

**Recommended Platforms:**
- Frontend: Vercel, Netlify, AWS S3 + CloudFront
- Backend: Heroku, Railway, Render, AWS EC2/ECS
- Full-stack: Vercel, Netlify (with serverless functions)

### 5.2 Performance
- Page load time < 3 seconds
- Real-time updates < 500ms latency (multiplayer)
- Responsive design (mobile-friendly recommended)

---

## 6. Security & Anti-Cheat

### 6.1 Cheating Vectors to Address
**Client-Side Cheating:**
- Inspecting network traffic to see opponent ship positions
- Modifying client-side code to reveal opponent grid
- Manipulating game state in browser DevTools

**Server-Side Cheating:**
- Firing multiple shots in one turn
- Targeting coordinates outside grid
- Re-firing at same coordinate
- Acting out of turn (multiplayer)

### 6.2 Anti-Cheat Measures
**Must Implement:**
- **Server-Side Validation**: All game logic validated server-side
- **Hidden State**: Opponent ship positions never sent to client until game ends
- **Turn Enforcement**: Server controls whose turn it is
- **Input Validation**: Validate all coordinates, moves server-side
- **Rate Limiting**: Prevent rapid-fire API abuse

**Recommended:**
- Session tokens/authentication for multiplayer
- Encrypted WebSocket connections (WSS)
- Audit logs of all actions
- Timeout mechanisms for inactive players

---

## 7. Scalability Considerations

### 7.1 Runtime Complexity Analysis
**Current Scale (10×10 grid):**
- Grid size: O(n²) where n=10
- Ship placement validation: O(n)
- Hit detection: O(1) with proper data structures
- Win condition check: O(1) with counter-based approach

### 7.2 Scaling to Large Boards
**If board scaled to 100×100 or 1000×1000:**

**Challenges:**
- Memory: O(n²) grid storage per game
- Network: Sending full grid state expensive
- Database: Storing full move history grows linearly with moves

**Optimization Strategies:**
- Sparse grid representation (store only ship/hit positions)
- Delta updates instead of full state sync
- Spatial indexing for ship collision detection
- Database indexing on game_id, player_id, timestamp
- Pagination for move history
- Caching frequently accessed game states

**Document in Writeup:**
- Current implementation complexity
- Data structure choices
- How architecture would adapt to 100× larger boards

---

## 8. Technical Stack (Recommended)

### 8.1 Frontend
- **Framework**: React, Vue, Svelte, or vanilla JS
- **Styling**: CSS, Tailwind, styled-components
- **State Management**: React Context, Zustand, Redux (if complex)

### 8.2 Backend
- **Runtime**: Node.js, Python (FastAPI), Go
- **Real-time**: WebSockets (Socket.io, ws), Server-Sent Events
- **API**: REST or GraphQL for game actions
- **Database**: PostgreSQL, MongoDB, Firebase

### 8.3 DevOps
- **Version Control**: Git + GitHub
- **CI/CD**: GitHub Actions (optional but recommended)
- **Monitoring**: Basic logging/error tracking

---

## 9. Deliverables Checklist

### 9.1 Code Repository (GitHub)
- [x] Clean, organized code structure
- [x] README with setup instructions
- [x] Development writeup documenting:
  - [x] Approach to problem-solving
  - [x] How AI tools (Claude Code) were used
  - [x] Technology choices and rationale
  - [x] Anti-cheat implementation
  - [x] Scalability analysis
  - [x] Known limitations/future improvements
- [x] Game history query examples/documentation
- [x] Environment setup documentation

### 9.2 Deployed Application
- [x] Live URL provided in submission
  - Frontend: https://battleship-eta-gules.vercel.app/
  - Backend: https://battleship-x18k.onrender.com/docs
- [x] Fully functional on modern browsers
- [x] Both game modes working
- [x] Persistence working (test with refresh)
- [x] No critical bugs

### 9.3 Spike Feature ✅
**Implemented: Replay Timeline + Player Analytics Dashboard**

Our spike feature includes:
- **Interactive replay system** with time-travel debugging
  - Step-by-step game replay with timeline scrubbing
  - Visual state reconstruction at any point
  - Adjustable playback speed (0.5x, 1x, 2x, 4x)
  - Windowed timeline view for long games
- **Player analytics dashboard**
  - Win/loss statistics
  - Accuracy metrics (hit rate)
  - Average game duration
  - Recent game history
  - Shot distribution heatmaps

**Spike demonstrates:**
- Advanced data visualization
- Complex state management
- Event sourcing architecture
- Performance optimization for large datasets
- Well-documented and polished implementation

---

## 10. Evaluation Criteria

### 10.1 Feature Completeness (40%)
- All core gameplay mechanics working
- Both game modes functional
- Persistence implemented
- Deployed and accessible

### 10.2 Code Quality (20%)
- Clean, readable code
- Proper separation of concerns
- Good architecture decisions
- Appropriate use of tools/frameworks

### 10.3 Anti-Cheat & Security (15%)
- Thoughtful approach to preventing cheating
- Server-side validation
- Secure implementation

### 10.4 Scalability Design (10%)
- Runtime complexity analysis
- Smart data structure choices
- Scalability considerations documented

### 10.5 Spike Feature (15%)
- Creativity and innovation
- Polish and execution quality
- Demonstrates unique skills/passion

---

## 11. Submission Guidelines

**Email Reply Must Include:**
1. **Live URL**: https://your-deployed-app.com
2. **GitHub Repository**: https://github.com/yourname/battleship
3. **WRITEUP.md**: Included in repo, covering:
   - Problem approach
   - AI tool usage (Claude Code, Cursor, etc.)
   - Technical decisions
   - Anti-cheat strategy
   - Scalability considerations
   - Spike feature explanation

**Timeline:**
- Plan for live review and Q&A session
- Be prepared to discuss code and decisions
- Have demo ready to showcase spike feature

---

## 12. Success Tips

1. **Start with Core Loop**: Get basic gameplay working first
2. **Test Early**: Deploy early, test on real URLs
3. **Document as You Go**: Write down decisions and rationale
4. **AI Usage**: Lean heavily on AI tools but understand the code
5. **Spike Planning**: Start thinking about spike early
6. **Time Management**: Don't let perfect be enemy of good
7. **Ask Questions**: Clarify requirements if unclear (via email)

---

## Appendix A: Example Game Flow

```
1. User lands on homepage
2. Selects "Play vs AI" or "Play vs Human"
3. [Multiplayer] Enters room or shares link
4. Ship placement phase begins
   - Place all 5 ships
   - Confirm placements
5. Battle phase
   - Take turns firing
   - See hits/misses/sunk ships
   - Continue until all ships sunk
6. Winner declared
7. Option to rematch or return to menu
```

## Appendix B: Data Model Examples

### Game State
```javascript
{
  gameId: "uuid",
  mode: "ai" | "multiplayer",
  status: "placement" | "battle" | "finished",
  players: [
    {
      id: "player1",
      ships: [...],
      shots: [...],
      shipsRemaining: 5
    },
    {
      id: "player2" | "ai",
      ships: [...],
      shots: [...],
      shipsRemaining: 3
    }
  ],
  currentTurn: "player1",
  winner: null | "player1" | "player2",
  startedAt: timestamp,
  endedAt: timestamp | null
}
```

### Move History
```javascript
{
  gameId: "uuid",
  moves: [
    {
      player: "player1",
      coordinate: {x: 3, y: 5},
      result: "hit" | "miss" | "sunk",
      shipSunk: "Destroyer" | null,
      timestamp: timestamp
    },
    ...
  ]
}
```

---

**Good luck! Show us what you can build. 🚀**
