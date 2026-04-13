import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

interface PlayerData {
  name: string;
  grid: string[][];
  ships: Array<{
    type: string;
    length: number;
    row: number;
    col: number;
    orientation: 'horizontal' | 'vertical';
    hits: number;
    is_sunk: boolean;
  }>;
  all_ships_placed: boolean;
  all_ships_sunk: boolean;
}

export interface GameResponse {
  game_id: string;
  mode: 'ai' | 'multiplayer';
  phase: string;
  current_turn: string;
  player1: PlayerData;
  player2: PlayerData;
  winner: string | null;
  created_at: string;
}

export interface CreateGameRequest {
  player_name: string;
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

export interface JoinGameRequest {
  player_name: string;
}

export interface GameHistoryEvent {
  event_type: string;
  player: string | null;
  created_at: string;
  row?: number;
  col?: number;
  result?: string;
  ship_sunk?: string | null;
  ship_type?: string;
  orientation?: string;
  player_name?: string;
  winner?: string | null;
}

export interface ReplayStep {
  turn_number: number;
  player: string;
  row: number;
  col: number;
  result: string;
  ship_sunk?: string | null;
  winner?: string | null;
  created_at: string;
}

export interface GameReplayResponse {
  game_id: string;
  steps: ReplayStep[];
  summary: {
    total_turns: number;
    player1_hits: number;
    player2_hits: number;
  };
}

export interface PlayerAnalyticsResponse {
  player_name: string;
  games_played: number;
  wins: number;
  losses: number;
  active_games: number;
  win_rate: number;
  hit_rate: number;
  average_turns_per_game: number;
  recent_games: Array<{
    game_id: string;
    mode: string;
    phase: string;
    winner: string | null;
    turns: number;
    hit_rate: number;
    updated_at: string;
  }>;
}

const withPlayerParam = (player?: 'player1' | 'player2') =>
  player ? { params: { player } } : undefined;

export const getWebSocketUrl = (gameId: string, player: 'player1' | 'player2') => {
  const base = API_BASE_URL.replace(/^http/, 'ws');
  return `${base}/ws/games/${gameId}?player=${player}`;
};

export const gameAPI = {
  createGame: async (data: CreateGameRequest): Promise<GameResponse> => {
    const response = await api.post('/api/games', data);
    return response.data;
  },

  joinGame: async (gameId: string, data: JoinGameRequest): Promise<GameResponse> => {
    const response = await api.post(`/api/games/${gameId}/join`, data);
    return response.data;
  },

  getGame: async (gameId: string, player?: 'player1' | 'player2'): Promise<GameResponse> => {
    const response = await api.get(`/api/games/${gameId}`, withPlayerParam(player));
    return response.data;
  },

  listGames: async (): Promise<GameResponse[]> => {
    const response = await api.get('/api/games');
    return response.data;
  },

  placeShip: async (
    gameId: string,
    data: PlaceShipRequest,
    player?: 'player1' | 'player2'
  ): Promise<unknown> => {
    const response = await api.post(`/api/games/${gameId}/place-ship`, data, withPlayerParam(player));
    return response.data;
  },

  fireShot: async (
    gameId: string,
    data: FireShotRequest,
    player?: 'player1' | 'player2'
  ): Promise<unknown> => {
    const response = await api.post(`/api/games/${gameId}/fire`, data, withPlayerParam(player));
    return response.data;
  },

  getHistory: async (gameId: string): Promise<{ game_id: string; events: GameHistoryEvent[] }> => {
    const response = await api.get(`/api/games/${gameId}/history`);
    return response.data;
  },

  getReplay: async (gameId: string): Promise<GameReplayResponse> => {
    const response = await api.get(`/api/games/${gameId}/replay`);
    return response.data;
  },

  getAnalytics: async (playerName: string): Promise<PlayerAnalyticsResponse> => {
    const response = await api.get(`/api/players/${encodeURIComponent(playerName)}/analytics`);
    return response.data;
  },

  deleteGame: async (gameId: string): Promise<void> => {
    await api.delete(`/api/games/${gameId}`);
  },
};
