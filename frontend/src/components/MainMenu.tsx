import React, { useState } from 'react';
import './MainMenu.css';

interface MainMenuProps {
  onCreateGame: (playerName: string, mode: 'ai' | 'multiplayer') => void;
  onJoinGame: (playerName: string, gameId: string) => void;
  defaultGameId?: string;
}

const MainMenu: React.FC<MainMenuProps> = ({ onCreateGame, onJoinGame, defaultGameId = '' }) => {
  const [playerName, setPlayerName] = useState('');
  const [selectedMode, setSelectedMode] = useState<'ai' | 'multiplayer' | null>(
    defaultGameId ? 'multiplayer' : null
  );
  const [gameId, setGameId] = useState(defaultGameId);

  const trimmedName = playerName.trim();
  const trimmedGameId = gameId.trim();

  const handleCreateGame = () => {
    if (trimmedName && selectedMode) {
      onCreateGame(trimmedName, selectedMode);
    }
  };

  const handleJoinGame = () => {
    if (trimmedName && trimmedGameId) {
      onJoinGame(trimmedName, trimmedGameId);
    }
  };

  return (
    <div className="main-menu">
      <div className="menu-container">
        <h1 className="game-title">⚓ BATTLESHIP</h1>

        <div className="menu-section">
          <label htmlFor="player-name">Your Name:</label>
          <input
            id="player-name"
            type="text"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            placeholder="Enter your name"
            maxLength={20}
          />
        </div>

        <div className="menu-section">
          <h2>Select Game Mode:</h2>
          <div className="mode-buttons">
            <button
              className={`mode-button ${selectedMode === 'ai' ? 'selected' : ''}`}
              onClick={() => setSelectedMode('ai')}
            >
              <div className="mode-icon">🤖</div>
              <div className="mode-title">vs AI</div>
              <div className="mode-desc">Play against computer</div>
            </button>

            <button
              className={`mode-button ${selectedMode === 'multiplayer' ? 'selected' : ''}`}
              onClick={() => setSelectedMode('multiplayer')}
            >
              <div className="mode-icon">👥</div>
              <div className="mode-title">Multiplayer</div>
              <div className="mode-desc">Play against human</div>
            </button>
          </div>
        </div>

        {selectedMode === 'multiplayer' && (
          <div className="menu-section">
            <label htmlFor="game-id">Join Existing Room:</label>
            <input
              id="game-id"
              type="text"
              value={gameId}
              onChange={(e) => setGameId(e.target.value)}
              placeholder="Enter game ID to join"
            />
          </div>
        )}

        {selectedMode === 'multiplayer' ? (
          <div className="mode-buttons">
            <button
              className="start-button"
              onClick={handleCreateGame}
              disabled={!trimmedName}
            >
              Create Room
            </button>
            <button
              className="start-button"
              onClick={handleJoinGame}
              disabled={!trimmedName || !trimmedGameId}
            >
              Join Room
            </button>
          </div>
        ) : (
          <button
            className="start-button"
            onClick={handleCreateGame}
            disabled={!trimmedName || !selectedMode}
          >
            Start Game
          </button>
        )}
      </div>
    </div>
  );
};

export default MainMenu;
