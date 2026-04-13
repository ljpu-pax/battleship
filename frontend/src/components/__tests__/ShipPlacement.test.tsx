import { describe, it, expect, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import ShipPlacement from '../ShipPlacement';
import { CellState, ShipType } from '../../types/game';

const createGrid = () =>
  Array.from({ length: 10 }, () => Array.from({ length: 10 }, () => CellState.EMPTY));

describe('ShipPlacement Component', () => {
  it('keeps confirm disabled until all ships are placed', () => {
    render(
      <ShipPlacement
        grid={createGrid()}
        placedShips={[]}
        onPlaceShip={vi.fn().mockResolvedValue({})}
        onConfirm={vi.fn()}
        onMenu={vi.fn()}
      />
    );

    expect(screen.getByRole('button', { name: /0\/5 Ships Placed/i })).toBeDisabled();
  });

  it('enables confirm once all ships are placed', () => {
    const onConfirm = vi.fn();

    render(
      <ShipPlacement
        grid={createGrid()}
        placedShips={[
          ShipType.CARRIER,
          ShipType.BATTLESHIP,
          ShipType.CRUISER,
          ShipType.SUBMARINE,
          ShipType.DESTROYER,
        ]}
        onPlaceShip={vi.fn().mockResolvedValue({})}
        onConfirm={onConfirm}
        onMenu={vi.fn()}
      />
    );

    const confirmButton = screen.getByRole('button', { name: /Confirm Placement/i });
    expect(confirmButton).toBeEnabled();
    fireEvent.click(confirmButton);
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('toggles orientation before placing a ship', async () => {
    const onPlaceShip = vi.fn().mockResolvedValue({});
    const { container } = render(
      <ShipPlacement
        grid={createGrid()}
        placedShips={[]}
        onPlaceShip={onPlaceShip}
        onConfirm={vi.fn()}
        onMenu={vi.fn()}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /Orientation: horizontal/i }));
    const firstCell = container.querySelector('.cell') as HTMLElement;
    fireEvent.click(firstCell);

    await waitFor(() =>
      expect(onPlaceShip).toHaveBeenCalledWith({
        ship_type: ShipType.CARRIER,
        row: 0,
        col: 0,
        orientation: 'vertical',
      })
    );
  });

  it('shows an error for invalid out-of-bounds placement', async () => {
    const onPlaceShip = vi.fn().mockResolvedValue({});
    const { container } = render(
      <ShipPlacement
        grid={createGrid()}
        placedShips={[]}
        onPlaceShip={onPlaceShip}
        onConfirm={vi.fn()}
        onMenu={vi.fn()}
      />
    );

    const targetCell = container.querySelectorAll('.cell')[9] as HTMLElement;
    fireEvent.click(targetCell);

    expect(await screen.findByText(/Invalid ship placement!/i)).toBeInTheDocument();
    expect(onPlaceShip).not.toHaveBeenCalled();
  });

  it('does not place ships when component is disabled', () => {
    const onPlaceShip = vi.fn();
    const { container } = render(
      <ShipPlacement
        grid={createGrid()}
        placedShips={[]}
        onPlaceShip={onPlaceShip}
        onConfirm={vi.fn()}
        onMenu={vi.fn()}
        disabled={true}
      />
    );

    const firstCell = container.querySelector('.cell') as HTMLElement;
    fireEvent.click(firstCell);

    expect(onPlaceShip).not.toHaveBeenCalled();
  });
});
