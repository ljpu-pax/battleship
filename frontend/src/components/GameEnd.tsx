import React, { useEffect, useMemo, useState } from 'react';
import Grid from './Grid';
import { CellState } from '../types/game';
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
  const hasReplay = Boolean(replay?.steps.length);
  const hasAnalytics = Boolean(analytics);
  const [activePanel, setActivePanel] = useState<'replay' | 'analytics' | null>(
    hasReplay ? 'replay' : hasAnalytics ? 'analytics' : null
  );
  const [replayIndex, setReplayIndex] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);

  const replaySteps = replay?.steps ?? [];
  const replayLength = replaySteps.length;
  const replayComplete = replayLength > 0 && replayIndex >= replayLength - 1;
  const currentReplayStep =
    replayIndex >= 0 && replayIndex < replayLength ? replaySteps[replayIndex] : null;

  useEffect(() => {
    if (activePanel !== 'replay' || !isPlaying || replayLength === 0) {
      return;
    }

    if (replayComplete) {
      return;
    }

    const timer = window.setTimeout(() => {
      setReplayIndex((current) => Math.min(current + 1, replayLength - 1));
    }, 700);

    return () => window.clearTimeout(timer);
  }, [activePanel, isPlaying, replayComplete, replayIndex, replayLength]);

  const replayBoards = useMemo(() => {
    const createGrid = (source?: string[][]): CellState[][] =>
      Array.from({ length: 10 }, (_, rowIndex) =>
        Array.from({ length: 10 }, (_, colIndex) => {
          const nextCell = source?.[rowIndex]?.[colIndex];
          return nextCell === CellState.SHIP ? CellState.SHIP : (CellState.EMPTY as CellState);
        })
      );

    const player1Fleet = createGrid(replay?.fleets.player1);
    const player2Fleet = createGrid(replay?.fleets.player2);

    if (!replay || replayIndex < 0) {
      return { player1Fleet, player2Fleet };
    }

    for (let index = 0; index <= replayIndex; index += 1) {
      const step = replay.steps[index];
      const nextState = step.result === 'miss' ? CellState.MISS : CellState.HIT;
      const targetGrid = step.player === 'player1' ? player2Fleet : player1Fleet;
      targetGrid[step.row][step.col] = nextState;
    }

    return { player1Fleet, player2Fleet };
  }, [replay, replayIndex]);

  const highlightedReplayCell = currentReplayStep
    ? [{ row: currentReplayStep.row, col: currentReplayStep.col }]
    : [];

  const replayHeadline = currentReplayStep
    ? `${currentReplayStep.player === 'player1' ? 'Player 1' : 'Player 2'} fired at (${currentReplayStep.row}, ${currentReplayStep.col})`
    : 'Press play to watch the battle unfold.';

  const replaySubline = currentReplayStep
    ? currentReplayStep.ship_sunk
      ? `${currentReplayStep.result.toUpperCase()} and sunk ${currentReplayStep.ship_sunk}`
      : currentReplayStep.result.toUpperCase()
    : `${replayLength} total turns recorded`;

  const winRate = analytics ? Math.round(analytics.win_rate * 100) : 0;
  const hitRate = analytics ? Math.round(analytics.hit_rate * 100) : 0;

  const jumpReplay = (nextIndex: number) => {
    if (!replayLength) {
      return;
    }

    setReplayIndex(Math.max(-1, Math.min(nextIndex, replayLength - 1)));
  };

  return (
    <div className="game-end">
      <div className="end-container">
        <div className={`ambient-glow ${isWinner ? 'winner' : 'loser'}`}></div>

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
                onClick={() => setActivePanel('replay')}
              >
                Battle Replay
              </button>
            )}
            {analytics && (
              <button
                className={`spike-button ${activePanel === 'analytics' ? 'active' : ''}`}
                onClick={() => setActivePanel('analytics')}
              >
                Postgame Intel
              </button>
            )}
          </div>
        )}

        {analytics && activePanel === 'analytics' && (
          <div className="insight-panel analytics-panel">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">Postgame Intel</p>
                <h2>How {playerName} is performing</h2>
              </div>
              <div className="panel-chip">Last {analytics.games_played} games</div>
            </div>

            <div className="insight-grid">
              <div className="insight-card">
                <span className="insight-label">Win Rate</span>
                <strong>{winRate}%</strong>
                <div className="insight-meter">
                  <div className="insight-meter-fill" style={{ width: `${winRate}%` }}></div>
                </div>
              </div>
              <div className="insight-card">
                <span className="insight-label">Hit Rate</span>
                <strong>{hitRate}%</strong>
                <div className="insight-meter">
                  <div className="insight-meter-fill accent" style={{ width: `${hitRate}%` }}></div>
                </div>
              </div>
              <div className="insight-card">
                <span className="insight-label">Avg Turns</span>
                <strong>{analytics.average_turns_per_game.toFixed(1)}</strong>
                <p className="insight-copy">Average battle length across recorded matches</p>
              </div>
              <div className="insight-card">
                <span className="insight-label">Games Played</span>
                <strong>{analytics.games_played}</strong>
                <p className="insight-copy">
                  {analytics.wins} wins, {analytics.losses} losses, {analytics.active_games} active
                </p>
              </div>
            </div>

            {analytics.recent_games.length > 0 && (
              <div className="insight-list">
                <h3>Recent Battles</h3>
                {analytics.recent_games.map((game) => (
                  <div key={game.game_id} className="insight-row">
                    <div>
                      <strong>{game.mode === 'ai' ? 'AI Skirmish' : 'Multiplayer Duel'}</strong>
                      <p>{game.turns} turns</p>
                    </div>
                    <div>
                      <strong>{Math.round(game.hit_rate * 100)}% hit rate</strong>
                      <p>{game.winner ?? 'In progress'}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {replay && activePanel === 'replay' && (
          <div className="insight-panel replay-panel">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">Battle Replay</p>
                <h2>Watch the match play back turn by turn</h2>
              </div>
              <div className="panel-chip">
                {replay.summary.total_turns} turns | P1 hits {replay.summary.player1_hits} | P2 hits{' '}
                {replay.summary.player2_hits}
              </div>
            </div>

            <div className="replay-hero">
              <div>
                <div className="replay-turn">
                  {currentReplayStep ? `Turn ${currentReplayStep.turn_number}` : 'Replay Ready'}
                </div>
                <h3>{replayHeadline}</h3>
                <p>{replaySubline}</p>
              </div>

              <div className="replay-controls">
                <button className="spike-button ghost" onClick={() => jumpReplay(-1)}>
                  Reset
                </button>
                <button
                  className="spike-button ghost"
                  onClick={() => {
                    setIsPlaying(false);
                    jumpReplay(replayIndex - 1);
                  }}
                  disabled={replayIndex < 0}
                >
                  Prev
                </button>
                <button
                  className="spike-button active"
                  onClick={() => {
                    if (replayComplete) {
                      setReplayIndex(-1);
                      setIsPlaying(true);
                      return;
                    }
                    setIsPlaying((current) => !current);
                  }}
                  disabled={!replayLength}
                >
                  {replayComplete ? 'Replay Again' : isPlaying ? 'Pause' : 'Play'}
                </button>
                <button
                  className="spike-button ghost"
                  onClick={() => {
                    setIsPlaying(false);
                    jumpReplay(replayIndex + 1);
                  }}
                  disabled={replayIndex >= replayLength - 1}
                >
                  Next
                </button>
              </div>
            </div>

            <div className="replay-progress">
              <input
                type="range"
                min={0}
                max={Math.max(replayLength, 1)}
                value={replayIndex + 1}
                onChange={(event) => {
                  setIsPlaying(false);
                  setReplayIndex(Number(event.target.value) - 1);
                }}
              />
              <div className="replay-progress-copy">
                <span>Start</span>
                <span>
                  {Math.max(replayIndex + 1, 0)} / {replayLength}
                </span>
                <span>Final turn</span>
              </div>
            </div>

            <div className="replay-grids">
              <div className="replay-grid-card">
                <div className="replay-grid-header">
                  <h3>Player 1 Fleet Board</h3>
                  <span>Original ship layout with incoming fire</span>
                </div>
                <Grid
                  grid={replayBoards.player1Fleet}
                  showShips={true}
                  disabled={true}
                  highlightCells={currentReplayStep?.player === 'player2' ? highlightedReplayCell : []}
                />
              </div>

              <div className="replay-grid-card">
                <div className="replay-grid-header">
                  <h3>Player 2 Fleet Board</h3>
                  <span>Original ship layout with incoming fire</span>
                </div>
                <Grid
                  grid={replayBoards.player2Fleet}
                  showShips={true}
                  disabled={true}
                  highlightCells={currentReplayStep?.player === 'player1' ? highlightedReplayCell : []}
                />
              </div>
            </div>

            <div className="timeline-strip">
              {replaySteps.map((step, index) => (
                <button
                  key={`${step.turn_number}-${step.created_at}`}
                  className={`timeline-step ${index === replayIndex ? 'active' : ''}`}
                  onClick={() => {
                    setIsPlaying(false);
                    setReplayIndex(index);
                  }}
                >
                  <span>T{step.turn_number}</span>
                  <strong>{step.result}</strong>
                </button>
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
