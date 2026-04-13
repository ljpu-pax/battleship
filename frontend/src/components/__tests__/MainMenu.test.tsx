import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import MainMenu from '../MainMenu';

describe('MainMenu Component', () => {
  it('renders main menu with title', () => {
    const handleCreate = vi.fn();
    const handleJoin = vi.fn();
    render(<MainMenu onCreateGame={handleCreate} onJoinGame={handleJoin} />);

    expect(screen.getByText(/BATTLESHIP/i)).toBeInTheDocument();
  });

  it('has player name input field', () => {
    const handleCreate = vi.fn();
    const handleJoin = vi.fn();
    render(<MainMenu onCreateGame={handleCreate} onJoinGame={handleJoin} />);

    expect(screen.getByPlaceholderText(/enter your name/i)).toBeInTheDocument();
  });

  it('has AI and Multiplayer mode buttons', () => {
    const handleCreate = vi.fn();
    const handleJoin = vi.fn();
    render(<MainMenu onCreateGame={handleCreate} onJoinGame={handleJoin} />);

    expect(screen.getByText(/vs AI/i)).toBeInTheDocument();
    expect(screen.getByText(/Multiplayer/i)).toBeInTheDocument();
  });

  it('start button is disabled when name is empty', () => {
    const handleCreate = vi.fn();
    const handleJoin = vi.fn();
    render(<MainMenu onCreateGame={handleCreate} onJoinGame={handleJoin} />);

    expect(screen.getByText(/Start Game/i)).toBeDisabled();
  });

  it('allows selecting AI mode', () => {
    const handleCreate = vi.fn();
    const handleJoin = vi.fn();
    render(<MainMenu onCreateGame={handleCreate} onJoinGame={handleJoin} />);

    const aiButton = screen.getByText(/vs AI/i).closest('button');
    fireEvent.click(aiButton!);

    expect(aiButton).toHaveClass('selected');
  });

  it('allows selecting Multiplayer mode', () => {
    const handleCreate = vi.fn();
    const handleJoin = vi.fn();
    render(<MainMenu onCreateGame={handleCreate} onJoinGame={handleJoin} />);

    const multiplayerButton = screen.getByText(/Multiplayer/i).closest('button');
    fireEvent.click(multiplayerButton!);

    expect(multiplayerButton).toHaveClass('selected');
    expect(screen.getByPlaceholderText(/enter game id to join/i)).toBeInTheDocument();
  });

  it('calls onCreateGame with correct parameters when AI mode is selected', () => {
    const handleCreate = vi.fn();
    const handleJoin = vi.fn();
    render(<MainMenu onCreateGame={handleCreate} onJoinGame={handleJoin} />);

    fireEvent.change(screen.getByPlaceholderText(/enter your name/i), {
      target: { value: 'Player1' },
    });
    fireEvent.click(screen.getByText(/vs AI/i).closest('button')!);
    fireEvent.click(screen.getByText(/Start Game/i));

    expect(handleCreate).toHaveBeenCalledWith('Player1', 'ai');
    expect(handleJoin).not.toHaveBeenCalled();
  });

  it('calls onCreateGame for multiplayer room creation', () => {
    const handleCreate = vi.fn();
    const handleJoin = vi.fn();
    render(<MainMenu onCreateGame={handleCreate} onJoinGame={handleJoin} />);

    fireEvent.change(screen.getByPlaceholderText(/enter your name/i), {
      target: { value: 'Player2' },
    });
    fireEvent.click(screen.getByText(/Multiplayer/i).closest('button')!);
    fireEvent.click(screen.getByText(/Create Room/i));

    expect(handleCreate).toHaveBeenCalledWith('Player2', 'multiplayer');
  });

  it('calls onJoinGame with correct parameters for multiplayer join', () => {
    const handleCreate = vi.fn();
    const handleJoin = vi.fn();
    render(<MainMenu onCreateGame={handleCreate} onJoinGame={handleJoin} />);

    fireEvent.change(screen.getByPlaceholderText(/enter your name/i), {
      target: { value: 'Guest' },
    });
    fireEvent.click(screen.getByText(/Multiplayer/i).closest('button')!);
    fireEvent.change(screen.getByPlaceholderText(/enter game id to join/i), {
      target: { value: 'abc-123' },
    });
    fireEvent.click(screen.getByText(/Join Room/i));

    expect(handleJoin).toHaveBeenCalledWith('Guest', 'abc-123');
  });

  it('trims whitespace from player name and game id', () => {
    const handleCreate = vi.fn();
    const handleJoin = vi.fn();
    render(<MainMenu onCreateGame={handleCreate} onJoinGame={handleJoin} />);

    fireEvent.change(screen.getByPlaceholderText(/enter your name/i), {
      target: { value: '  Guest  ' },
    });
    fireEvent.click(screen.getByText(/Multiplayer/i).closest('button')!);
    fireEvent.change(screen.getByPlaceholderText(/enter game id to join/i), {
      target: { value: '  room-42  ' },
    });
    fireEvent.click(screen.getByText(/Join Room/i));

    expect(handleJoin).toHaveBeenCalledWith('Guest', 'room-42');
  });
});
