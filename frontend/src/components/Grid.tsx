import React from 'react';
import { CellState } from '../types/game';
import './Grid.css';

interface GridProps {
  grid: CellState[][];
  onCellClick?: (row: number, col: number) => void;
  showShips?: boolean;
  highlightCells?: Array<{ row: number; col: number }>;
  disabled?: boolean;
}

const Grid: React.FC<GridProps> = ({
  grid,
  onCellClick,
  showShips = false,
  highlightCells = [],
  disabled = false,
}) => {
  const getCellClass = (row: number, col: number, cellState: CellState): string => {
    const classes = ['cell'];

    // Add state class
    if (cellState === CellState.HIT) {
      classes.push('hit');
    } else if (cellState === CellState.MISS) {
      classes.push('miss');
    } else if (cellState === CellState.SHIP && showShips) {
      classes.push('ship');
    } else {
      classes.push('empty');
    }

    // Check if cell is highlighted
    if (highlightCells.some(cell => cell.row === row && cell.col === col)) {
      classes.push('highlighted');
    }

    // Add clickable class if not disabled
    if (onCellClick && !disabled) {
      classes.push('clickable');
    }

    return classes.join(' ');
  };

  const handleCellClick = (row: number, col: number) => {
    if (onCellClick && !disabled) {
      onCellClick(row, col);
    }
  };

  return (
    <div className="grid-container">
      <div className="grid-labels">
        <div className="corner-label"></div>
        {[...Array(10)].map((_, i) => (
          <div key={`col-${i}`} className="col-label">
            {i}
          </div>
        ))}
      </div>

      <div className="grid-content">
        <div className="row-labels">
          {[...Array(10)].map((_, i) => (
            <div key={`row-${i}`} className="row-label">
              {i}
            </div>
          ))}
        </div>

        <div className="grid">
          {grid.map((row, rowIndex) => (
            <div key={`row-${rowIndex}`} className="grid-row">
              {row.map((cellState, colIndex) => (
                <div
                  key={`cell-${rowIndex}-${colIndex}`}
                  className={getCellClass(rowIndex, colIndex, cellState)}
                  onClick={() => handleCellClick(rowIndex, colIndex)}
                  title={`(${rowIndex}, ${colIndex})`}
                >
                  {cellState === CellState.HIT && '💥'}
                  {cellState === CellState.MISS && '•'}
                  {cellState === CellState.SHIP && showShips && '🚢'}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Grid;
