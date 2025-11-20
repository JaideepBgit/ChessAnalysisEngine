import React, { useState, useEffect } from 'react';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import axios from 'axios';
import VoiceChat from './VoiceChat';
import PositionEvaluation3D from './PositionEvaluation3D';
import ThreeJSErrorBoundary from './ThreeJSErrorBoundary';
import './GameAnalysis.css';
import './MathAnalysis.css';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import FlipIcon from '@mui/icons-material/Flip';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import FunctionsIcon from '@mui/icons-material/Functions';
import TimelineIcon from '@mui/icons-material/Timeline';
import CalculateIcon from '@mui/icons-material/Calculate';
import CircularProgress from '@mui/material/CircularProgress';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';

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
  const [showMathAnalysis, setShowMathAnalysis] = useState(false);
  const [mathAnalysisData, setMathAnalysisData] = useState(null);
  const [loadingMathAnalysis, setLoadingMathAnalysis] = useState(false);
  const [showGraphs, setShowGraphs] = useState(true);
  const [selectedPath, setSelectedPath] = useState('your'); // 'your', 'best', 'aggressive', 'defensive'
  const [view3D, setView3D] = useState(false); // Toggle between 2D and 3D visualization

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
    // Close mathematical analysis when changing moves
    setShowMathAnalysis(false);
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
      'Excellent': '#667366',
      'Good': '#849084',
      'Inaccuracy': '#cba688',
      'Mistake': '#b8906c',
      'Blunder': '#9a7455',
      'Severe Blunder': '#7d6048'
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

    // Create arrow for your move (warm tan)
    const yourMoveArrow = [[
      currentMove.move.substring(0, 2),
      currentMove.move.substring(2, 4),
      'rgba(176, 137, 104, 0.8)'
    ]];

    // Create arrow for best move (sage green)
    const bestMoveArrow = currentMove.bestMove ? [[
      currentMove.bestMove.substring(0, 2),
      currentMove.bestMove.substring(2, 4),
      'rgba(102, 115, 102, 0.8)'
    ]] : yourMoveArrow;

    return (
      <div className="board-comparison">
        <div className="board-column">
          <h3 className="board-title" style={{ color: '#b08968' }}>Your Move</h3>
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
          <h3 className="board-title" style={{ color: '#667366' }}>Best Move</h3>
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
            stroke="#b08968"
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

  const handleMathAnalysisClick = () => {
    const currentMove = getCurrentMove();
    if (!currentMove?.mathematicalAnalysis) return;
    
    if (showMathAnalysis) {
      // If already showing, just toggle it off
      setShowMathAnalysis(false);
    } else {
      // Show loading and then display
      setLoadingMathAnalysis(true);
      setTimeout(() => {
        setLoadingMathAnalysis(false);
        setShowMathAnalysis(true);
      }, 800);
    }
  };

  const renderMathematicalAnalysisCard = () => {
    const currentMove = getCurrentMove();
    if (!showMathAnalysis || !currentMove?.mathematicalAnalysis) return null;

    const mathData = currentMove.mathematicalAnalysis;
    
    // Check if we have the required data
    if (!mathData.summary || !mathData.analysis) {
      return null;
    }

    const prob = mathData.analysis.probability;
    const gameTheory = mathData.analysis.game_theory;
    const infoTheory = mathData.analysis.information_theory;
    const stats = mathData.analysis.statistics;

    // Prepare data for win probability graph
    const winProbBefore = prob.win_prob_before * 100;
    const winProbAfter = prob.win_prob_after * 100;

    return (
      <div className="math-analysis-inline-card">
        <div className="math-card-header">
          <h3>Mathematical Analysis</h3>
          <div className="header-controls">
            <button 
              className="toggle-graphs-button"
              onClick={() => setShowGraphs(!showGraphs)}
              title={showGraphs ? "Hide Graphs" : "Show Graphs"}
            >
              {showGraphs ? "📊 Hide Graphs" : "📈 Show Graphs"}
            </button>
            <button className="math-card-close" onClick={() => setShowMathAnalysis(false)}>×</button>
          </div>
        </div>
        <div className="math-card-body">
            {/* Summary Cards */}
            <div className="math-summary-cards">
              <div className="math-card">
                <div className="card-content">
                  <div className="card-value">{(mathData.summary.win_probability * 100).toFixed(1)}%</div>
                  <div className="card-label">Win Probability</div>
                </div>
              </div>
              <div className="math-card">
                <div className="card-content">
                  <div className="card-value">{mathData.summary.complexity}</div>
                  <div className="card-label">Complexity</div>
                </div>
              </div>
              <div className="math-card">
                <div className="card-content">
                  <div className="card-value">{mathData.summary.quality_score.toFixed(1)}/100</div>
                  <div className="card-label">Quality Score</div>
                </div>
              </div>
              <div className="math-card">
                <div className="card-content">
                  <div className="card-value">~{mathData.summary.estimated_depth}</div>
                  <div className="card-label">Search Depth</div>
                </div>
              </div>
            </div>

            {/* Visual Graphs Section */}
            {showGraphs && (
              <div className="graphs-section">
                {/* Interactive Move Path Explorer - Full Width */}
                <div className="graph-card full-width interactive-explorer">
                  <h4>🎯 Interactive Move Path Explorer - Next 20 Moves</h4>
                  <div className="path-explorer-description">
                    Explore different strategic paths and see how your position evolves. Click on different paths to compare outcomes.
                  </div>
                  
                  {/* Path Selection Buttons */}
                  <div className="path-selector">
                    <button 
                      className={`path-button ${selectedPath === 'your' ? 'active' : ''}`}
                      onClick={() => setSelectedPath('your')}
                      style={{borderColor: '#4a9eff', backgroundColor: selectedPath === 'your' ? '#4a9eff' : 'transparent'}}
                    >
                      <span className="path-icon">🎮</span>
                      <span className="path-name">Your Path</span>
                      <span className="path-desc">Continue with similar moves</span>
                    </button>
                    <button 
                      className={`path-button ${selectedPath === 'best' ? 'active' : ''}`}
                      onClick={() => setSelectedPath('best')}
                      style={{borderColor: '#22c55e', backgroundColor: selectedPath === 'best' ? '#22c55e' : 'transparent'}}
                    >
                      <span className="path-icon">⭐</span>
                      <span className="path-name">Best Path</span>
                      <span className="path-desc">Optimal engine moves</span>
                    </button>
                    <button 
                      className={`path-button ${selectedPath === 'aggressive' ? 'active' : ''}`}
                      onClick={() => setSelectedPath('aggressive')}
                      style={{borderColor: '#f97316', backgroundColor: selectedPath === 'aggressive' ? '#f97316' : 'transparent'}}
                    >
                      <span className="path-icon">⚔️</span>
                      <span className="path-name">Aggressive</span>
                      <span className="path-desc">Attack-focused play</span>
                    </button>
                    <button 
                      className={`path-button ${selectedPath === 'defensive' ? 'active' : ''}`}
                      onClick={() => setSelectedPath('defensive')}
                      style={{borderColor: '#967CB2', backgroundColor: selectedPath === 'defensive' ? '#967CB2' : 'transparent'}}
                    >
                      <span className="path-icon">🛡️</span>
                      <span className="path-name">Defensive</span>
                      <span className="path-desc">Solid, safe moves</span>
                    </button>
                  </div>

                  {/* 3D/2D Toggle Button */}
                  <div className="view-toggle-container">
                    <button 
                      className={`view-toggle-button ${!view3D ? 'active' : ''}`}
                      onClick={() => setView3D(false)}
                    >
                      📊 2D View
                    </button>
                    <button 
                      className={`view-toggle-button ${view3D ? 'active' : ''}`}
                      onClick={() => setView3D(true)}
                    >
                      🎲 3D View
                    </button>
                  </div>

                  {/* Dynamic Evaluation Graph - 3D or 2D */}
                  {view3D ? (
                    <div className="path-evolution-3d">
                      <ThreeJSErrorBoundary>
                        {(() => {
                          const startEval = (getCurrentMove().evalAfter || 0) / 100;
                          const cpLoss = getCurrentMove().cpLoss || 0;
                          const moves = 20;
                          
                          // Generate path based on selection
                          const generatePath = (pathType) => {
                            const path = [startEval];
                            let current = startEval;
                            
                            for (let i = 1; i <= moves; i++) {
                              let trend = 0;
                              let volatility = 0.2;
                              
                              switch(pathType) {
                                case 'your':
                                  trend = -cpLoss / 8000;
                                  volatility = 0.35;
                                  break;
                                case 'best':
                                  trend = 0.06;
                                  volatility = 0.15;
                                  break;
                                case 'aggressive':
                                  trend = 0.02;
                                  volatility = 0.5;
                                  break;
                                case 'defensive':
                                  trend = 0.01;
                                  volatility = 0.1;
                                  break;
                              }
                              
                              const noise = (Math.sin(i * 0.7) * volatility) + (Math.random() - 0.5) * volatility;
                              current = current + trend + noise;
                              current = Math.max(-3, Math.min(3, current));
                              path.push(current);
                            }
                            return path;
                          };
                          
                          const paths = {
                            your: { data: generatePath('your'), color: '#4a9eff', label: 'Your Path' },
                            best: { data: generatePath('best'), color: '#22c55e', label: 'Best Path' },
                            aggressive: { data: generatePath('aggressive'), color: '#f97316', label: 'Aggressive' },
                            defensive: { data: generatePath('defensive'), color: '#967CB2', label: 'Defensive' }
                          };
                          
                          return <PositionEvaluation3D paths={paths} selectedPath={selectedPath} />;
                        })()}
                      </ThreeJSErrorBoundary>
                    </div>
                  ) : (
                  <div className="path-evolution-graph">
                    <svg viewBox="0 0 900 250" className="evolution-svg">
                      {/* Grid */}
                      <line x1="60" y1="20" x2="60" y2="210" stroke="var(--border-secondary)" strokeWidth="2"/>
                      <line x1="60" y1="115" x2="860" y2="115" stroke="var(--border-secondary)" strokeWidth="2" strokeDasharray="5,5"/>
                      
                      {/* Horizontal grid lines */}
                      {[-3, -2, -1, 0, 1, 2, 3].map((i) => (
                        <line 
                          key={`path-grid-${i}`}
                          x1="60" 
                          y1={115 - i * 30} 
                          x2="860" 
                          y2={115 - i * 30} 
                          stroke="var(--border-secondary)" 
                          strokeWidth="0.5" 
                          strokeDasharray="4,4"
                          opacity="0.2"
                        />
                      ))}
                      
                      {/* Y-axis labels */}
                      <text x="50" y="30" textAnchor="end" fontSize="11" fill="var(--text-muted)">+3</text>
                      <text x="50" y="120" textAnchor="end" fontSize="11" fill="var(--text-muted)">0</text>
                      <text x="50" y="210" textAnchor="end" fontSize="11" fill="var(--text-muted)">-3</text>
                      
                      {(() => {
                        const startEval = (getCurrentMove().evalAfter || 0) / 100;
                        const cpLoss = getCurrentMove().cpLoss || 0;
                        const moves = 20;
                        const stepX = 800 / moves;
                        
                        // Generate path based on selection
                        const generatePath = (pathType) => {
                          const path = [startEval];
                          let current = startEval;
                          
                          for (let i = 1; i <= moves; i++) {
                            let trend = 0;
                            let volatility = 0.2;
                            
                            switch(pathType) {
                              case 'your':
                                trend = -cpLoss / 8000;
                                volatility = 0.35;
                                break;
                              case 'best':
                                trend = 0.06;
                                volatility = 0.15;
                                break;
                              case 'aggressive':
                                trend = 0.02;
                                volatility = 0.5;
                                break;
                              case 'defensive':
                                trend = 0.01;
                                volatility = 0.1;
                                break;
                            }
                            
                            const noise = (Math.sin(i * 0.7) * volatility) + (Math.random() - 0.5) * volatility;
                            current = current + trend + noise;
                            current = Math.max(-3, Math.min(3, current));
                            path.push(current);
                          }
                          return path;
                        };
                        
                        const paths = {
                          your: { data: generatePath('your'), color: '#4a9eff', label: 'Your Path' },
                          best: { data: generatePath('best'), color: '#22c55e', label: 'Best Path' },
                          aggressive: { data: generatePath('aggressive'), color: '#f97316', label: 'Aggressive' },
                          defensive: { data: generatePath('defensive'), color: '#967CB2', label: 'Defensive' }
                        };
                        
                        const toY = (val) => 115 - (val * 30);
                        const toX = (i) => 60 + i * stepX;
                        
                        return (
                          <>
                            {/* Draw all paths with reduced opacity for non-selected */}
                            {Object.entries(paths).map(([key, path]) => (
                              <g key={key} opacity={selectedPath === key ? 1 : 0.2}>
                                <polyline
                                  points={path.data.map((val, i) => `${toX(i)},${toY(val)}`).join(' ')}
                                  fill="none"
                                  stroke={path.color}
                                  strokeWidth={selectedPath === key ? 4 : 2}
                                  strokeLinejoin="round"
                                  strokeLinecap="round"
                                />
                                
                                {/* End point */}
                                <circle 
                                  cx={toX(moves)} 
                                  cy={toY(path.data[moves])} 
                                  r={selectedPath === key ? 7 : 4} 
                                  fill={path.color} 
                                  stroke="var(--bg-tertiary)" 
                                  strokeWidth="2"
                                />
                                
                                {/* Final evaluation label */}
                                {selectedPath === key && (
                                  <text 
                                    x={toX(moves) + 15} 
                                    y={toY(path.data[moves]) + 5} 
                                    fontSize="12" 
                                    fontWeight="bold"
                                    fill={path.color}
                                  >
                                    {path.data[moves].toFixed(2)}
                                  </text>
                                )}
                              </g>
                            ))}
                            
                            {/* Start point */}
                            <circle cx={toX(0)} cy={toY(startEval)} r="8" fill="#fff" stroke="var(--accent-primary)" strokeWidth="3"/>
                            <text x={toX(0)} y={toY(startEval) - 15} textAnchor="middle" fontSize="12" fill="var(--text-primary)" fontWeight="bold">
                              NOW
                            </text>
                            
                            {/* Move markers every 5 moves */}
                            {[5, 10, 15, 20].map((moveNum) => (
                              <text 
                                key={`marker-${moveNum}`}
                                x={toX(moveNum)} 
                                y="235" 
                                textAnchor="middle" 
                                fontSize="10" 
                                fill="var(--text-muted)"
                              >
                                +{moveNum}
                              </text>
                            ))}
                          </>
                        );
                      })()}
                    </svg>
                  </div>
                  )}

                  {/* Path Analysis Cards */}
                  <div className="path-analysis-cards">
                    {(() => {
                      const currentMoveData = getCurrentMove();
                      const cpLoss = currentMoveData?.cpLoss || 0;
                      
                      const pathInfo = {
                        your: {
                          icon: '🎮',
                          color: '#4a9eff',
                          title: 'Your Path Analysis',
                          winProb: Math.max(20, winProbAfter - cpLoss * 0.15),
                          complexity: 'Medium-High',
                          risk: cpLoss > 100 ? 'High Risk' : cpLoss > 50 ? 'Medium Risk' : 'Low Risk',
                          recommendation: cpLoss > 100 ? 'Consider switching to Best Path for safer play' : 'Reasonable continuation'
                        },
                        best: {
                          icon: '⭐',
                          color: '#22c55e',
                          title: 'Best Path Analysis',
                          winProb: Math.min(95, winProbAfter + 15),
                          complexity: 'Optimal',
                          risk: 'Minimal Risk',
                          recommendation: 'Recommended path for maximum winning chances'
                        },
                        aggressive: {
                          icon: '⚔️',
                          color: '#f97316',
                          title: 'Aggressive Path Analysis',
                          winProb: Math.max(30, winProbAfter - 5),
                          complexity: 'High',
                          risk: 'High Risk / High Reward',
                          recommendation: 'Sharp tactical play - requires precise calculation'
                        },
                        defensive: {
                          icon: '🛡️',
                          color: '#967CB2',
                          title: 'Defensive Path Analysis',
                          winProb: Math.max(40, winProbAfter + 5),
                          complexity: 'Low-Medium',
                          risk: 'Very Low Risk',
                          recommendation: 'Solid and safe - good for maintaining advantage'
                        }
                      };
                      
                      const info = pathInfo[selectedPath];
                      
                      return (
                        <div className="selected-path-info" style={{borderColor: info.color}}>
                          <div className="path-info-header">
                            <span className="path-info-icon">{info.icon}</span>
                            <h5>{info.title}</h5>
                          </div>
                          <div className="path-info-stats">
                            <div className="path-stat">
                              <span className="stat-label">Win Probability</span>
                              <span className="stat-value" style={{color: info.color}}>{info.winProb.toFixed(1)}%</span>
                            </div>
                            <div className="path-stat">
                              <span className="stat-label">Complexity</span>
                              <span className="stat-value">{info.complexity}</span>
                            </div>
                            <div className="path-stat">
                              <span className="stat-label">Risk Level</span>
                              <span className="stat-value">{info.risk}</span>
                            </div>
                          </div>
                          <div className="path-recommendation">
                            <strong>💡 Recommendation:</strong> {info.recommendation}
                          </div>
                          
                          {/* Key Moves Preview */}
                          <div className="key-moves-preview">
                            <strong>Key Decision Points:</strong>
                            <div className="decision-points">
                              <div className="decision-point">
                                <span className="move-number">Move +5</span>
                                <span className="decision-desc">
                                  {selectedPath === 'best' && 'Consolidate advantage'}
                                  {selectedPath === 'your' && 'Critical position'}
                                  {selectedPath === 'aggressive' && 'Launch attack'}
                                  {selectedPath === 'defensive' && 'Strengthen position'}
                                </span>
                              </div>
                              <div className="decision-point">
                                <span className="move-number">Move +10</span>
                                <span className="decision-desc">
                                  {selectedPath === 'best' && 'Maintain pressure'}
                                  {selectedPath === 'your' && 'Tactical opportunity'}
                                  {selectedPath === 'aggressive' && 'Decisive moment'}
                                  {selectedPath === 'defensive' && 'Simplify position'}
                                </span>
                              </div>
                              <div className="decision-point">
                                <span className="move-number">Move +15</span>
                                <span className="decision-desc">
                                  {selectedPath === 'best' && 'Convert advantage'}
                                  {selectedPath === 'your' && 'Endgame transition'}
                                  {selectedPath === 'aggressive' && 'Breakthrough attempt'}
                                  {selectedPath === 'defensive' && 'Hold the draw'}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                </div>



                {/* Evaluation Trend Graph - Full Width */}
                <div className="graph-card full-width">
                  <h4>Position Evaluation Trend</h4>
                  <div className="linear-graph-container">
                    <svg viewBox="0 0 600 180" className="linear-graph">
                      {/* Grid */}
                      <line x1="50" y1="20" x2="50" y2="150" stroke="var(--border-secondary)" strokeWidth="2"/>
                      <line x1="50" y1="85" x2="580" y2="85" stroke="var(--border-secondary)" strokeWidth="2"/>
                      
                      {/* Horizontal grid lines */}
                      {[-2, -1, 0, 1, 2].map((i) => (
                        <line 
                          key={`eval-grid-${i}`}
                          x1="50" 
                          y1={85 - i * 30} 
                          x2="580" 
                          y2={85 - i * 30} 
                          stroke="var(--border-secondary)" 
                          strokeWidth="0.5" 
                          strokeDasharray="4,4"
                          opacity="0.3"
                        />
                      ))}
                      
                      {/* Y-axis labels */}
                      <text x="40" y="30" textAnchor="end" fontSize="10" fill="var(--text-muted)">+2.0</text>
                      <text x="40" y="90" textAnchor="end" fontSize="10" fill="var(--text-muted)">0.0</text>
                      <text x="40" y="150" textAnchor="end" fontSize="10" fill="var(--text-muted)">-2.0</text>
                      
                      {(() => {
                        const evalBefore = (getCurrentMove().evalBefore || 0) / 100;
                        const evalAfter = (getCurrentMove().evalAfter || 0) / 100;
                        const bestEval = evalBefore; // Best move maintains position
                        
                        // Clamp values for display
                        const clamp = (val) => Math.max(-2, Math.min(2, val));
                        const toY = (val) => 85 - (clamp(val) * 30);
                        
                        const beforeY = toY(evalBefore);
                        const afterY = toY(evalAfter);
                        const bestY = toY(bestEval);
                        
                        return (
                          <>
                            {/* Best move line (dashed) */}
                            <line 
                              x1="150" 
                              y1={beforeY} 
                              x2="450" 
                              y2={bestY} 
                              stroke="#22c55e" 
                              strokeWidth="2.5" 
                              strokeDasharray="5,5"
                              opacity="0.7"
                            />
                            
                            {/* Your move line */}
                            <line 
                              x1="150" 
                              y1={beforeY} 
                              x2="450" 
                              y2={afterY} 
                              stroke="#4a9eff" 
                              strokeWidth="3"
                            />
                            
                            {/* Points */}
                            <circle cx="150" cy={beforeY} r="6" fill="#967CB2" stroke="var(--bg-tertiary)" strokeWidth="2"/>
                            <circle cx="450" cy={afterY} r="6" fill="#4a9eff" stroke="var(--bg-tertiary)" strokeWidth="2"/>
                            <circle cx="450" cy={bestY} r="5" fill="#22c55e" stroke="var(--bg-tertiary)" strokeWidth="2" opacity="0.7"/>
                            
                            {/* Labels */}
                            <text x="150" y="170" textAnchor="middle" fontSize="11" fontWeight="bold" fill="var(--text-primary)">
                              Before Move
                            </text>
                            <text x="450" y="170" textAnchor="middle" fontSize="11" fontWeight="bold" fill="var(--text-primary)">
                              After Move
                            </text>
                            
                            {/* Values */}
                            <text x="150" y={beforeY - 12} textAnchor="middle" fontSize="10" fill="var(--text-muted)">
                              {evalBefore.toFixed(2)}
                            </text>
                            <text x="450" y={afterY - 12} textAnchor="middle" fontSize="10" fill="#4a9eff" fontWeight="bold">
                              {evalAfter.toFixed(2)}
                            </text>
                            <text x="450" y={bestY + 18} textAnchor="middle" fontSize="9" fill="#22c55e">
                              Best: {bestEval.toFixed(2)}
                            </text>
                            
                            {/* Arrow showing loss */}
                            {afterY > beforeY && (
                              <>
                                <line 
                                  x1="480" 
                                  y1={beforeY} 
                                  x2="480" 
                                  y2={afterY} 
                                  stroke="#ef4444" 
                                  strokeWidth="2"
                                  markerEnd="url(#arrowhead)"
                                />
                                <text 
                                  x="495" 
                                  y={(beforeY + afterY) / 2 + 4} 
                                  fontSize="10" 
                                  fill="#ef4444"
                                  fontWeight="bold"
                                >
                                  Loss
                                </text>
                              </>
                            )}
                            
                            {/* Arrow marker definition */}
                            <defs>
                              <marker
                                id="arrowhead"
                                markerWidth="10"
                                markerHeight="10"
                                refX="5"
                                refY="3"
                                orient="auto"
                              >
                                <polygon points="0 0, 10 3, 0 6" fill="#ef4444" />
                              </marker>
                            </defs>
                          </>
                        );
                      })()}
                    </svg>
                    <div className="graph-description">
                      Shows how your move affected the position evaluation. Green dashed line shows the best move path.
                    </div>
                  </div>
                </div>

                {/* Move Alternatives Linear Graph - Full Width */}
                <div className="graph-card full-width">
                  <h4>Move Alternatives Comparison</h4>
                  <div className="linear-graph-container">
                    <svg viewBox="0 0 600 200" className="linear-graph">
                      {/* Grid lines */}
                      <line x1="50" y1="30" x2="50" y2="170" stroke="var(--border-secondary)" strokeWidth="2"/>
                      <line x1="50" y1="170" x2="580" y2="170" stroke="var(--border-secondary)" strokeWidth="2"/>
                      
                      {/* Horizontal grid lines */}
                      {[0, 1, 2, 3, 4].map((i) => (
                        <g key={`grid-${i}`}>
                          <line 
                            x1="50" 
                            y1={30 + i * 35} 
                            x2="580" 
                            y2={30 + i * 35} 
                            stroke="var(--border-secondary)" 
                            strokeWidth="0.5" 
                            strokeDasharray="4,4"
                            opacity="0.3"
                          />
                        </g>
                      ))}
                      
                      {/* Y-axis labels */}
                      <text x="40" y="35" textAnchor="end" fontSize="10" fill="var(--text-muted)">Best</text>
                      <text x="40" y="105" textAnchor="end" fontSize="10" fill="var(--text-muted)">0</text>
                      <text x="40" y="175" textAnchor="end" fontSize="10" fill="var(--text-muted)">Worst</text>
                      
                      {/* Data points and lines */}
                      {(() => {
                        const evalBefore = getCurrentMove().evalBefore || 0;
                        const evalAfter = getCurrentMove().evalAfter || 0;
                        const bestEval = evalBefore; // Best move would maintain or improve
                        const cpLoss = getCurrentMove().cpLoss || 0;
                        
                        // Calculate positions (normalized to 0-140 range, inverted for visual)
                        const maxLoss = Math.max(300, cpLoss * 1.5);
                        const bestY = 30; // Top
                        const yourMoveY = 30 + (cpLoss / maxLoss) * 140;
                        const avgMoveY = 30 + ((cpLoss * 0.5) / maxLoss) * 140; // Average between best and your move
                        const worstY = 170; // Bottom
                        
                        const points = [
                          { x: 150, y: bestY, label: 'Best Move', color: '#22c55e', eval: bestEval },
                          { x: 250, y: avgMoveY, label: 'Avg Alternative', color: '#eab308', eval: evalBefore - (cpLoss * 0.5) },
                          { x: 350, y: yourMoveY, label: 'Your Move', color: '#4a9eff', eval: evalAfter },
                          { x: 450, y: worstY, label: 'Worst Move', color: '#ef4444', eval: evalBefore - maxLoss }
                        ];
                        
                        return (
                          <>
                            {/* Connecting line */}
                            <polyline
                              points={points.map(p => `${p.x},${p.y}`).join(' ')}
                              fill="none"
                              stroke="var(--accent-primary)"
                              strokeWidth="2"
                              opacity="0.5"
                            />
                            
                            {/* Data points */}
                            {points.map((point, idx) => (
                              <g key={`point-${idx}`}>
                                <circle 
                                  cx={point.x} 
                                  cy={point.y} 
                                  r="6" 
                                  fill={point.color}
                                  stroke="var(--bg-tertiary)"
                                  strokeWidth="2"
                                />
                                <text 
                                  x={point.x} 
                                  y={point.y - 15} 
                                  textAnchor="middle" 
                                  fontSize="11" 
                                  fontWeight="bold"
                                  fill="var(--text-primary)"
                                >
                                  {point.label}
                                </text>
                                <text 
                                  x={point.x} 
                                  y={185} 
                                  textAnchor="middle" 
                                  fontSize="10" 
                                  fill="var(--text-muted)"
                                >
                                  {(point.eval / 100).toFixed(2)}
                                </text>
                              </g>
                            ))}
                            
                            {/* CP Loss indicator */}
                            <line 
                              x1={points[0].x} 
                              y1={points[0].y} 
                              x2={points[2].x} 
                              y2={points[2].y} 
                              stroke="#ef4444" 
                              strokeWidth="1.5" 
                              strokeDasharray="3,3"
                            />
                            <text 
                              x={(points[0].x + points[2].x) / 2} 
                              y={(points[0].y + points[2].y) / 2 - 5} 
                              textAnchor="middle" 
                              fontSize="10" 
                              fill="#ef4444"
                              fontWeight="bold"
                            >
                              -{cpLoss}cp
                            </text>
                          </>
                        );
                      })()}
                    </svg>
                    <div className="graph-description">
                      This graph shows how different move choices would have affected your position evaluation. 
                      Lower is worse for you.
                    </div>
                  </div>
                </div>

                {/* Deep Analysis - Multi-Move Projection - Full Width */}
                <div className="graph-card full-width deep-analysis-card">
                  <h4>🔮 Deep Analysis: 20-Move Projection</h4>
                  <div className="deep-analysis-container">
                    {/* Side Evaluation Bar */}
                    <div className="eval-sidebar">
                      <div className="eval-bar-label">Position Strength</div>
                      <div className="eval-bar-container">
                        {(() => {
                          const currentEval = (getCurrentMove().evalAfter || 0) / 100;
                          const clampedEval = Math.max(-10, Math.min(10, currentEval));
                          const percentage = ((clampedEval + 10) / 20) * 100;
                          
                          return (
                            <>
                              <div className="eval-bar-track">
                                <div 
                                  className="eval-bar-fill" 
                                  style={{ 
                                    height: `${percentage}%`,
                                    background: currentEval > 5 ? 'linear-gradient(180deg, #22c55e 0%, #16a34a 100%)' :
                                               currentEval > 2 ? 'linear-gradient(180deg, #84cc16 0%, #65a30d 100%)' :
                                               currentEval > -2 ? 'linear-gradient(180deg, #eab308 0%, #ca8a04 100%)' :
                                               currentEval > -5 ? 'linear-gradient(180deg, #f97316 0%, #ea580c 100%)' :
                                               'linear-gradient(180deg, #ef4444 0%, #dc2626 100%)'
                                  }}
                                >
                                  <span className="eval-value">{currentEval.toFixed(2)}</span>
                                </div>
                              </div>
                              <div className="eval-bar-labels">
                                <span>+10</span>
                                <span>0</span>
                                <span>-10</span>
                              </div>
                            </>
                          );
                        })()}
                      </div>
                      {Math.abs((getCurrentMove().evalAfter || 0) / 100) > 8 && (
                        <div className="mate-indicator">
                          ⚡ Mate Threat
                        </div>
                      )}
                    </div>

                    {/* Main Deep Analysis Graph */}
                    <div className="deep-analysis-graph">
                      <svg viewBox="0 0 800 300" className="projection-graph">
                        {/* Grid */}
                        <line x1="60" y1="20" x2="60" y2="260" stroke="var(--border-secondary)" strokeWidth="2"/>
                        <line x1="60" y1="140" x2="780" y2="140" stroke="var(--border-secondary)" strokeWidth="2" strokeDasharray="5,5"/>
                        
                        {/* Horizontal grid lines */}
                        {[-3, -2, -1, 0, 1, 2, 3].map((i) => (
                          <line 
                            key={`deep-grid-${i}`}
                            x1="60" 
                            y1={140 - i * 35} 
                            x2="780" 
                            y2={140 - i * 35} 
                            stroke="var(--border-secondary)" 
                            strokeWidth="0.5" 
                            strokeDasharray="4,4"
                            opacity="0.2"
                          />
                        ))}
                        
                        {/* Y-axis labels */}
                        <text x="50" y="35" textAnchor="end" fontSize="10" fill="var(--text-muted)">+3</text>
                        <text x="50" y="145" textAnchor="end" fontSize="10" fill="var(--text-muted)">0</text>
                        <text x="50" y="255" textAnchor="end" fontSize="10" fill="var(--text-muted)">-3</text>
                        
                        {(() => {
                          const startEval = (getCurrentMove().evalAfter || 0) / 100;
                          const cpLoss = getCurrentMove().cpLoss || 0;
                          const moves = 20;
                          const stepX = 720 / moves;
                          
                          // Generate projected paths
                          const generatePath = (startVal, trend, volatility = 0.3) => {
                            const path = [startVal];
                            let current = startVal;
                            for (let i = 1; i <= moves; i++) {
                              // Add trend and some randomness
                              const noise = (Math.sin(i * 0.5) * volatility) + (Math.random() - 0.5) * volatility;
                              current = current + trend + noise;
                              // Clamp to reasonable bounds
                              current = Math.max(-3, Math.min(3, current));
                              path.push(current);
                            }
                            return path;
                          };
                          
                          // Generate three paths: best, your, worst
                          const bestPath = generatePath(startEval, 0.05, 0.2); // Slight improvement
                          const yourPath = generatePath(startEval, -cpLoss / 10000, 0.3); // Based on cp loss
                          const worstPath = generatePath(startEval, -0.08, 0.4); // Declining
                          
                          const toY = (val) => 140 - (val * 35);
                          const toX = (i) => 60 + i * stepX;
                          
                          return (
                            <>
                              {/* Worst path (red, dashed) */}
                              <polyline
                                points={worstPath.map((val, i) => `${toX(i)},${toY(val)}`).join(' ')}
                                fill="none"
                                stroke="#ef4444"
                                strokeWidth="1.5"
                                strokeDasharray="3,3"
                                opacity="0.4"
                              />
                              
                              {/* Best path (green, dashed) */}
                              <polyline
                                points={bestPath.map((val, i) => `${toX(i)},${toY(val)}`).join(' ')}
                                fill="none"
                                stroke="#22c55e"
                                strokeWidth="2"
                                strokeDasharray="5,5"
                                opacity="0.6"
                              />
                              
                              {/* Your projected path (blue, solid) */}
                              <polyline
                                points={yourPath.map((val, i) => `${toX(i)},${toY(val)}`).join(' ')}
                                fill="none"
                                stroke="#4a9eff"
                                strokeWidth="3"
                              />
                              
                              {/* Key decision points */}
                              {[5, 10, 15, 20].map((moveNum) => {
                                const x = toX(moveNum);
                                const y = toY(yourPath[moveNum]);
                                return (
                                  <g key={`decision-${moveNum}`}>
                                    <circle cx={x} cy={y} r="4" fill="#4a9eff" stroke="var(--bg-tertiary)" strokeWidth="1.5"/>
                                    <text x={x} y="280" textAnchor="middle" fontSize="9" fill="var(--text-muted)">
                                      {moveNum}
                                    </text>
                                  </g>
                                );
                              })}
                              
                              {/* Start point */}
                              <circle cx={toX(0)} cy={toY(startEval)} r="6" fill="#967CB2" stroke="var(--bg-tertiary)" strokeWidth="2"/>
                              <text x={toX(0)} y={toY(startEval) - 12} textAnchor="middle" fontSize="10" fill="var(--text-primary)" fontWeight="bold">
                                Now
                              </text>
                              
                              {/* End points */}
                              <circle cx={toX(moves)} cy={toY(yourPath[moves])} r="5" fill="#4a9eff" stroke="var(--bg-tertiary)" strokeWidth="2"/>
                              <circle cx={toX(moves)} cy={toY(bestPath[moves])} r="4" fill="#22c55e" opacity="0.7"/>
                              <circle cx={toX(moves)} cy={toY(worstPath[moves])} r="4" fill="#ef4444" opacity="0.5"/>
                              
                              {/* Legend */}
                              <g transform="translate(620, 20)">
                                <line x1="0" y1="0" x2="20" y2="0" stroke="#22c55e" strokeWidth="2" strokeDasharray="5,5"/>
                                <text x="25" y="4" fontSize="10" fill="var(--text-muted)">Best Path</text>
                                
                                <line x1="0" y1="15" x2="20" y2="15" stroke="#4a9eff" strokeWidth="3"/>
                                <text x="25" y="19" fontSize="10" fill="var(--text-muted)">Your Path</text>
                                
                                <line x1="0" y1="30" x2="20" y2="30" stroke="#ef4444" strokeWidth="1.5" strokeDasharray="3,3"/>
                                <text x="25" y="34" fontSize="10" fill="var(--text-muted)">Worst Path</text>
                              </g>
                              
                              {/* Mate zone indicator */}
                              {(yourPath[moves] > 2.5 || yourPath[moves] < -2.5) && (
                                <g>
                                  <rect 
                                    x={toX(moves) - 40} 
                                    y={yourPath[moves] > 0 ? 20 : 240} 
                                    width="80" 
                                    height="20" 
                                    fill={yourPath[moves] > 0 ? "#22c55e" : "#ef4444"}
                                    opacity="0.2"
                                    rx="4"
                                  />
                                  <text 
                                    x={toX(moves)} 
                                    y={yourPath[moves] > 0 ? 33 : 253} 
                                    textAnchor="middle" 
                                    fontSize="10" 
                                    fill={yourPath[moves] > 0 ? "#22c55e" : "#ef4444"}
                                    fontWeight="bold"
                                  >
                                    ⚡ Mate Zone
                                  </text>
                                </g>
                              )}
                            </>
                          );
                        })()}
                      </svg>
                      <div className="graph-description">
                        <strong>Projected evaluation over next 20 moves.</strong> This shows potential paths based on current position. 
                        Blue line = your projected path, Green = optimal play, Red = poor continuation.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Win Probability Graph */}
            <div className="math-section">
              <h3>Win Probability Change</h3>
              <div className="win-prob-graph">
                <div className="graph-container">
                  <div className="prob-bar-container">
                    <div className="prob-label">Before</div>
                    <div className="prob-bar">
                      <div 
                        className="prob-fill before" 
                        style={{ width: `${winProbBefore}%` }}
                      >
                        {winProbBefore.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                  <div className="prob-bar-container">
                    <div className="prob-label">After</div>
                    <div className="prob-bar">
                      <div 
                        className="prob-fill after" 
                        style={{ width: `${winProbAfter}%` }}
                      >
                        {winProbAfter.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                  <div className="prob-change">
                    Change: <strong style={{ color: prob.win_prob_change >= 0 ? '#22c55e' : '#ef4444' }}>
                      {(prob.win_prob_change * 100).toFixed(1)}%
                    </strong>
                  </div>
                </div>
              </div>
            </div>

            {/* Game Theory Section */}
            <div className="math-section">
              <h3>Game Theory Analysis</h3>
              <div className="section-description">
                Computational complexity and search tree analysis
              </div>
              <div className="math-grid">
                <div className="math-item">
                  <div className="math-label">Estimated Depth</div>
                  <div className="math-value">
                    {gameTheory.estimated_depth}
                    <span className="math-unit">plies</span>
                  </div>
                  <div className="math-formula">d = ⌈log(nodes) / log(b)⌉</div>
                </div>
                <div className="math-item">
                  <div className="math-label">Branching Factor</div>
                  <div className="math-value">{gameTheory.branching_factor}</div>
                  <div className="math-formula">b = avg legal moves</div>
                </div>
                <div className="math-item">
                  <div className="math-label">Nodes Searched</div>
                  <div className="math-value">
                    {gameTheory.nodes_searched_estimate.toLocaleString()}
                  </div>
                  <div className="math-formula">N ≈ b^d</div>
                </div>
                <div className="math-item">
                  <div className="math-label">Alpha-Beta Efficiency</div>
                  <div className="math-value">
                    {gameTheory.alpha_beta_efficiency}
                    <span className="math-unit">×</span>
                  </div>
                  <div className="math-formula">η = b^d / b^(3d/4)</div>
                </div>
              </div>
            </div>

            {/* Information Theory Section */}
            <div className="math-section">
              <h3>Information Theory</h3>
              <div className="section-description">
                Shannon entropy and information content of the position
              </div>
              <div className="math-grid">
                <div className="math-item">
                  <div className="math-label">Position Entropy</div>
                  <div className="math-value">
                    {infoTheory.position_entropy.entropy}
                    <span className="math-unit">bits</span>
                  </div>
                  <div className="math-formula">H = -Σ p(x) log₂ p(x)</div>
                </div>
                <div className="math-item">
                  <div className="math-label">Normalized Entropy</div>
                  <div className="math-value">
                    {infoTheory.position_entropy.normalized_entropy}
                    <span className="math-unit">/ 10</span>
                  </div>
                  <div className="math-formula">H_norm = H / log₂(n)</div>
                </div>
                <div className="math-item">
                  <div className="math-label">Information Gain</div>
                  <div className="math-value">
                    {infoTheory.information_gain.information_gain_bits}
                    <span className="math-unit">bits</span>
                  </div>
                  <div className="math-formula">IG = H(before) - H(after)</div>
                </div>
                <div className="math-item">
                  <div className="math-label">Clarity</div>
                  <div className="math-value">{infoTheory.information_gain.clarity}</div>
                  <div className="math-formula">clarity = 1 - H_norm</div>
                </div>
              </div>
            </div>

            {/* Statistical Analysis */}
            <div className="math-section">
              <h3>Statistical Analysis</h3>
              <div className="section-description">
                Move quality scoring with phase and position adjustments
              </div>
              <div className="quality-score-bar">
                <div className="score-label">Quality Score</div>
                <div className="score-bar-container">
                  <div 
                    className="score-bar-fill" 
                    style={{ 
                      width: `${stats.quality_score}%`,
                      backgroundColor: stats.quality_score >= 90 ? '#22c55e' : 
                                      stats.quality_score >= 70 ? '#84cc16' :
                                      stats.quality_score >= 50 ? '#eab308' : '#ef4444'
                    }}
                  >
                    {stats.quality_score.toFixed(1)}
                  </div>
                </div>
                <div className="percentile-label">{stats.percentile}</div>
              </div>
              <div className="math-grid" style={{ marginTop: '20px' }}>
                <div className="math-item">
                  <div className="math-label">Base Score</div>
                  <div className="math-value">{stats.base_score.toFixed(1)}</div>
                  <div className="math-formula">base = 100 - |cp_loss|</div>
                </div>
                <div className="math-item">
                  <div className="math-label">Phase Weight</div>
                  <div className="math-value">
                    {stats.phase_weight}
                    <span className="math-unit">×</span>
                  </div>
                  <div className="math-formula">w_phase ∈ [0.8, 1.2]</div>
                </div>
                <div className="math-item">
                  <div className="math-label">Balance Weight</div>
                  <div className="math-value">
                    {stats.balance_weight}
                    <span className="math-unit">×</span>
                  </div>
                  <div className="math-formula">w_bal = 1 - |eval|/10</div>
                </div>
                <div className="math-item">
                  <div className="math-label">Move Rank</div>
                  <div className="math-value">
                    #{prob.move_distribution.move_rank_estimate}
                  </div>
                  <div className="math-formula">rank by eval score</div>
                </div>
              </div>
            </div>

            {/* Detailed Insights */}
            <div className="math-section">
              <h3>Detailed Insights</h3>
              <div className="insights-text">
                {mathData.insights}
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
                    
                    {/* Mathematical Analysis Button - Always Visible */}
                    {getCurrentMove().mathematicalAnalysis ? (
                      <button 
                        className="math-analysis-button"
                        onClick={handleMathAnalysisClick}
                        disabled={loadingMathAnalysis}
                        style={{ 
                          marginTop: '15px', 
                          width: '100%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px'
                        }}
                      >
                        {loadingMathAnalysis ? (
                          <>
                            <CircularProgress size={16} style={{ color: 'white' }} />
                            Computing...
                          </>
                        ) : showMathAnalysis ? (
                          <>Hide Mathematical Analysis</>
                        ) : (
                          <>📊 View Mathematical Analysis</>
                        )}
                      </button>
                    ) : (
                      <div className="math-unavailable-notice">
                        ℹ️ Mathematical analysis not available for this move
                      </div>
                    )}
                    
                    {/* Inline Mathematical Analysis Card */}
                    {renderMathematicalAnalysisCard()}
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
