import { describe, it, expect, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import BattlePhase from '../BattlePhase';
import { CellState, GamePhase, type GameState } from '../../types/game';

const createGrid = (defaultCell: CellState = CellState.EMPTY) =>
  Array.from({ length: 10 }, () => Array.from({ length: 10 }, () => defaultCell));

const createGameState = (): GameState => ({
  game_id: 'game-1',
  mode: 'ai',
  phase: GamePhase.BATTLE,
  current_turn: 'player1',
  winner: null,
  created_at: '2026-01-01T00:00:00Z',
  player1: {
    name: 'Player 1',
    grid: createGrid(),
    ships: [
      {
        type: 'carrier',
        length: 5,
        row: 0,
        col: 0,
        orientation: 'horizontal',
        hits: 0,
        is_sunk: false,
      },
    ],
    all_ships_placed: true,
    all_ships_sunk: false,
  },
  player2: {
    name: 'AI',
    grid: createGrid(),
    ships: [],
    all_ships_placed: true,
    all_ships_sunk: false,
  },
});

describe('BattlePhase Component', () => {
  it('calls onFireShot when clicking an untargeted enemy cell on your turn', async () => {
    const onFireShot = vi.fn().mockResolvedValue({ result: 'miss' });
    const onMenu = vi.fn();

    const { container } = render(
      <BattlePhase
        gameState={createGameState()}
        playerRole="player1"
        onFireShot={onFireShot}
        onMenu={onMenu}
        historyEvents={[]}
      />
    );

    const enemyCell = container.querySelectorAll('.grid-container')[1].querySelector('.cell') as HTMLElement;
    fireEvent.click(enemyCell);

    await waitFor(() => expect(onFireShot).toHaveBeenCalledWith({ row: 0, col: 0 }));
    expect(await screen.findByText('💧 MISS')).toBeInTheDocument();
  });

  it('blocks firing when it is not your turn', () => {
    const onFireShot = vi.fn();
    const onMenu = vi.fn();
    const gameState = { ...createGameState(), current_turn: 'player2' };

    const { container } = render(
      <BattlePhase
        gameState={gameState}
        playerRole="player1"
        onFireShot={onFireShot}
        onMenu={onMenu}
        historyEvents={[]}
      />
    );

    const enemyCell = container.querySelectorAll('.grid-container')[1].querySelector('.cell') as HTMLElement;
    fireEvent.click(enemyCell);

    expect(screen.getByText(/Opponent's Turn/i)).toBeInTheDocument();
    expect(onFireShot).not.toHaveBeenCalled();
  });

  it('blocks firing at a previously targeted cell', async () => {
    const onFireShot = vi.fn();
    const onMenu = vi.fn();
    const gameState = createGameState();
    gameState.player2.grid[0][0] = CellState.HIT;

    const { container } = render(
      <BattlePhase
        gameState={gameState}
        playerRole="player1"
        onFireShot={onFireShot}
        onMenu={onMenu}
        historyEvents={[]}
      />
    );

    const enemyCell = container.querySelectorAll('.grid-container')[1].querySelector('.cell') as HTMLElement;
    fireEvent.click(enemyCell);

    await screen.findByText(/Already shot this position!/i);
    expect(onFireShot).not.toHaveBeenCalled();
  });

  it('shows sunk feedback with ship name', async () => {
    const onFireShot = vi.fn().mockResolvedValue({ result: 'sunk', ship_type: 'destroyer' });
    const onMenu = vi.fn();

    const { container } = render(
      <BattlePhase
        gameState={createGameState()}
        playerRole="player1"
        onFireShot={onFireShot}
        onMenu={onMenu}
        historyEvents={[]}
      />
    );

    const enemyCell = container.querySelectorAll('.grid-container')[1].querySelector('.cell') as HTMLElement;
    fireEvent.click(enemyCell);

    expect(await screen.findByText(/sunk the destroyer/i)).toBeInTheDocument();
  });

  it('renders recent shots and supports auto-finish button state', () => {
    const onFireShot = vi.fn();
    const onAutoFinish = vi.fn();
    const onMenu = vi.fn();

    render(
      <BattlePhase
        gameState={createGameState()}
        playerRole="player1"
        onFireShot={onFireShot}
        onAutoFinish={onAutoFinish}
        autoFinishing={true}
        onMenu={onMenu}
        historyEvents={[
          {
            event_type: 'shot_fired',
            player: 'player1',
            created_at: '2026-01-01T00:00:00Z',
            row: 0,
            col: 0,
            result: 'hit',
          },
        ]}
      />
    );

    expect(screen.getByText(/Recent Shots/i)).toBeInTheDocument();
    expect(screen.getByText(/player1 fired at \(0, 0\) -> hit/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Finishing.../i })).toBeDisabled();
  });
});
