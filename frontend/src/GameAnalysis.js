import React, { useState, useEffect } from 'react';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import axios from 'axios';
import VoiceChat from './VoiceChat';
import './GameAnalysis.css';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import FlipIcon from '@mui/icons-material/Flip';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';

const API_URL = 'http://localhost:5000/api';

function GameAnalysis({ isDarkTheme, setIsDarkTheme }) {
  const [pgn, setPgn] = useState('');
  const [targetPlayer, setTargetPlayer] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentMoveIndex, setCurrentMoveIndex] = useState(0);
  const [game, setGame] = useState(new Chess());
  const [showBestMove, setShowBestMove] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [boardOrientation, setBoardOrientation] = useState('white');

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (!analysisResult) return;

      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        goToMove(Math.max(0, currentMoveIndex - 1));
      } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        goToMove(Math.min(analysisResult.moves.length - 1, currentMoveIndex + 1));
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [analysisResult, currentMoveIndex]);

  const analyzeGame = async () => {
    if (!pgn.trim()) {
      alert('Please paste a PGN');
      return;
    }

    setIsAnalyzing(true);
    try {
      const response = await axios.post(`${API_URL}/analyze-game`, {
        pgn: pgn,
        targetPlayer: targetPlayer,
        depth: 18
      });

      if (response.data.success) {
        setAnalysisResult(response.data);
        setCurrentMoveIndex(0);
        setGame(new Chess());
        // Set initial board orientation based on target player color
        setBoardOrientation(response.data.gameInfo.targetColor === 'black' ? 'black' : 'white');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Error analyzing game: ' + (error.response?.data?.error || error.message));
    }
    setIsAnalyzing(false);
  };

  const goToMove = (index) => {
    if (!analysisResult || index < 0) return;
    
    const newGame = new Chess();
    for (let i = 0; i <= index; i++) {
      const move = analysisResult.moves[i];
      try {
        newGame.move({ from: move.move.substring(0, 2), to: move.move.substring(2, 4), promotion: 'q' });
      } catch (e) {
        console.error('Error making move:', move.move, e);
      }
    }
    
    setGame(newGame);
    setCurrentMoveIndex(index);
  };

  const formatEvaluation = (score) => {
    if (score === null || score === undefined) return '0.00';
    if (Math.abs(score) >= 1000) {
      const mateIn = Math.floor(10000 / Math.abs(score));
      return score > 0 ? `M${mateIn}` : `-M${mateIn}`;
    }
    return (score / 100).toFixed(2);
  };

  const getQualityColor = (quality) => {
    const colors = {
      'Excellent': '#22c55e',
      'Good': '#84cc16',
      'Inaccuracy': '#eab308',
      'Mistake': '#f97316',
      'Blunder': '#ef4444',
      'Severe Blunder': '#dc2626'
    };
    return colors[quality] || '#888';
  };

  const getCurrentMove = () => {
    if (!analysisResult || currentMoveIndex < 0) return null;
    return analysisResult.moves[currentMoveIndex];
  };

  const renderBoardComparison = () => {
    const currentMove = getCurrentMove();
    if (!currentMove) return null;

    const boardAfter = new Chess(currentMove.fen);
    
    let boardBest = new Chess(currentMove.fenBefore);
    if (currentMove.bestMove && currentMove.bestMove !== currentMove.move) {
      boardBest.move({ 
        from: currentMove.bestMove.substring(0, 2), 
        to: currentMove.bestMove.substring(2, 4) 
      });
    } else {
      boardBest = boardAfter;
    }

    // Create arrow for your move (blue)
    const yourMoveArrow = [[
      currentMove.move.substring(0, 2),
      currentMove.move.substring(2, 4),
      'rgba(74, 158, 255, 0.8)'
    ]];

    // Create arrow for best move (green)
    const bestMoveArrow = currentMove.bestMove ? [[
      currentMove.bestMove.substring(0, 2),
      currentMove.bestMove.substring(2, 4),
      'rgba(34, 197, 94, 0.8)'
    ]] : yourMoveArrow;

    return (
      <div className="board-comparison">
        <div className="board-column">
          <h3 className="board-title" style={{ color: '#4a9eff' }}>Your Move</h3>
          <Chessboard
            position={currentMove.fenBefore}
            boardWidth={350}
            arePiecesDraggable={false}
            boardOrientation={boardOrientation}
            customArrows={yourMoveArrow}
          />
          <div className="move-info">
            <span className="move-label">Played:</span>
            <span className="move-value">{currentMove.san}</span>
          </div>
        </div>
        
        <div className="board-column">
          <h3 className="board-title" style={{ color: '#22c55e' }}>Best Move</h3>
          <Chessboard
            position={currentMove.fenBefore}
            boardWidth={350}
            arePiecesDraggable={false}
            boardOrientation={boardOrientation}
            customArrows={bestMoveArrow}
          />
          <div className="move-info">
            <span className="move-label">Best:</span>
            <span className="move-value">{currentMove.bestMoveSan || currentMove.san}</span>
          </div>
        </div>
      </div>
    );
  };

  const renderEvaluationGraph = () => {
    if (!analysisResult) return null;

    const moves = analysisResult.moves;
    const maxEval = 500; // Cap at +5.00 / -5.00
    
    return (
      <div className="evaluation-graph">
        <svg width="100%" height="120" viewBox="0 0 800 120" preserveAspectRatio="none">
          {/* Background - neutral gray */}
          <rect x="0" y="0" width="800" height="120" fill="#2a2a2a" />
          
          {/* Black advantage area - fill from evaluation line to TOP */}
          <path
            d={`M 0,0 L 0,${60 - ((moves[0].evalAfter || 0) / maxEval) * 60} ${moves.map((move, idx) => {
              const x = (idx / (moves.length - 1)) * 800;
              const eval_cp = move.evalAfter || 0;
              const clamped = Math.max(-maxEval, Math.min(maxEval, eval_cp));
              const y = 60 - (clamped / maxEval) * 60;
              return `L ${x},${y}`;
            }).join(' ')} L 800,0 Z`}
            fill="#1a1a1a"
          />
          
          {/* White advantage area - fill from evaluation line to BOTTOM */}
          <path
            d={`M 0,120 L 0,${60 - ((moves[0].evalAfter || 0) / maxEval) * 60} ${moves.map((move, idx) => {
              const x = (idx / (moves.length - 1)) * 800;
              const eval_cp = move.evalAfter || 0;
              const clamped = Math.max(-maxEval, Math.min(maxEval, eval_cp));
              const y = 60 - (clamped / maxEval) * 60;
              return `L ${x},${y}`;
            }).join(' ')} L 800,120 Z`}
            fill="#e8e8e8"
          />
          
          {/* Center line (equal position) */}
          <line x1="0" y1="60" x2="800" y2="60" stroke="#666" strokeWidth="1.5" strokeDasharray="5,5" />
          
          {/* Evaluation line */}
          <polyline
            points={moves.map((move, idx) => {
              const x = (idx / (moves.length - 1)) * 800;
              const eval_cp = move.evalAfter || 0;
              const clamped = Math.max(-maxEval, Math.min(maxEval, eval_cp));
              const y = 60 - (clamped / maxEval) * 60;
              return `${x},${y}`;
            }).join(' ')}
            fill="none"
            stroke="#4a9eff"
            strokeWidth="3"
            strokeLinejoin="round"
            strokeLinecap="round"
          />
          
          {/* Move quality markers */}
          {moves.filter(m => m.isTarget && m.cpLoss > 50).map((move) => {
            const moveIdx = moves.indexOf(move);
            const x = (moveIdx / (moves.length - 1)) * 800;
            const eval_cp = move.evalAfter || 0;
            const clamped = Math.max(-maxEval, Math.min(maxEval, eval_cp));
            const y = 60 - (clamped / maxEval) * 60;
            
            let color = '#eab308'; // inaccuracy
            if (move.cpLoss > 300) color = '#dc2626'; // severe blunder
            else if (move.cpLoss > 100) color = '#ef4444'; // blunder
            else if (move.cpLoss > 50) color = '#f97316'; // mistake
            
            return (
              <circle
                key={moveIdx}
                cx={x}
                cy={y}
                r="5"
                fill={color}
                stroke="white"
                strokeWidth="2"
              />
            );
          })}
        </svg>
        <div className="graph-labels">
          <div className="label-side">
            <span className="label-white">⬆ White Advantage (Top)</span>
          </div>
          <div className="label-side">
            <span className="label-black">⬇ Black Advantage (Bottom)</span>
          </div>
        </div>
      </div>
    );
  };

  const renderStatistics = () => {
    if (!analysisResult) return null;

    const { gameInfo, statistics } = analysisResult;
    const targetStats = statistics[gameInfo.targetColor];
    const opponentStats = statistics[gameInfo.targetColor === 'white' ? 'black' : 'white'];

    return (
      <div className={`statistics-panel ${isMinimized ? 'minimized' : ''}`}>
        <div className="game-header">
          <div className="header-top">
            <h2>Game Analysis</h2>
            <div className="header-buttons">
              <button 
                className="theme-toggle" 
                onClick={() => setIsDarkTheme(!isDarkTheme)}
                title={isDarkTheme ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
              >
                {isDarkTheme ? <Brightness7Icon /> : <Brightness4Icon />}
              </button>
              <button 
                className="flip-button" 
                onClick={() => setBoardOrientation(boardOrientation === 'white' ? 'black' : 'white')}
                title="Flip Board"
              >
                <FlipIcon />
              </button>
              <button 
                className="minimize-button" 
                onClick={() => setIsMinimized(!isMinimized)}
                title={isMinimized ? "Expand" : "Minimize"}
              >
                {isMinimized ? <ExpandMoreIcon /> : <ExpandLessIcon />}
              </button>
            </div>
          </div>
          <div className="players-info">
            <div className={`player-card ${gameInfo.targetColor === 'white' ? 'target-player' : ''}`}>
              <div className="player-name">{gameInfo.white}</div>
              <div className="player-rating">Rating: {gameInfo.whiteElo}</div>
              {gameInfo.targetColor === 'white' && (
                <>
                  <div className="target-badge">YOU</div>
                  <div className="performance-rating-badge">
                    Performance: {statistics.performanceRating}
                  </div>
                </>
              )}
            </div>
            <div className="vs">vs</div>
            <div className={`player-card ${gameInfo.targetColor === 'black' ? 'target-player' : ''}`}>
              <div className="player-name">{gameInfo.black}</div>
              <div className="player-rating">Rating: {gameInfo.blackElo}</div>
              {gameInfo.targetColor === 'black' && (
                <>
                  <div className="target-badge">YOU</div>
                  <div className="performance-rating-badge">
                    Performance: {statistics.performanceRating}
                  </div>
                </>
              )}
            </div>
          </div>
          <div className="game-result">
            Result: <strong>{gameInfo.result}</strong>
          </div>
        </div>

        {renderEvaluationGraph()}

        <div className="stats-grid">
          <div className="stat-card highlight">
            <h3>Your Performance</h3>
            <div className="big-stat">{targetStats.accuracy}%</div>
            <div className="stat-label">Accuracy</div>
            <div className="performance-rating">
              Performance Rating: <strong>{statistics.performanceRating}</strong>
            </div>
          </div>

          <div className="stat-card">
            <h3>Opponent Performance</h3>
            <div className="big-stat">{opponentStats.accuracy}%</div>
            <div className="stat-label">Accuracy</div>
          </div>
        </div>

        <div className="phase-accuracy">
          <h3>Accuracy by Phase</h3>
          <div className="phase-bars">
            <div className="phase-bar">
              <div className="phase-label">Opening ({statistics.phaseAccuracy.openingMoves} moves)</div>
              <div className="bar-container">
                <div className="bar-fill" style={{ width: `${statistics.phaseAccuracy.opening}%` }}>
                  {statistics.phaseAccuracy.opening}%
                </div>
              </div>
            </div>
            <div className="phase-bar">
              <div className="phase-label">Middlegame ({statistics.phaseAccuracy.middlegameMoves} moves)</div>
              <div className="bar-container">
                <div className="bar-fill" style={{ width: `${statistics.phaseAccuracy.middlegame}%` }}>
                  {statistics.phaseAccuracy.middlegame}%
                </div>
              </div>
            </div>
            <div className="phase-bar">
              <div className="phase-label">Endgame ({statistics.phaseAccuracy.endgameMoves} moves)</div>
              <div className="bar-container">
                <div className="bar-fill" style={{ width: `${statistics.phaseAccuracy.endgame}%` }}>
                  {statistics.phaseAccuracy.endgame}%
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="move-quality-breakdown">
          <h3>Your Move Quality</h3>
          <div className="quality-grid">
            <div className="quality-item">
              <div className="quality-count" style={{ color: '#22c55e' }}>{targetStats.excellent}</div>
              <div className="quality-label">Excellent</div>
            </div>
            <div className="quality-item">
              <div className="quality-count" style={{ color: '#84cc16' }}>{targetStats.good}</div>
              <div className="quality-label">Good</div>
            </div>
            <div className="quality-item">
              <div className="quality-count" style={{ color: '#eab308' }}>{targetStats.inaccuracies}</div>
              <div className="quality-label">Inaccuracies</div>
            </div>
            <div className="quality-item">
              <div className="quality-count" style={{ color: '#f97316' }}>{targetStats.mistakes}</div>
              <div className="quality-label">Mistakes</div>
            </div>
            <div className="quality-item">
              <div className="quality-count" style={{ color: '#ef4444' }}>{targetStats.blunders}</div>
              <div className="quality-label">Blunders</div>
            </div>
            <div className="quality-item">
              <div className="quality-count" style={{ color: '#dc2626' }}>{targetStats.severeBlunders}</div>
              <div className="quality-label">Severe</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderMovesList = () => {
    if (!analysisResult) return null;

    const currentMove = getCurrentMove();

    return (
      <div className="moves-analysis-list">
        <h3>Move-by-Move Analysis</h3>
        <div className="moves-scroll">
          {analysisResult.moves.map((move, idx) => (
            <div
              key={idx}
              className={`move-analysis-item ${idx === currentMoveIndex ? 'active' : ''} ${move.isTarget ? 'target-move' : ''}`}
              onClick={() => goToMove(idx)}
            >
              <div className="move-header">
                <span className="move-num">
                  {move.moveNumber}{move.color === 'white' ? '.' : '...'}
                </span>
                <span className="move-san">{move.san}</span>
                <span className="move-symbol" style={{ color: getQualityColor(move.quality) }}>
                  {move.symbol}
                </span>
              </div>
              <div className="move-details">
                <span className="move-phase">{move.phase}</span>
                <span className="move-eval">{formatEvaluation(move.evalAfter)}</span>
                <span className="move-loss">-{move.cpLoss}cp</span>
              </div>
              {move.isTarget && move.cpLoss > 25 && (
                <div className="move-quality-badge" style={{ backgroundColor: getQualityColor(move.quality) }}>
                  {move.quality}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="game-analysis-container">
      {!analysisResult ? (
        <div className="input-section">
          <h1>Chess Game Analysis</h1>
          <p className="subtitle">Paste your PGN and get comprehensive analysis with detailed statistics</p>
          
          <div className="input-form">
            <div className="form-group">
              <label>Your Username (optional)</label>
              <input
                type="text"
                value={targetPlayer}
                onChange={(e) => setTargetPlayer(e.target.value)}
                placeholder="Enter your chess.com username"
                className="input-field"
              />
            </div>
            
            <div className="form-group">
              <label>PGN</label>
              <textarea
                value={pgn}
                onChange={(e) => setPgn(e.target.value)}
                placeholder="Paste your PGN here..."
                className="pgn-textarea"
                rows={15}
              />
            </div>
            
            <button
              onClick={analyzeGame}
              disabled={isAnalyzing}
              className="analyze-button"
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Game'}
            </button>
          </div>
        </div>
      ) : (
        <div className="analysis-view">
          <button onClick={() => setAnalysisResult(null)} className="back-button">
            <ArrowBackIcon style={{ marginRight: '8px' }} />
            New Analysis
          </button>
          
          <div className={`analysis-content ${isMinimized ? 'minimized' : ''}`}>
            {/* Boards Section - Always visible, on top when minimized */}
            <div className="boards-section">
              {renderBoardComparison()}
              
              <div className="current-position">
                <h3>Position Analysis</h3>
                {getCurrentMove() && (
                  <div className="position-info">
                    <div className="info-row">
                      <span>Move:</span>
                      <strong>
                        {getCurrentMove().moveNumber}
                        {getCurrentMove().color === 'white' ? '.' : '...'} {getCurrentMove().san}
                      </strong>
                    </div>
                    <div className="info-row">
                      <span>Phase:</span>
                      <strong>{getCurrentMove().phase}</strong>
                    </div>
                    <div className="info-row">
                      <span>Evaluation:</span>
                      <strong>{formatEvaluation(getCurrentMove().evalAfter)}</strong>
                    </div>
                    <div className="info-row">
                      <span>CP Loss:</span>
                      <strong style={{ color: getQualityColor(getCurrentMove().quality) }}>
                        {getCurrentMove().cpLoss}
                      </strong>
                    </div>
                    <div className="info-row">
                      <span>Quality:</span>
                      <strong style={{ color: getQualityColor(getCurrentMove().quality) }}>
                        {getCurrentMove().quality}
                      </strong>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="navigation-controls">
                <button
                  onClick={() => goToMove(Math.max(-1, currentMoveIndex - 1))}
                  disabled={currentMoveIndex <= 0}
                >
                  <ArrowBackIosIcon style={{ fontSize: '16px' }} />
                  Previous
                </button>
                <span className="move-counter">
                  {currentMoveIndex + 1} / {analysisResult.moves.length}
                </span>
                <button
                  onClick={() => goToMove(Math.min(analysisResult.moves.length - 1, currentMoveIndex + 1))}
                  disabled={currentMoveIndex >= analysisResult.moves.length - 1}
                >
                  Next
                  <ArrowForwardIosIcon style={{ fontSize: '16px' }} />
                </button>
              </div>

              {/* AI Voice Coach */}
              {getCurrentMove() && (
                <VoiceChat
                  fen={getCurrentMove().fen}
                  move={getCurrentMove().san}
                  bestMove={getCurrentMove().bestMoveSan}
                  evaluation={getCurrentMove().evalAfter}
                  cpLoss={getCurrentMove().cpLoss}
                  quality={getCurrentMove().quality}
                  phase={getCurrentMove().phase}
                />
              )}
            </div>

            {/* Analysis Section - Minimizable */}
            <div className="analysis-section">
              {renderStatistics()}
              {!isMinimized && renderMovesList()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default GameAnalysis;
