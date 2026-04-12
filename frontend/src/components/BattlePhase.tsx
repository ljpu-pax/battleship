import React, { useState } from 'react';
import Grid from './Grid';
import { CellState } from '../types/game';
import type { GameState } from '../types/game';
import type { FireShotRequest } from '../api/client';
import './BattlePhase.css';

interface ShotResult {
  result: string;
  ship_type?: string;
}

interface BattlePhaseProps {
  gameState: GameState;
  playerName: string;
  onFireShot: (request: FireShotRequest) => Promise<ShotResult>;
  disabled?: boolean;
}

const BattlePhase: React.FC<BattlePhaseProps> = ({
  gameState,
  playerName,
  onFireShot,
  disabled = false,
}) => {
  const [selectedCell, setSelectedCell] = useState<{ row: number; col: number } | null>(null);
  const [message, setMessage] = useState<string>('');
  const [messageType, setMessageType] = useState<'success' | 'error' | 'info'>('info');

  const isPlayer1 = gameState.player1.name === playerName;
  const myGrid = isPlayer1 ? gameState.player1.grid : gameState.player2.grid;
  const opponentGrid = isPlayer1 ? gameState.player2.grid : gameState.player1.grid;
  const isMyTurn = gameState.current_turn === playerName;

  const handleTargetCellClick = async (row: number, col: number) => {
    if (!isMyTurn || disabled) {
      showMessage('Not your turn!', 'error');
      return;
    }

    // Check if already shot
    const cellState = opponentGrid[row][col];
    if (cellState === CellState.HIT || cellState === CellState.MISS) {
      showMessage('Already shot this position!', 'error');
      return;
    }

    setSelectedCell({ row, col });

    try {
      const result = await onFireShot({ row, col });

      if (result.result === 'sunk') {
        showMessage(`💥 HIT! You sunk the ${result.ship_type}!`, 'success');
      } else if (result.result === 'hit') {
        showMessage('💥 HIT!', 'success');
      } else {
        showMessage('💧 MISS', 'info');
      }

      setSelectedCell(null);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      showMessage(error.response?.data?.detail || 'Failed to fire shot', 'error');
      setSelectedCell(null);
    }
  };

  const showMessage = (msg: string, type: 'success' | 'error' | 'info') => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => setMessage(''), 3000);
  };

  return (
    <div className="battle-phase">
      <div className="battle-header">
        <h2>⚓ Battle Phase</h2>
        <div className={`turn-indicator ${isMyTurn ? 'my-turn' : 'opponent-turn'}`}>
          {isMyTurn ? "🎯 YOUR TURN" : "⏳ Opponent's Turn"}
        </div>
      </div>

      {message && (
        <div className={`battle-message ${messageType}`}>
          {message}
        </div>
      )}

      <div className="battle-grids">
        <div className="grid-section">
          <h3>Your Fleet</h3>
          <Grid
            grid={myGrid}
            showShips={true}
            disabled={true}
          />
          <div className="grid-stats">
            <div>Ships: {gameState[isPlayer1 ? 'player1' : 'player2'].ships.length}/5</div>
            <div className={gameState[isPlayer1 ? 'player1' : 'player2'].all_ships_sunk ? 'danger' : ''}>
              {gameState[isPlayer1 ? 'player1' : 'player2'].all_ships_sunk ? '💀 Fleet Destroyed' : '⚡ Fleet Active'}
            </div>
          </div>
        </div>

        <div className="grid-section">
          <h3>Enemy Waters</h3>
          <Grid
            grid={opponentGrid}
            onCellClick={handleTargetCellClick}
            showShips={false}
            highlightCells={selectedCell ? [selectedCell] : []}
            disabled={!isMyTurn || disabled}
          />
          <div className="grid-stats">
            <div>
              Hits: {opponentGrid.flat().filter(cell => cell === CellState.HIT).length}
            </div>
            <div>
              Misses: {opponentGrid.flat().filter(cell => cell === CellState.MISS).length}
            </div>
          </div>
        </div>
      </div>

      <div className="battle-instructions">
        <p>{isMyTurn ? '👆 Click on Enemy Waters grid to fire!' : '⏳ Waiting for opponent...'}</p>
      </div>
    </div>
  );
};

export default BattlePhase;
