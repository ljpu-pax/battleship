import { useState, useEffect } from 'react';
import MainMenu from './components/MainMenu';
import ShipPlacement from './components/ShipPlacement';
import BattlePhase from './components/BattlePhase';
import GameEnd from './components/GameEnd';
import { gameAPI, PlaceShipRequest, FireShotRequest } from './api/client';
import { GameState, GamePhase, ShipType, CellState } from './types/game';
import './App.css';

type AppPhase = 'menu' | 'placement' | 'battle' | 'finished';

function App() {
  const [appPhase, setAppPhase] = useState<AppPhase>('menu');
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [playerName, setPlayerName] = useState<string>('');
  const [placedShips, setPlacedShips] = useState<ShipType[]>([]);
  const [loading, setLoading] = useState(false);
  const [pollingInterval, setPollingInterval] = useState<number | null>(null);

  // Poll game state for AI and multiplayer modes
  useEffect(() => {
    if (gameState && appPhase === 'battle') {
      const interval = window.setInterval(async () => {
        try {
          const updated = await gameAPI.getGame(gameState.game_id);
          setGameState(updated);

          if (updated.phase === GamePhase.FINISHED) {
            setAppPhase('finished');
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Failed to poll game state:', err);
        }
      }, 1000);

      setPollingInterval(interval);

      return () => {
        clearInterval(interval);
      };
    }
  }, [gameState?.game_id, appPhase]);

  const handleStartGame = async (name: string, mode: 'ai' | 'multiplayer') => {
    setLoading(true);
    try {
      const game = await gameAPI.createGame({
        player1_name: name,
        mode,
      });

      setPlayerName(name);
      setGameState(game);
      setAppPhase('placement');
      setPlacedShips([]);
    } catch (err) {
      console.error('Failed to create game:', err);
      alert('Failed to create game. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePlaceShip = async (request: PlaceShipRequest) => {
    if (!gameState) return;

    const result = await gameAPI.placeShip(gameState.game_id, request);

    // Update game state
    const updated = await gameAPI.getGame(gameState.game_id);
    setGameState(updated);
    setPlacedShips([...placedShips, request.ship_type as ShipType]);

    return result;
  };

  const handleConfirmPlacement = async () => {
    if (!gameState) return;

    // Fetch latest state
    const updated = await gameAPI.getGame(gameState.game_id);
    setGameState(updated);

    // Check if we can start battle
    if (updated.phase === GamePhase.BATTLE || updated.player1.all_ships_placed) {
      setAppPhase('battle');
    }
  };

  const handleFireShot = async (request: FireShotRequest) => {
    if (!gameState) return;

    const result = await gameAPI.fireShot(gameState.game_id, request);

    // Update game state
    const updated = await gameAPI.getGame(gameState.game_id);
    setGameState(updated);

    if (updated.phase === GamePhase.FINISHED) {
      setAppPhase('finished');
    }

    return result;
  };

  const handleRematch = async () => {
    if (!gameState) return;

    // Create new game with same settings
    await handleStartGame(playerName, gameState.mode);
  };

  const handleMenu = () => {
    if (gameState && pollingInterval) {
      clearInterval(pollingInterval);
    }
    setAppPhase('menu');
    setGameState(null);
    setPlayerName('');
    setPlacedShips([]);
  };

  if (loading) {
    return (
      <div className="app-loading">
        <div className="spinner"></div>
        <p>Creating game...</p>
      </div>
    );
  }

  return (
    <div className="app">
      {appPhase === 'menu' && (
        <MainMenu onStartGame={handleStartGame} />
      )}

      {appPhase === 'placement' && gameState && (
        <ShipPlacement
          grid={gameState.player1.name === playerName ? gameState.player1.grid as any : gameState.player2.grid as any}
          placedShips={placedShips}
          onPlaceShip={handlePlaceShip}
          onConfirm={handleConfirmPlacement}
        />
      )}

      {appPhase === 'battle' && gameState && (
        <BattlePhase
          gameState={gameState}
          playerName={playerName}
          onFireShot={handleFireShot}
        />
      )}

      {appPhase === 'finished' && gameState && gameState.winner && (
        <GameEnd
          winner={gameState.winner}
          playerName={playerName}
          onRematch={handleRematch}
          onMenu={handleMenu}
        />
      )}
    </div>
  );
}

export default App;
