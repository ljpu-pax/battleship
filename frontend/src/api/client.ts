import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface GameResponse {
  game_id: string;
  mode: string;
  phase: string;
  current_turn: string;
  player1: {
    name: string;
    grid: string[][];
    ships: any[];
    all_ships_placed: boolean;
    all_ships_sunk: boolean;
  };
  player2: {
    name: string;
    grid: string[][];
    ships: any[];
    all_ships_placed: boolean;
    all_ships_sunk: boolean;
  };
  winner: string | null;
  created_at: string;
}

export interface CreateGameRequest {
  player1_name: string;
  mode: 'ai' | 'multiplayer';
}

export interface PlaceShipRequest {
  ship_type: string;
  row: number;
  col: number;
  orientation: 'horizontal' | 'vertical';
}

export interface FireShotRequest {
  row: number;
  col: number;
}

export const gameAPI = {
  createGame: async (data: CreateGameRequest): Promise<GameResponse> => {
    const response = await api.post('/api/games', data);
    return response.data;
  },

  getGame: async (gameId: string): Promise<GameResponse> => {
    const response = await api.get(`/api/games/${gameId}`);
    return response.data;
  },

  listGames: async (): Promise<GameResponse[]> => {
    const response = await api.get('/api/games');
    return response.data;
  },

  placeShip: async (gameId: string, data: PlaceShipRequest): Promise<any> => {
    const response = await api.post(`/api/games/${gameId}/place-ship`, data);
    return response.data;
  },

  fireShot: async (gameId: string, data: FireShotRequest): Promise<any> => {
    const response = await api.post(`/api/games/${gameId}/fire`, data);
    return response.data;
  },

  deleteGame: async (gameId: string): Promise<void> => {
    await api.delete(`/api/games/${gameId}`);
  },
};
