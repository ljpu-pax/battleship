import React, { useState } from 'react';
import Grid from './Grid';
import { CellState } from '../types/game';
import type { GameState } from '../types/game';
import type { FireShotRequest, GameHistoryEvent } from '../api/client';
import './BattlePhase.css';

interface ShotResult {
  result: string;
  ship_type?: string;
}

interface BattlePhaseProps {
  gameState: GameState;
  playerRole: 'player1' | 'player2';
  onFireShot: (request: FireShotRequest) => Promise<ShotResult>;
  onMenu: () => void;
  historyEvents: GameHistoryEvent[];
  disabled?: boolean;
}

const BattlePhase: React.FC<BattlePhaseProps> = ({
  gameState,
  playerRole,
  onFireShot,
  onMenu,
  historyEvents,
  disabled = false,
}) => {
  const [selectedCell, setSelectedCell] = useState<{ row: number; col: number } | null>(null);
  const [message, setMessage] = useState<string>('');
  const [messageType, setMessageType] = useState<'success' | 'error' | 'info'>('info');

  const isPlayer1 = playerRole === 'player1';
  const myGrid = isPlayer1 ? gameState.player1?.grid : gameState.player2?.grid;
  const opponentGrid = isPlayer1 ? gameState.player2?.grid : gameState.player1?.grid;
  const isMyTurn =
    (isPlayer1 && gameState.current_turn === 'player1') ||
    (!isPlayer1 && gameState.current_turn === 'player2');
  const recentShots = historyEvents.filter((event) => event.event_type === 'shot_fired').slice(-6).reverse();

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

  // Safety check
  if (!myGrid || !opponentGrid) {
    return <div className="loading">Loading battle phase...</div>;
  }

  return (
    <div className="battle-phase">
      <div className="battle-header">
        <h2>⚓ Battle Phase</h2>
        <div className={`turn-indicator ${isMyTurn ? 'my-turn' : 'opponent-turn'}`}>
          {isMyTurn ? "🎯 YOUR TURN" : "⏳ Opponent's Turn"}
        </div>
        <button className="leave-button" onClick={onMenu}>
          Return to Menu
        </button>
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

      <div className="battle-instructions">
        <p>Game ID: <strong>{gameState.game_id}</strong></p>
      </div>

      {recentShots.length > 0 && (
        <div className="battle-message info">
          <strong>Recent Shots</strong>
          <div>
            {recentShots.map((event, index) => (
              <div key={`${event.created_at}-${index}`}>
                {event.player} fired at ({event.row}, {event.col}) {'->'} {event.result}
                {event.ship_sunk ? `, sunk ${event.ship_sunk}` : ''}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default BattlePhase;
