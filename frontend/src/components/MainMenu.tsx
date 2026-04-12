import React, { useState } from 'react';
import './MainMenu.css';

interface MainMenuProps {
  onStartGame: (playerName: string, mode: 'ai' | 'multiplayer') => void;
}

const MainMenu: React.FC<MainMenuProps> = ({ onStartGame }) => {
  const [playerName, setPlayerName] = useState('');
  const [selectedMode, setSelectedMode] = useState<'ai' | 'multiplayer' | null>(null);

  const handleStartGame = () => {
    if (playerName.trim() && selectedMode) {
      onStartGame(playerName.trim(), selectedMode);
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

        <button
          className="start-button"
          onClick={handleStartGame}
          disabled={!playerName.trim() || !selectedMode}
        >
          Start Game
        </button>
      </div>
    </div>
  );
};

export default MainMenu;
