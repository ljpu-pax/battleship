import React from 'react';
import './GameEnd.css';

interface GameEndProps {
  winner: string;
  playerName: string;
  onRematch: () => void;
  onMenu: () => void;
}

const GameEnd: React.FC<GameEndProps> = ({ winner, playerName, onRematch, onMenu }) => {
  const isWinner = winner === playerName;

  return (
    <div className="game-end">
      <div className="end-container">
        <div className={`trophy-icon ${isWinner ? 'winner' : 'loser'}`}>
          {isWinner ? '🏆' : '💔'}
        </div>

        <h1 className={`end-title ${isWinner ? 'winner' : 'loser'}`}>
          {isWinner ? 'VICTORY!' : 'DEFEAT'}
        </h1>

        <div className="winner-announcement">
          <p className="winner-text">
            {isWinner ? `Congratulations, ${winner}!` : `${winner} wins!`}
          </p>
          <p className="subtext">
            {isWinner
              ? 'You sunk all enemy ships! ⚓'
              : 'All your ships have been destroyed. Better luck next time!'}
          </p>
        </div>

        <div className="end-actions">
          <button className="action-button rematch" onClick={onRematch}>
            <span className="button-icon">🔄</span>
            <span>Play Again</span>
          </button>

          <button className="action-button menu" onClick={onMenu}>
            <span className="button-icon">🏠</span>
            <span>Main Menu</span>
          </button>
        </div>

        <div className="fireworks-container">
          {isWinner && (
            <>
              <div className="firework"></div>
              <div className="firework"></div>
              <div className="firework"></div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default GameEnd;
