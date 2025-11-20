import React, { useState, useEffect } from 'react';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import axios from 'axios';
import './App.css';
import GameAnalysis from './GameAnalysis';
import { lightTheme, darkTheme, applyTheme } from './theme';
import BarChartIcon from '@mui/icons-material/BarChart';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';

const API_URL = 'http://localhost:5000/api';

function App() {
  const [mode, setMode] = useState('play'); // 'play' or 'analyze'
  const [game, setGame] = useState(new Chess());
  const [evaluation, setEvaluation] = useState(0);
  const [bestMoves, setBestMoves] = useState([]);
  const [moveHistory, setMoveHistory] = useState([]);
  const [currentMoveIndex, setCurrentMoveIndex] = useState(-1);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [depth, setDepth] = useState(18);
  const [selectedSquare, setSelectedSquare] = useState(null);
  const [highlightedSquares, setHighlightedSquares] = useState({});
  const [isDarkTheme, setIsDarkTheme] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });

  useEffect(() => {
    applyTheme(isDarkTheme ? darkTheme : lightTheme);
    localStorage.setItem('theme', isDarkTheme ? 'dark' : 'light');
  }, [isDarkTheme]);

  useEffect(() => {
    analyzePosition(game.fen());
  }, []);

  const analyzePosition = async (fen) => {
    setIsAnalyzing(true);
    try {
      const response = await axios.post(`${API_URL}/analyze-position`, {
        fen: fen,
        depth: depth
      });
      
      if (response.data.success) {
        setEvaluation(response.data.evaluation);
        setBestMoves(response.data.bestMoves);
      }
    } catch (error) {
      console.error('Analysis error:', error);
    }
    setIsAnalyzing(false);
  };

  const onDrop = (sourceSquare, targetSquare) => {
    try {
      const gameCopy = new Chess(game.fen());
      const move = gameCopy.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: 'q'
      });

      if (move === null) return false;

      setGame(gameCopy);
      
      const newHistory = [...moveHistory, {
        move: move.san,
        fen: gameCopy.fen(),
        from: sourceSquare,
        to: targetSquare
      }];
      setMoveHistory(newHistory);
      setCurrentMoveIndex(newHistory.length - 1);
      
      analyzePosition(gameCopy.fen());
      setSelectedSquare(null);
      setHighlightedSquares({});
      
      return true;
    } catch (error) {
      return false;
    }
  };

  const onSquareClick = (square) => {
    if (selectedSquare === square) {
      setSelectedSquare(null);
      setHighlightedSquares({});
      return;
    }

    const piece = game.get(square);
    if (piece && piece.color === game.turn()) {
      setSelectedSquare(square);
      
      const moves = game.moves({ square, verbose: true });
      const highlights = {};
      moves.forEach(move => {
        highlights[move.to] = {
          background: 'radial-gradient(circle, rgba(0,255,0,0.3) 25%, transparent 25%)',
          borderRadius: '50%'
        };
      });
      setHighlightedSquares(highlights);
    } else if (selectedSquare) {
      onDrop(selectedSquare, square);
    }
  };

  const goToMove = (index) => {
    if (index === -1) {
      setGame(new Chess());
      setCurrentMoveIndex(-1);
    } else if (index >= 0 && index < moveHistory.length) {
      setGame(new Chess(moveHistory[index].fen));
      setCurrentMoveIndex(index);
    }
    analyzePosition(index === -1 ? new Chess().fen() : moveHistory[index].fen);
  };

  const resetGame = () => {
    const newGame = new Chess();
    setGame(newGame);
    setMoveHistory([]);
    setCurrentMoveIndex(-1);
    setSelectedSquare(null);
    setHighlightedSquares({});
    analyzePosition(newGame.fen());
  };

  const formatEvaluation = (score) => {
    if (score === null || score === undefined) return '0.00';
    if (Math.abs(score) >= 1000) {
      const mateIn = Math.floor(10000 / Math.abs(score));
      return score > 0 ? `M${mateIn}` : `-M${mateIn}`;
    }
    return (score / 100).toFixed(2);
  };

  const getEvaluationBar = () => {
    const normalized = Math.max(-10, Math.min(10, evaluation / 100));
    const percentage = ((normalized + 10) / 20) * 100;
    return percentage;
  };

  if (mode === 'analyze') {
    return <GameAnalysis onBack={() => setMode('play')} isDarkTheme={isDarkTheme} setIsDarkTheme={setIsDarkTheme} />;
  }

  return (
    <div className="App">
      <div className="header">
        <h1>Chess Engine Interface</h1>
        <div className="controls">
          <button onClick={() => setMode('analyze')} className="mode-button">
            <BarChartIcon style={{ marginRight: '8px' }} />
            Analyze Game
          </button>
          <button onClick={resetGame}>New Game</button>
          <label>
            Depth:
            <input 
              type="number" 
              value={depth} 
              onChange={(e) => setDepth(parseInt(e.target.value))}
              min="1"
              max="30"
            />
          </label>
          <button 
            onClick={() => setIsDarkTheme(!isDarkTheme)} 
            className="theme-toggle"
            title={isDarkTheme ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
          >
            {isDarkTheme ? <Brightness7Icon /> : <Brightness4Icon />}
          </button>
        </div>
      </div>

      <div className="main-container">
        <div className="board-section">
          <div className="board-container">
            <div className="player-info">
              <div className="player-name">Black</div>
            </div>
            
            <div className="board-wrapper">
              <Chessboard
                position={game.fen()}
                onPieceDrop={onDrop}
                onSquareClick={onSquareClick}
                customSquareStyles={{
                  ...highlightedSquares,
                  ...(selectedSquare && {
                    [selectedSquare]: { backgroundColor: 'rgba(255, 255, 0, 0.4)' }
                  })
                }}
                boardWidth={560}
              />
            </div>

            <div className="player-info">
              <div className="player-name">White</div>
            </div>
          </div>

          <div className="eval-bar-container">
            <div className="eval-label">Evaluation</div>
            <div className="eval-bar">
              <div 
                className="eval-bar-white" 
                style={{ height: `${getEvaluationBar()}%` }}
              />
              <div className="eval-text">
                {formatEvaluation(evaluation)}
              </div>
            </div>
          </div>
        </div>

        <div className="analysis-panel">
          <div className="evaluation-section">
            <h3>Best Moves</h3>
            
            {isAnalyzing && <div className="analyzing">Analyzing position...</div>}
            
            <div className="best-moves">
              {bestMoves.slice(0, 3).map((move, idx) => (
                <div key={idx} className="best-move-item">
                  <span className="move-number">{idx + 1}</span>
                  <span className="move-san">{move.san}</span>
                  <span className="move-eval">{formatEvaluation(move.score)}</span>
                </div>
              ))}
              {bestMoves.length === 0 && !isAnalyzing && (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>
                  No moves available
                </div>
              )}
            </div>
          </div>

          <div className="moves-section">
            <h3>Moves</h3>
            <div className="moves-list">
              <div 
                className={`move-item ${currentMoveIndex === -1 ? 'active' : ''}`}
                onClick={() => goToMove(-1)}
              >
                Starting Position
              </div>
              {moveHistory.map((item, idx) => (
                <div 
                  key={idx}
                  className={`move-item ${currentMoveIndex === idx ? 'active' : ''}`}
                  onClick={() => goToMove(idx)}
                >
                  <span className="move-number">
                    {Math.floor(idx / 2) + 1}{idx % 2 === 0 ? '.' : '...'}
                  </span>
                  <span className="move-text">{item.move}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="navigation-buttons">
            <button onClick={() => goToMove(currentMoveIndex - 1)} disabled={currentMoveIndex <= -1}>
              ◀ Previous
            </button>
            <button onClick={() => goToMove(currentMoveIndex + 1)} disabled={currentMoveIndex >= moveHistory.length - 1}>
              Next ▶
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
