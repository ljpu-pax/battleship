import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import GameEnd from '../GameEnd';

describe('GameEnd Component', () => {
  it('displays victory message when player wins', () => {
    const handleRematch = vi.fn();
    const handleMenu = vi.fn();

    render(
      <GameEnd
        winner="Player1"
        playerName="Player1"
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
        onRematch={handleRematch}
        onMenu={handleMenu}
      />
    );

    const fireworks = container.querySelectorAll('.firework');
    expect(fireworks).toHaveLength(0);
  });
});
