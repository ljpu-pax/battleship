import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import MainMenu from '../MainMenu';

describe('MainMenu Component', () => {
  it('renders main menu with title', () => {
    const handleStart = vi.fn();
    render(<MainMenu onStartGame={handleStart} />);

    expect(screen.getByText(/BATTLESHIP/i)).toBeInTheDocument();
  });

  it('has player name input field', () => {
    const handleStart = vi.fn();
    render(<MainMenu onStartGame={handleStart} />);

    const input = screen.getByPlaceholderText(/enter your name/i);
    expect(input).toBeInTheDocument();
  });

  it('has AI and Multiplayer mode buttons', () => {
    const handleStart = vi.fn();
    render(<MainMenu onStartGame={handleStart} />);

    expect(screen.getByText(/vs AI/i)).toBeInTheDocument();
    expect(screen.getByText(/Multiplayer/i)).toBeInTheDocument();
  });

  it('start button is disabled when name is empty', () => {
    const handleStart = vi.fn();
    render(<MainMenu onStartGame={handleStart} />);

    const startButton = screen.getByText(/Start Game/i);
    expect(startButton).toBeDisabled();
  });

  it('start button is disabled when mode is not selected', () => {
    const handleStart = vi.fn();
    render(<MainMenu onStartGame={handleStart} />);

    const input = screen.getByPlaceholderText(/enter your name/i);
    fireEvent.change(input, { target: { value: 'Player1' } });

    const startButton = screen.getByText(/Start Game/i);
    expect(startButton).toBeDisabled();
  });

  it('allows selecting AI mode', () => {
    const handleStart = vi.fn();
    render(<MainMenu onStartGame={handleStart} />);

    const aiButton = screen.getByText(/vs AI/i).closest('button');
    fireEvent.click(aiButton!);

    expect(aiButton).toHaveClass('selected');
  });

  it('allows selecting Multiplayer mode', () => {
    const handleStart = vi.fn();
    render(<MainMenu onStartGame={handleStart} />);

    const multiplayerButton = screen.getByText(/Multiplayer/i).closest('button');
    fireEvent.click(multiplayerButton!);

    expect(multiplayerButton).toHaveClass('selected');
  });

  it('calls onStartGame with correct parameters when AI mode is selected', () => {
    const handleStart = vi.fn();
    render(<MainMenu onStartGame={handleStart} />);

    const input = screen.getByPlaceholderText(/enter your name/i);
    fireEvent.change(input, { target: { value: 'Player1' } });

    const aiButton = screen.getByText(/vs AI/i).closest('button');
    fireEvent.click(aiButton!);

    const startButton = screen.getByText(/Start Game/i);
    fireEvent.click(startButton);

    expect(handleStart).toHaveBeenCalledWith('Player1', 'ai');
  });

  it('calls onStartGame with correct parameters when Multiplayer mode is selected', () => {
    const handleStart = vi.fn();
    render(<MainMenu onStartGame={handleStart} />);

    const input = screen.getByPlaceholderText(/enter your name/i);
    fireEvent.change(input, { target: { value: 'Player2' } });

    const multiplayerButton = screen.getByText(/Multiplayer/i).closest('button');
    fireEvent.click(multiplayerButton!);

    const startButton = screen.getByText(/Start Game/i);
    fireEvent.click(startButton);

    expect(handleStart).toHaveBeenCalledWith('Player2', 'multiplayer');
  });

  it('trims whitespace from player name', () => {
    const handleStart = vi.fn();
    render(<MainMenu onStartGame={handleStart} />);

    const input = screen.getByPlaceholderText(/enter your name/i);
    fireEvent.change(input, { target: { value: '  Player1  ' } });

    const aiButton = screen.getByText(/vs AI/i).closest('button');
    fireEvent.click(aiButton!);

    const startButton = screen.getByText(/Start Game/i);
    fireEvent.click(startButton);

    expect(handleStart).toHaveBeenCalledWith('Player1', 'ai');
  });
});
