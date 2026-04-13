import React, { useState } from 'react';
import Grid from './Grid';
import { ShipType, SHIP_LENGTHS, Orientation, CellState } from '../types/game';
import type { PlaceShipRequest } from '../api/client';
import './ShipPlacement.css';

interface ShipPlacementProps {
  grid: CellState[][];
  placedShips: ShipType[];
  onPlaceShip: (request: PlaceShipRequest) => Promise<unknown>;
  onConfirm: () => void;
  title?: string;
  helperText?: string;
  disabled?: boolean;
}

const SHIPS_TO_PLACE = [
  ShipType.CARRIER,
  ShipType.BATTLESHIP,
  ShipType.CRUISER,
  ShipType.SUBMARINE,
  ShipType.DESTROYER,
];

const ShipPlacement: React.FC<ShipPlacementProps> = ({
  grid,
  placedShips,
  onPlaceShip,
  onConfirm,
  title = 'Place Your Ships',
  helperText,
  disabled = false,
}) => {
  const [selectedShip, setSelectedShip] = useState<ShipType | null>(SHIPS_TO_PLACE[0]);
  const [orientation, setOrientation] = useState<Orientation>(Orientation.HORIZONTAL);
  const [error, setError] = useState<string>('');

  const getShipCells = (row: number, col: number, ship: ShipType, orient: Orientation) => {
    const length = SHIP_LENGTHS[ship];
    const cells = [];

    for (let i = 0; i < length; i++) {
      if (orient === Orientation.HORIZONTAL) {
        cells.push({ row, col: col + i });
      } else {
        cells.push({ row: row + i, col });
      }
    }

    return cells;
  };

  const isValidPlacement = (row: number, col: number, ship: ShipType, orient: Orientation): boolean => {
    const cells = getShipCells(row, col, ship, orient);

    // Check bounds
    for (const cell of cells) {
      if (cell.row < 0 || cell.row >= 10 || cell.col < 0 || cell.col >= 10) {
        return false;
      }
    }

    // Check overlaps
    for (const cell of cells) {
      if (grid[cell.row][cell.col] === CellState.SHIP) {
        return false;
      }
    }

    return true;
  };

  const handleCellClick = async (row: number, col: number) => {
    if (!selectedShip || placedShips.includes(selectedShip) || disabled) {
      return;
    }

    if (!isValidPlacement(row, col, selectedShip, orientation)) {
      setError('Invalid ship placement! Check bounds and overlaps.');
      setTimeout(() => setError(''), 3000);
      return;
    }

    try {
      await onPlaceShip({
        ship_type: selectedShip,
        row,
        col,
        orientation,
      });

      setError('');

      // Auto-select next ship
      const nextShip = SHIPS_TO_PLACE.find(ship => !placedShips.includes(ship) && ship !== selectedShip);
      setSelectedShip(nextShip || null);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to place ship');
      setTimeout(() => setError(''), 3000);
    }
  };

  const toggleOrientation = () => {
    setOrientation(orientation === Orientation.HORIZONTAL ? Orientation.VERTICAL : Orientation.HORIZONTAL);
  };

  const allShipsPlaced = placedShips.length === SHIPS_TO_PLACE.length;

  return (
    <div className="ship-placement">
      <h2>{title}</h2>
      {helperText && <p className="placement-helper">{helperText}</p>}

      <div className="placement-container">
        <div className="placement-grid">
          <Grid
            grid={grid}
            onCellClick={handleCellClick}
            showShips={true}
            disabled={disabled || allShipsPlaced}
          />
        </div>

        <div className="placement-controls">
          <div className="ship-list">
            <h3>Ships to Place:</h3>
            {SHIPS_TO_PLACE.map((ship) => {
              const isPlaced = placedShips.includes(ship);
              const isSelected = selectedShip === ship;

              return (
                <button
                  key={ship}
                  className={`ship-button ${isPlaced ? 'placed' : ''} ${isSelected ? 'selected' : ''}`}
                  onClick={() => !isPlaced && setSelectedShip(ship)}
                  disabled={isPlaced || disabled}
                >
                  <span className="ship-name">{ship}</span>
                  <span className="ship-length">({SHIP_LENGTHS[ship]} cells)</span>
                  {isPlaced && <span className="check-mark">✓</span>}
                </button>
              );
            })}
          </div>

          <div className="orientation-control">
            <button
              className="orientation-button"
              onClick={toggleOrientation}
              disabled={!selectedShip || placedShips.includes(selectedShip!) || disabled}
            >
              <div className="orientation-icon">
                {orientation === Orientation.HORIZONTAL ? '→' : '↓'}
              </div>
              <div>Orientation: {orientation}</div>
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            className="confirm-button"
            onClick={onConfirm}
            disabled={!allShipsPlaced || disabled}
          >
            {allShipsPlaced ? 'Confirm Placement ✓' : `${placedShips.length}/5 Ships Placed`}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ShipPlacement;
