import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/react';
import Grid from '../Grid';
import { CellState } from '../../types/game';

describe('Grid Component', () => {
  const mockGrid: CellState[][] = Array(10).fill(null).map(() =>
    Array(10).fill(CellState.EMPTY)
  );

  it('renders 10x10 grid', () => {
    const { container } = render(<Grid grid={mockGrid} showShips={false} />);
    const cells = container.querySelectorAll('.cell');
    expect(cells).toHaveLength(100);
  });

  it('shows ships when showShips is true', () => {
    const gridWithShip = mockGrid.map((row, i) =>
      row.map((cell, j) => (i === 0 && j === 0 ? CellState.SHIP : CellState.EMPTY))
    );

    const { container } = render(<Grid grid={gridWithShip} showShips={true} />);
    const shipCell = container.querySelector('.cell.ship');
    expect(shipCell).toBeInTheDocument();
  });

  it('hides ships when showShips is false', () => {
    const gridWithShip = mockGrid.map((row, i) =>
      row.map((cell, j) => (i === 0 && j === 0 ? CellState.SHIP : CellState.EMPTY))
    );

    const { container } = render(<Grid grid={gridWithShip} showShips={false} />);
    const shipCell = container.querySelector('.cell.ship');
    expect(shipCell).not.toBeInTheDocument();
  });

  it('calls onCellClick when cell is clicked', () => {
    const handleClick = vi.fn();
    const { container } = render(
      <Grid grid={mockGrid} onCellClick={handleClick} showShips={false} />
    );

    const firstCell = container.querySelector('.cell') as HTMLElement;
    fireEvent.click(firstCell);

    expect(handleClick).toHaveBeenCalledWith(0, 0);
  });

  it('does not call onCellClick when disabled', () => {
    const handleClick = vi.fn();
    const { container } = render(
      <Grid grid={mockGrid} onCellClick={handleClick} disabled={true} showShips={false} />
    );

    const firstCell = container.querySelector('.cell') as HTMLElement;
    fireEvent.click(firstCell);

    expect(handleClick).not.toHaveBeenCalled();
  });

  it('highlights cells correctly', () => {
    const { container } = render(
      <Grid
        grid={mockGrid}
        highlightCells={[{ row: 0, col: 0 }, { row: 1, col: 1 }]}
        showShips={false}
      />
    );

    const highlightedCells = container.querySelectorAll('.cell.highlighted');
    expect(highlightedCells).toHaveLength(2);
  });

  it('displays hit marker on hit cells', () => {
    const gridWithHit = mockGrid.map((row, i) =>
      row.map((cell, j) => (i === 0 && j === 0 ? CellState.HIT : CellState.EMPTY))
    );

    const { container } = render(<Grid grid={gridWithHit} showShips={false} />);
    const hitCell = container.querySelector('.cell.hit');
    expect(hitCell).toBeInTheDocument();
    expect(hitCell?.textContent).toBe('💥');
  });

  it('displays miss marker on miss cells', () => {
    const gridWithMiss = mockGrid.map((row, i) =>
      row.map((cell, j) => (i === 0 && j === 0 ? CellState.MISS : CellState.EMPTY))
    );

    const { container } = render(<Grid grid={gridWithMiss} showShips={false} />);
    const missCell = container.querySelector('.cell.miss');
    expect(missCell).toBeInTheDocument();
    expect(missCell?.textContent).toBe('•');
  });
});
