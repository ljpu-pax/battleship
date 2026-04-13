import { useEffect, useMemo, useRef, useState } from 'react';
import MainMenu from './components/MainMenu';
import ShipPlacement from './components/ShipPlacement';
import BattlePhase from './components/BattlePhase';
import GameEnd from './components/GameEnd';
import { gameAPI, getWebSocketUrl } from './api/client';
import type {
  FireShotRequest,
  GameHistoryEvent,
  GameReplayResponse,
  PlaceShipRequest,
  PlayerAnalyticsResponse,
} from './api/client';
import { GamePhase, type ShipType } from './types/game';
import type { GameState } from './types/game';
import './App.css';

type AppPhase = 'menu' | 'placement' | 'battle' | 'finished';
type PlayerRole = 'player1' | 'player2';

interface StoredSession {
  gameId: string;
  playerName: string;
  playerRole: PlayerRole;
  mode: 'ai' | 'multiplayer';
}

const STORAGE_KEY = 'battleship-session';

function App() {
  const [inviteGameId, setInviteGameId] = useState('');
  const [appPhase, setAppPhase] = useState<AppPhase>('menu');
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [playerName, setPlayerName] = useState('');
  const [playerRole, setPlayerRole] = useState<PlayerRole>('player1');
  const [historyEvents, setHistoryEvents] = useState<GameHistoryEvent[]>([]);
  const [replayData, setReplayData] = useState<GameReplayResponse | null>(null);
  const [analyticsData, setAnalyticsData] = useState<PlayerAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const websocketRef = useRef<WebSocket | null>(null);

  const currentPlayer = useMemo(() => {
    if (!gameState) {
      return null;
    }
    return playerRole === 'player1' ? gameState.player1 : gameState.player2;
  }, [gameState, playerRole]);

  const placedShips = useMemo(() => {
    if (!currentPlayer) {
      return [];
    }

    return currentPlayer.ships.map((ship) => ship.type.toLowerCase() as ShipType);
  }, [currentPlayer]);

  const winnerName = useMemo(() => {
    if (!gameState?.winner) {
      return null;
    }
    return gameState[gameState.winner as PlayerRole].name;
  }, [gameState]);

  const inviteLink = useMemo(() => {
    if (!gameState || gameState.mode !== 'multiplayer' || playerRole !== 'player1') {
      return '';
    }

    return `${window.location.origin}/?join=${gameState.game_id}`;
  }, [gameState, playerRole]);

  const persistSession = (session: StoredSession | null) => {
    if (session) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  const syncPhase = (nextGameState: GameState) => {
    if (nextGameState.phase === GamePhase.FINISHED) {
      setAppPhase('finished');
    } else if (nextGameState.phase === GamePhase.BATTLE) {
      setAppPhase('battle');
    } else {
      setAppPhase('placement');
    }
  };

  const refreshHistory = async (gameId: string) => {
    try {
      const response = await gameAPI.getHistory(gameId);
      setHistoryEvents(response.events);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  const refreshInsights = async (gameId: string, currentPlayerName: string) => {
    try {
      const [replay, analytics] = await Promise.all([
        gameAPI.getReplay(gameId),
        gameAPI.getAnalytics(currentPlayerName),
      ]);
      setReplayData(replay);
      setAnalyticsData(analytics);
    } catch (error) {
      console.error('Failed to fetch replay/analytics:', error);
    }
  };

  const loadSession = async (session: StoredSession) => {
    const restored = await gameAPI.getGame(session.gameId, session.playerRole);
    setPlayerName(session.playerName);
    setPlayerRole(session.playerRole);
    setGameState(restored as GameState);
    syncPhase(restored as GameState);
    await refreshHistory(session.gameId);
    if ((restored as GameState).phase === GamePhase.FINISHED) {
      await refreshInsights(session.gameId, session.playerName);
    }
    setStatusMessage('Restored previous session.');
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const joinId = params.get('join');
    if (joinId) {
      setInviteGameId(joinId);
    }
  }, []);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return;
    }

    const session = JSON.parse(stored) as StoredSession;
    setLoading(true);
    loadSession(session)
      .catch(() => {
        persistSession(null);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!gameState) {
      return;
    }

    refreshHistory(gameState.game_id);
  }, [gameState?.game_id]);

  useEffect(() => {
    if (!gameState || !playerRole || appPhase === 'finished') {
      return;
    }

    const socket = new WebSocket(getWebSocketUrl(gameState.game_id, playerRole));
    websocketRef.current = socket;

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data) as GameState & { type?: string };
      if (payload.type === 'game_state') {
        setGameState(payload);
        syncPhase(payload);
        refreshHistory(payload.game_id);
      }
    };

    socket.onerror = () => {
      console.error('WebSocket connection error');
    };

    return () => {
      socket.close();
      websocketRef.current = null;
    };
  }, [gameState?.game_id, playerRole, appPhase]);

  const handleCreateGame = async (name: string, mode: 'ai' | 'multiplayer') => {
    setLoading(true);
    setStatusMessage('');
    try {
      const game = await gameAPI.createGame({
        player_name: name,
        mode,
      });

      setPlayerName(name);
      setPlayerRole('player1');
      setGameState(game as GameState);
      syncPhase(game as GameState);
      setReplayData(null);
      setAnalyticsData(null);
      persistSession({
        gameId: game.game_id,
        playerName: name,
        playerRole: 'player1',
        mode,
      });
      await refreshHistory(game.game_id);
      if (mode === 'multiplayer') {
        setStatusMessage(`Room created. Share Game ID: ${game.game_id}`);
      }
    } catch (err) {
      console.error('Failed to create game:', err);
      alert('Failed to create game. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleJoinGame = async (name: string, gameId: string) => {
    setLoading(true);
    setStatusMessage('');
    try {
      const game = await gameAPI.joinGame(gameId, { player_name: name });
      setPlayerName(name);
      setPlayerRole('player2');
    setGameState(game as GameState);
    syncPhase(game as GameState);
    setReplayData(null);
    setAnalyticsData(null);
    persistSession({
        gameId,
        playerName: name,
        playerRole: 'player2',
        mode: 'multiplayer',
      });
      await refreshHistory(gameId);
    } catch (err) {
      console.error('Failed to join game:', err);
      alert('Failed to join game. Please verify the game ID and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePlaceShip = async (request: PlaceShipRequest) => {
    if (!gameState) {
      return;
    }

    const result = await gameAPI.placeShip(gameState.game_id, request, playerRole);
    const updated = await gameAPI.getGame(gameState.game_id, playerRole);
    setGameState(updated as GameState);
    syncPhase(updated as GameState);
    await refreshHistory(gameState.game_id);
    if ((updated as GameState).phase === GamePhase.FINISHED) {
      await refreshInsights(gameState.game_id, playerName);
    }
    return result;
  };

  const handleConfirmPlacement = async () => {
    if (!gameState) {
      return;
    }

    const updated = await gameAPI.getGame(gameState.game_id, playerRole);
    setGameState(updated as GameState);
    syncPhase(updated as GameState);

    if ((updated as GameState).phase === GamePhase.PLACEMENT) {
      setStatusMessage('Waiting for the other player to finish placement.');
    } else {
      setStatusMessage('');
    }
  };

  const handleFireShot = async (request: FireShotRequest) => {
    if (!gameState) {
      return { result: 'error' };
    }

    const result = (await gameAPI.fireShot(gameState.game_id, request, playerRole)) as {
      result: string;
      ship_type?: string;
    };

    const updated = await gameAPI.getGame(gameState.game_id, playerRole);
    setGameState(updated as GameState);
    syncPhase(updated as GameState);
    await refreshHistory(gameState.game_id);
    return result;
  };

  const handleRematch = async () => {
    if (!gameState) {
      return;
    }
    await handleCreateGame(playerName, gameState.mode);
  };

  const handleMenu = () => {
    websocketRef.current?.close();
    setAppPhase('menu');
    setGameState(null);
    setPlayerName('');
    setPlayerRole('player1');
    setHistoryEvents([]);
    setReplayData(null);
    setAnalyticsData(null);
    setStatusMessage('');
    persistSession(null);
  };

  const handleCopyInviteLink = async () => {
    if (!inviteLink) {
      return;
    }

    try {
      await navigator.clipboard.writeText(inviteLink);
      setStatusMessage('Invite link copied to clipboard.');
    } catch (error) {
      console.error('Failed to copy invite link:', error);
      setStatusMessage(`Share this link manually: ${inviteLink}`);
    }
  };

  if (loading) {
    return (
      <div className="app-loading">
        <div className="spinner"></div>
        <p>Loading game...</p>
      </div>
    );
  }

  return (
    <div className="app">
      {appPhase === 'menu' && (
        <MainMenu
          onCreateGame={handleCreateGame}
          onJoinGame={handleJoinGame}
          defaultGameId={inviteGameId}
        />
      )}

      {appPhase === 'placement' && gameState && currentPlayer && (
        <ShipPlacement
          grid={currentPlayer.grid}
          placedShips={placedShips}
          onPlaceShip={handlePlaceShip}
          onConfirm={handleConfirmPlacement}
          helperText={
            statusMessage ||
            (gameState.mode === 'multiplayer'
              ? `Game ID: ${gameState.game_id}`
              : 'Place all five ships to begin.')
          }
        />
      )}

      {appPhase === 'battle' && gameState && (
        <>
          <BattlePhase
            gameState={gameState}
            playerRole={playerRole}
            onFireShot={handleFireShot}
            historyEvents={historyEvents}
          />
          {inviteLink && (
            <div className="app-invite-banner">
              <div>
                <strong>Invite Link:</strong> {inviteLink}
              </div>
              <button className="app-invite-button" onClick={handleCopyInviteLink}>
                Copy Invite Link
              </button>
            </div>
          )}
        </>
      )}

      {appPhase === 'finished' && gameState && winnerName && (
        <GameEnd
          winner={winnerName}
          playerName={playerName}
          replay={replayData}
          analytics={analyticsData}
          onRematch={handleRematch}
          onMenu={handleMenu}
        />
      )}
    </div>
  );
}

export default App;
