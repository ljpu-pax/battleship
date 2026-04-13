import React, { useState } from 'react';
import type { GameReplayResponse, PlayerAnalyticsResponse } from '../api/client';
import './GameEnd.css';

interface GameEndProps {
  winner: string;
  playerName: string;
  replay: GameReplayResponse | null;
  analytics: PlayerAnalyticsResponse | null;
  onRematch: () => void;
  onMenu: () => void;
}

const GameEnd: React.FC<GameEndProps> = ({
  winner,
  playerName,
  replay,
  analytics,
  onRematch,
  onMenu,
}) => {
  const isWinner = winner === playerName;
  const replaySteps = replay?.steps.slice(0, 10) ?? [];
  const [activePanel, setActivePanel] = useState<'replay' | 'analytics' | null>(null);

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

        {(analytics || replay) && (
          <div className="spike-actions">
            {replay && (
              <button
                className={`spike-button ${activePanel === 'replay' ? 'active' : ''}`}
                onClick={() =>
                  setActivePanel((current) => (current === 'replay' ? null : 'replay'))
                }
              >
                View Replay
              </button>
            )}
            {analytics && (
              <button
                className={`spike-button ${activePanel === 'analytics' ? 'active' : ''}`}
                onClick={() =>
                  setActivePanel((current) => (current === 'analytics' ? null : 'analytics'))
                }
              >
                View Analytics
              </button>
            )}
          </div>
        )}

        {analytics && activePanel === 'analytics' && (
          <div className="insight-panel">
            <h2>Basic Analytics</h2>
            <div className="insight-grid">
              <div className="insight-card">
                <span className="insight-label">Win Rate</span>
                <strong>{(analytics.win_rate * 100).toFixed(0)}%</strong>
              </div>
              <div className="insight-card">
                <span className="insight-label">Hit Rate</span>
                <strong>{(analytics.hit_rate * 100).toFixed(0)}%</strong>
              </div>
              <div className="insight-card">
                <span className="insight-label">Avg Turns</span>
                <strong>{analytics.average_turns_per_game.toFixed(1)}</strong>
              </div>
              <div className="insight-card">
                <span className="insight-label">Games Played</span>
                <strong>{analytics.games_played}</strong>
              </div>
            </div>

            {analytics.recent_games.length > 0 && (
              <div className="insight-list">
                <h3>Recent Games</h3>
                {analytics.recent_games.map((game) => (
                  <div key={game.game_id} className="insight-row">
                    <span>{game.mode}</span>
                    <span>{game.turns} turns</span>
                    <span>{game.winner ?? 'In progress'}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {replay && activePanel === 'replay' && (
          <div className="insight-panel">
            <h2>Replay Timeline</h2>
            <p className="subtext">
              {replay.summary.total_turns} turns, P1 hits {replay.summary.player1_hits}, P2 hits{' '}
              {replay.summary.player2_hits}
            </p>
            <div className="insight-list">
              {replaySteps.map((step) => (
                <div key={`${step.turn_number}-${step.created_at}`} className="insight-row">
                  <span>Turn {step.turn_number}</span>
                  <span>{step.player}</span>
                  <span>
                    ({step.row}, {step.col}) {step.result}
                    {step.ship_sunk ? `, sunk ${step.ship_sunk}` : ''}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

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
