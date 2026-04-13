import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import GameEnd from '../GameEnd';

describe('GameEnd Component', () => {
  const replay = {
    game_id: 'game-1',
    steps: [
      {
        turn_number: 1,
        player: 'player1',
        row: 0,
        col: 0,
        result: 'hit',
        created_at: '2026-01-01T00:00:00Z',
      },
    ],
    summary: {
      total_turns: 1,
      player1_hits: 1,
      player2_hits: 0,
    },
  };

  const analytics = {
    player_name: 'Player1',
    games_played: 2,
    wins: 1,
    losses: 1,
    active_games: 0,
    win_rate: 0.5,
    hit_rate: 0.75,
    average_turns_per_game: 12,
    recent_games: [
      {
        game_id: 'game-1',
        mode: 'ai',
        phase: 'finished',
        winner: 'Player1',
        turns: 12,
        hit_rate: 0.75,
        updated_at: '2026-01-01T00:00:00Z',
      },
    ],
  };

  it('displays victory message when player wins', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    render(
      <GameEnd
        winner="Player1"
        playerName="Player1"
        replay={null}
        analytics={null}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    expect(screen.getByText(/VICTORY!/i)).toBeInTheDocument();
    expect(screen.getByText(/Congratulations, Player1!/i)).toBeInTheDocument();
  });

  it('displays defeat message when player loses', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    render(
      <GameEnd
        winner="AI"
        playerName="Player1"
        replay={null}
        analytics={null}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    expect(screen.getByText(/DEFEAT/i)).toBeInTheDocument();
    expect(screen.getByText(/AI wins!/i)).toBeInTheDocument();
  });

  it('shows trophy icon when player wins', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    const { container } = render(
      <GameEnd
        winner="Player1"
        playerName="Player1"
        replay={null}
        analytics={null}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    const trophy = container.querySelector('.trophy-icon.winner');
    expect(trophy).toBeInTheDocument();
    expect(trophy?.textContent).toBe('🏆');
  });

  it('shows broken heart icon when player loses', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    const { container } = render(
      <GameEnd
        winner="AI"
        playerName="Player1"
        replay={null}
        analytics={null}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    const trophy = container.querySelector('.trophy-icon.loser');
    expect(trophy).toBeInTheDocument();
    expect(trophy?.textContent).toBe('💔');
  });

  it('has Play Again button', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    render(
      <GameEnd
        winner="Player1"
        playerName="Player1"
        replay={null}
        analytics={null}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    expect(screen.getByText(/Play Again/i)).toBeInTheDocument();
  });

  it('has Main Menu button', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    render(
      <GameEnd
        winner="Player1"
        playerName="Player1"
        replay={null}
        analytics={null}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    expect(screen.getByText(/Main Menu/i)).toBeInTheDocument();
  });

  it('calls onRematch when Play Again is clicked', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    render(
      <GameEnd
        winner="Player1"
        playerName="Player1"
        replay={null}
        analytics={null}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    const playAgainButton = screen.getByText(/Play Again/i);
    fireEvent.click(playAgainButton);

    expect(handleRematch).toHaveBeenCalledTimes(1);
  });

  it('calls onMenu when Main Menu is clicked', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    render(
      <GameEnd
        winner="Player1"
        playerName="Player1"
        replay={null}
        analytics={null}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    const menuButton = screen.getByText(/Main Menu/i);
    fireEvent.click(menuButton);

    expect(handleMenu).toHaveBeenCalledTimes(1);
  });

  it('shows fireworks when player wins', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    const { container } = render(
      <GameEnd
        winner="Player1"
        playerName="Player1"
        replay={null}
        analytics={null}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    const fireworks = container.querySelectorAll('.firework');
    expect(fireworks.length).toBeGreaterThan(0);
  });

  it('does not show fireworks when player loses', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    const { container } = render(
      <GameEnd
        winner="AI"
        playerName="Player1"
        replay={null}
        analytics={null}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    const fireworks = container.querySelectorAll('.firework');
    expect(fireworks).toHaveLength(0);
  });

  it('shows spike buttons when replay and analytics exist', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    render(
      <GameEnd
        winner="Player1"
        playerName="Player1"
        replay={replay}
        analytics={analytics}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    expect(screen.getByText(/View Replay/i)).toBeInTheDocument();
    expect(screen.getByText(/View Analytics/i)).toBeInTheDocument();
  });

  it('toggles analytics panel', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    render(
      <GameEnd
        winner="Player1"
        playerName="Player1"
        replay={replay}
        analytics={analytics}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    fireEvent.click(screen.getByText(/View Analytics/i));
    expect(screen.getByText(/Basic Analytics/i)).toBeInTheDocument();
  });

  it('toggles replay panel', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    render(
      <GameEnd
        winner="Player1"
        playerName="Player1"
        replay={replay}
        analytics={analytics}
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    fireEvent.click(screen.getByText(/View Replay/i));
    expect(screen.getByText(/Replay Timeline/i)).toBeInTheDocument();
  });
});
