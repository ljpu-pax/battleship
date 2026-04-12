export enum CellState {
  EMPTY = 'empty',
  SHIP = 'ship',
  HIT = 'hit',
  MISS = 'miss',
}

export enum ShipType {
  CARRIER = 'carrier',
  BATTLESHIP = 'battleship',
  CRUISER = 'cruiser',
  SUBMARINE = 'submarine',
  DESTROYER = 'destroyer',
}

export const SHIP_LENGTHS: Record<ShipType, number> = {
  [ShipType.CARRIER]: 5,
  [ShipType.BATTLESHIP]: 4,
  [ShipType.CRUISER]: 3,
  [ShipType.SUBMARINE]: 3,
  [ShipType.DESTROYER]: 2,
};

export enum Orientation {
  HORIZONTAL = 'horizontal',
  VERTICAL = 'vertical',
}

export enum GamePhase {
  PLACEMENT = 'placement',
  BATTLE = 'battle',
  FINISHED = 'finished',
}

export interface Ship {
  ship_type: ShipType;
  row: number;
  col: number;
  orientation: Orientation;
  is_sunk: boolean;
}

export interface Player {
  name: string;
  grid: CellState[][];
  ships: Ship[];
  all_ships_placed: boolean;
  all_ships_sunk: boolean;
}

export interface GameState {
  game_id: string;
  mode: 'ai' | 'multiplayer';
  phase: GamePhase;
  current_turn: string;
  player1: Player;
  player2: Player;
  winner: string | null;
  created_at: string;
}

export interface ShotResult {
  result: 'hit' | 'miss' | 'sunk';
  ship_type?: ShipType;
  row: number;
  col: number;
}
