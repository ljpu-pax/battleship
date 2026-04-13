export const CellState = {
  EMPTY: 'empty',
  SHIP: 'ship',
  HIT: 'hit',
  MISS: 'miss',
} as const;

export type CellState = typeof CellState[keyof typeof CellState];

export const ShipType = {
  CARRIER: 'carrier',
  BATTLESHIP: 'battleship',
  CRUISER: 'cruiser',
  SUBMARINE: 'submarine',
  DESTROYER: 'destroyer',
} as const;

export type ShipType = typeof ShipType[keyof typeof ShipType];

export const SHIP_LENGTHS: Record<ShipType, number> = {
  [ShipType.CARRIER]: 5,
  [ShipType.BATTLESHIP]: 4,
  [ShipType.CRUISER]: 3,
  [ShipType.SUBMARINE]: 3,
  [ShipType.DESTROYER]: 2,
};

export const Orientation = {
  HORIZONTAL: 'horizontal',
  VERTICAL: 'vertical',
} as const;

export type Orientation = typeof Orientation[keyof typeof Orientation];

export const GamePhase = {
  PLACEMENT: 'placement',
  BATTLE: 'battle',
  FINISHED: 'finished',
} as const;

export type GamePhase = typeof GamePhase[keyof typeof GamePhase];

export interface Ship {
  type: string;
  length: number;
  row: number;
  col: number;
  orientation: Orientation;
  hits: number;
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
