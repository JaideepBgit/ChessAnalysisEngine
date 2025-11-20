from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import chess
import chess.engine
import chess.pgn
import io
import os
import tempfile
from collections import defaultdict
from mathematical_analysis import analyze_position_mathematically

app = Flask(__name__)
CORS(app)

# Configure Stockfish path
STOCKFISH_PATH = r"C:\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"

# Initialize AI components
ollama_available = False
speech_recognition_available = False
piper_tts_available = False
piper_voice = None

try:
    import ollama
    ollama_available = True
    print("✓ Ollama available")
except ImportError:
    print("Ollama not available. Install with: pip install ollama")

# SpeechRecognition for voice input (uses Google's free API)
try:
    import speech_recognition as sr
    speech_recognition_available = True
    print("✓ SpeechRecognition available (voice input enabled)")
except ImportError:
    print("SpeechRecognition not available. Install with: pip install SpeechRecognition")
    speech_recognition_available = False

# Piper TTS for voice output (local, high-quality) - using executable
import subprocess

# Check if Piper executable exists
piper_exe_path = os.path.join(os.path.dirname(__file__), "piper", "piper.exe")
piper_model_path = os.path.join(os.path.dirname(__file__), "models", "en_US-lessac-medium.onnx")

if os.path.exists(piper_exe_path) and os.path.exists(piper_model_path):
    piper_tts_available = True
    print(f"✓ Piper TTS available at {piper_exe_path}")
    print(f"✓ Voice model found at {piper_model_path}")
else:
    piper_tts_available = False
    if not os.path.exists(piper_exe_path):
        print(f"⚠️ Piper executable not found at {piper_exe_path}")
    if not os.path.exists(piper_model_path):
        print(f"⚠️ Voice model not found at {piper_model_path}")
    print("Install Piper: Download from https://github.com/rhasspy/piper/releases")


def detect_game_phase(board, move_number):
    """Detect game phase based on move number and material on board."""
    piece_count = len(board.piece_map()) - 2
    
    if move_number <= 10:
        return 'opening'
    
    if piece_count <= 10:
        return 'endgame'
    
    white_queen = len(board.pieces(chess.QUEEN, chess.WHITE))
    black_queen = len(board.pieces(chess.QUEEN, chess.BLACK))
    
    if white_queen == 0 and black_queen == 0 and piece_count <= 14:
        return 'endgame'
    
    return 'middlegame'


def classify_move_quality(centipawn_loss):
    """Classify move quality based on centipawn loss."""
    if centipawn_loss <= 10:
        return "Excellent", "✓"
    elif centipawn_loss <= 25:
        return "Good", "○"
    elif centipawn_loss <= 50:
        return "Inaccuracy", "?!"
    elif centipawn_loss <= 100:
        return "Mistake", "?"
    elif centipawn_loss <= 300:
        return "Blunder", "??"
    else:
        return "Severe Blunder", "???"


def calculate_accuracy(centipawn_losses):
    """Calculate accuracy percentage from centipawn losses."""
    if not centipawn_losses:
        return 100.0
    avg_loss = sum(centipawn_losses) / len(centipawn_losses)
    accuracy = max(0, 100 - avg_loss / 5)
    return round(accuracy, 1)


def count_material(board, color):
    """Count material value for a color."""
    material = 0
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }
    
    for piece_type, value in piece_values.items():
        material += len(board.pieces(piece_type, color)) * value
    
    return material

@app.route('/api/analyze-position', methods=['POST'])
def analyze_position():
    """Analyze a chess position and return best moves and evaluation"""
    try:
        data = request.json
        fen = data.get('fen')
        depth = data.get('depth', 18)
        
        board = chess.Board(fen)
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        
        # Analyze position
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        
        # Get evaluation
        score = info["score"].white().score(mate_score=10000)
        
        # Get best moves (top 3)
        multipv_info = engine.analyse(board, chess.engine.Limit(depth=depth), multipv=3)
        
        best_moves = []
        for pv_info in multipv_info:
            pv = pv_info.get("pv", [])
            if pv:
                move = pv[0]
                pv_score = pv_info["score"].white().score(mate_score=10000)
                best_moves.append({
                    'move': move.uci(),
                    'san': board.san(move),
                    'score': pv_score,
                    'pv': [m.uci() for m in pv[:5]]
                })
        
        engine.quit()
        
        return jsonify({
            'success': True,
            'evaluation': score,
            'bestMoves': best_moves,
            'fen': fen
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/make-move', methods=['POST'])
def make_move():
    """Make a move and return the new position"""
    try:
        data = request.json
        fen = data.get('fen')
        move_uci = data.get('move')
        
        board = chess.Board(fen)
        move = chess.Move.from_uci(move_uci)
        
        if move in board.legal_moves:
            board.push(move)
            return jsonify({
                'success': True,
                'fen': board.fen(),
                'san': board.san(move),
                'isGameOver': board.is_game_over(),
                'result': board.result() if board.is_game_over() else None
            })
        else:
            return jsonify({'success': False, 'error': 'Illegal move'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/get-legal-moves', methods=['POST'])
def get_legal_moves():
    """Get all legal moves for current position"""
    try:
        data = request.json
        fen = data.get('fen')
        
        board = chess.Board(fen)
        legal_moves = []
        
        for move in board.legal_moves:
            legal_moves.append({
                'from': chess.square_name(move.from_square),
                'to': chess.square_name(move.to_square),
                'uci': move.uci(),
                'san': board.san(move)
            })
        
        return jsonify({
            'success': True,
            'legalMoves': legal_moves,
            'turn': 'white' if board.turn == chess.WHITE else 'black'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/analyze-game', methods=['POST'])
def analyze_game():
    """Analyze a complete game from PGN with comprehensive statistics"""
    try:
        data = request.json
        pgn_string = data.get('pgn')
        target_player = data.get('targetPlayer', '')
        depth = data.get('depth', 18)
        
        pgn = io.StringIO(pgn_string)
        game = chess.pgn.read_game(pgn)
        
        if not game:
            return jsonify({'success': False, 'error': 'Invalid PGN'}), 400
        
        # Get game info
        white_name = game.headers.get("White", "White")
        black_name = game.headers.get("Black", "Black")
        white_elo = int(game.headers.get("WhiteElo", 1500))
        black_elo = int(game.headers.get("BlackElo", 1500))
        result = game.headers.get("Result", "*")
        
        # Determine target player color
        if target_player.lower() in white_name.lower():
            target_color = chess.WHITE
            opponent_name = black_name
            target_elo = white_elo
            opponent_elo = black_elo
        elif target_player.lower() in black_name.lower():
            target_color = chess.BLACK
            opponent_name = white_name
            target_elo = black_elo
            opponent_elo = white_elo
        else:
            target_color = chess.WHITE
            opponent_name = black_name
            target_elo = white_elo
            opponent_elo = black_elo
        
        # Get game result scores
        if result == "1-0":
            white_score, black_score = 1.0, 0.0
        elif result == "0-1":
            white_score, black_score = 0.0, 1.0
        else:
            white_score, black_score = 0.5, 0.5
        
        target_score = white_score if target_color == chess.WHITE else black_score
        
        # Initialize engine
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        engine.configure({"Hash": 256, "Threads": 4})
        
        # Analysis data structures
        board = game.board()
        moves_analysis = []
        
        # Phase-specific tracking
        phase_data = {
            'opening': {'errors': [], 'moves': 0},
            'middlegame': {'errors': [], 'moves': 0},
            'endgame': {'errors': [], 'moves': 0}
        }
        
        # Move quality counters
        white_stats = {'excellent': 0, 'good': 0, 'inaccuracies': 0, 'mistakes': 0, 'blunders': 0, 'severe_blunders': 0, 'cp_losses': []}
        black_stats = {'excellent': 0, 'good': 0, 'inaccuracies': 0, 'mistakes': 0, 'blunders': 0, 'severe_blunders': 0, 'cp_losses': []}
        
        move_number = 1
        
        # Analyze each move
        for idx, move in enumerate(game.mainline_moves()):
            current_phase = detect_game_phase(board, move_number)
            is_white_move = (idx % 2 == 0)
            is_target_move = (board.turn == target_color)
            
            # Get best move and evaluation before the move
            info_before = engine.analyse(board, chess.engine.Limit(depth=depth))
            best_move = info_before.get("pv", [None])[0]
            eval_before = info_before["score"].white().score(mate_score=10000)
            
            move_san = board.san(move)
            best_move_san = board.san(best_move) if best_move else None
            board_before_fen = board.fen()
            
            board.push(move)
            
            # Get evaluation after the move
            info_after = engine.analyse(board, chess.engine.Limit(depth=depth))
            eval_after = info_after["score"].white().score(mate_score=10000)
            
            # Calculate centipawn loss
            if eval_before is not None and eval_after is not None:
                if is_white_move:
                    cp_loss = max(0, eval_before - eval_after)
                else:
                    cp_loss = max(0, eval_after - eval_before)
            else:
                cp_loss = 0
            
            quality, symbol = classify_move_quality(cp_loss)
            
            # Update statistics
            stats = white_stats if is_white_move else black_stats
            stats['cp_losses'].append(cp_loss)
            
            if cp_loss <= 10:
                stats['excellent'] += 1
            elif cp_loss <= 25:
                stats['good'] += 1
            elif cp_loss <= 50:
                stats['inaccuracies'] += 1
            elif cp_loss <= 100:
                stats['mistakes'] += 1
            elif cp_loss <= 300:
                stats['blunders'] += 1
            else:
                stats['severe_blunders'] += 1
            
            # Update phase tracking
            if is_target_move:
                phase_data[current_phase]['errors'].append(cp_loss)
                phase_data[current_phase]['moves'] += 1
            
            # Calculate material
            white_material = count_material(board, chess.WHITE)
            black_material = count_material(board, chess.BLACK)
            
            # Add mathematical analysis for important moves (target player moves with cp_loss > 25)
            math_analysis = None
            if is_target_move and cp_loss > 25:
                try:
                    math_result = analyze_position_mathematically(
                        board_before_fen, move.uci(), best_move.uci() if best_move else None,
                        eval_before, eval_after, cp_loss, current_phase, move_san, best_move_san
                    )
                    math_analysis = {
                        'analysis': math_result['analysis'],
                        'insights': math_result['insights'],
                        'summary': math_result['summary']
                    }
                except Exception as e:
                    print(f"Math analysis error for move {move_number}: {e}")
            
            moves_analysis.append({
                'moveNumber': move_number,
                'halfMove': idx,
                'color': 'white' if is_white_move else 'black',
                'phase': current_phase,
                'move': move.uci(),
                'san': move_san,
                'bestMove': best_move.uci() if best_move else None,
                'bestMoveSan': best_move_san,
                'evalBefore': eval_before,
                'evalAfter': eval_after,
                'cpLoss': cp_loss,
                'quality': quality,
                'symbol': symbol,
                'isTarget': is_target_move,
                'fen': board.fen(),
                'fenBefore': board_before_fen,
                'whiteMaterial': white_material,
                'blackMaterial': black_material,
                'mathematicalAnalysis': math_analysis
            })
            
            if is_white_move:
                move_number += 1
        
        engine.quit()
        
        # Calculate accuracies
        white_accuracy = calculate_accuracy(white_stats['cp_losses'])
        black_accuracy = calculate_accuracy(black_stats['cp_losses'])
        
        opening_accuracy = calculate_accuracy(phase_data['opening']['errors'])
        middlegame_accuracy = calculate_accuracy(phase_data['middlegame']['errors'])
        endgame_accuracy = calculate_accuracy(phase_data['endgame']['errors'])
        
        target_stats = white_stats if target_color == chess.WHITE else black_stats
        target_accuracy = white_accuracy if target_color == chess.WHITE else black_accuracy
        
        # Calculate performance rating (chess.com style)
        # This considers: accuracy, move quality distribution, game result, and opponent strength
        
        total_moves = len(target_stats['cp_losses'])
        if total_moves == 0:
            performance_rating = target_elo
        else:
            # Base rating from accuracy (0-100 scale)
            accuracy_component = (target_accuracy - 50) * 10  # -500 to +500
            
            # Move quality score (weighted by severity)
            excellent_score = target_stats['excellent'] * 10
            good_score = target_stats['good'] * 5
            inaccuracy_penalty = target_stats['inaccuracies'] * -15
            mistake_penalty = target_stats['mistakes'] * -40
            blunder_penalty = target_stats['blunders'] * -90
            severe_blunder_penalty = target_stats['severe_blunders'] * -150
            
            quality_score = (excellent_score + good_score + inaccuracy_penalty + 
                           mistake_penalty + blunder_penalty + severe_blunder_penalty) / total_moves
            
            # Game result bonus/penalty
            if target_score == 1.0:  # Win
                result_bonus = 50
            elif target_score == 0.5:  # Draw
                result_bonus = 0
            else:  # Loss
                result_bonus = -50
            
            # Opponent strength factor
            rating_diff = opponent_elo - target_elo
            opponent_factor = rating_diff * 0.1  # Stronger opponent = higher performance potential
            
            # Phase performance (bonus for consistent play)
            phase_consistency = 100 - abs(opening_accuracy - middlegame_accuracy) - abs(middlegame_accuracy - endgame_accuracy)
            phase_bonus = phase_consistency * 0.5
            
            # Combine all factors
            total_adjustment = (accuracy_component + quality_score + result_bonus + 
                              opponent_factor + phase_bonus)
            
            # Cap the adjustment
            total_adjustment = max(-400, min(400, total_adjustment))
            
            performance_rating = round(target_elo + total_adjustment)
        
        return jsonify({
            'success': True,
            'gameInfo': {
                'white': white_name,
                'black': black_name,
                'whiteElo': white_elo,
                'blackElo': black_elo,
                'result': result,
                'targetPlayer': target_player,
                'targetColor': 'white' if target_color == chess.WHITE else 'black',
                'opponent': opponent_name,
                'targetElo': target_elo,
                'opponentElo': opponent_elo,
                'targetScore': target_score
            },
            'moves': moves_analysis,
            'statistics': {
                'white': {
                    'accuracy': white_accuracy,
                    'avgCpLoss': round(sum(white_stats['cp_losses']) / len(white_stats['cp_losses']), 2) if white_stats['cp_losses'] else 0,
                    'excellent': white_stats['excellent'],
                    'good': white_stats['good'],
                    'inaccuracies': white_stats['inaccuracies'],
                    'mistakes': white_stats['mistakes'],
                    'blunders': white_stats['blunders'],
                    'severeBlunders': white_stats['severe_blunders']
                },
                'black': {
                    'accuracy': black_accuracy,
                    'avgCpLoss': round(sum(black_stats['cp_losses']) / len(black_stats['cp_losses']), 2) if black_stats['cp_losses'] else 0,
                    'excellent': black_stats['excellent'],
                    'good': black_stats['good'],
                    'inaccuracies': black_stats['inaccuracies'],
                    'mistakes': black_stats['mistakes'],
                    'blunders': black_stats['blunders'],
                    'severeBlunders': black_stats['severe_blunders']
                },
                'phaseAccuracy': {
                    'opening': opening_accuracy,
                    'openingMoves': phase_data['opening']['moves'],
                    'middlegame': middlegame_accuracy,
                    'middlegameMoves': phase_data['middlegame']['moves'],
                    'endgame': endgame_accuracy,
                    'endgameMoves': phase_data['endgame']['moves']
                },
                'performanceRating': performance_rating
            }
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/mathematical-analysis', methods=['POST'])
def mathematical_analysis():
    """Get deep mathematical analysis for a specific move"""
    try:
        data = request.json
        fen = data.get('fen')
        move_uci = data.get('move')
        best_move_uci = data.get('bestMove')
        eval_before = data.get('evalBefore')
        eval_after = data.get('evalAfter')
        cp_loss = data.get('cpLoss', 0)
        phase = data.get('phase', 'middlegame')
        move_san = data.get('moveSan', '')
        best_move_san = data.get('bestMoveSan', '')
        
        # Get mathematical analysis
        result = analyze_position_mathematically(
            fen, move_uci, best_move_uci, eval_before, eval_after,
            cp_loss, phase, move_san, best_move_san
        )
        
        return jsonify({
            'success': True,
            'analysis': result['analysis'],
            'insights': result['insights'],
            'summary': result['summary']
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/chat-analysis', methods=['POST'])
def chat_analysis():
    """Chat with AI coach about chess positions"""
    if not ollama_available:
        error_msg = 'Ollama not installed. Please install Ollama from https://ollama.ai'
        print(f"❌ Chat analysis error: {error_msg}")
        return jsonify({
            'success': False, 
            'error': error_msg
        }), 400
    
    try:
        data = request.json
        fen = data.get('fen', '')
        move = data.get('move', '')
        best_move = data.get('bestMove', '')
        evaluation = data.get('evaluation', 0)
        cp_loss = data.get('cpLoss', 0)
        quality = data.get('quality', '')
        user_question = data.get('question', '')
        game_phase = data.get('phase', '')
        
        print(f"🤖 AI Coach request: {user_question[:50]}...")
        
        # Build context for Ollama
        context = f"""You are an expert chess coach analyzing a position.

Position (FEN): {fen}
Game Phase: {game_phase}
Move played: {move}
Best move: {best_move}
Engine evaluation: {evaluation} centipawns
Centipawn loss: {cp_loss}
Move quality: {quality}

Player question: {user_question if user_question else "Please analyze this position and move."}

Provide clear, educational insights. Explain:
- Why this move is good/bad
- What the player should look for in this position
- Key tactical or strategic ideas
- Better alternatives if the move wasn't optimal
- Specific advice for improvement

Keep your response concise (3-5 sentences), educational, and encouraging."""

        # Call Ollama (using qwen2.5:7b - change to 'llama3.2' if you download it)
        print("📡 Calling Ollama...")
        response = ollama.chat(model='qwen2.5:7b', messages=[
            {'role': 'system', 'content': 'You are a patient and knowledgeable chess coach who explains concepts clearly and encourages improvement.'},
            {'role': 'user', 'content': context}
        ])
        
        print("✓ AI Coach response received")
        
        return jsonify({
            'success': True,
            'response': response['message']['content']
        })
    
    except Exception as e:
        error_msg = f'AI Coach error: {str(e)}. Make sure Ollama is running and qwen2.5:7b model is installed.'
        print(f"❌ {error_msg}")
        return jsonify({
            'success': False, 
            'error': error_msg
        }), 400


@app.route('/api/voice-to-text', methods=['POST'])
def voice_to_text():
    """Convert voice recording to text using SpeechRecognition (Google API - Free)"""
    if not speech_recognition_available:
        error_msg = 'SpeechRecognition not installed. Run: pip install SpeechRecognition'
        print(f"❌ Voice-to-text error: {error_msg}")
        return jsonify({
            'success': False, 
            'error': error_msg
        }), 400
    
    try:
        if 'audio' not in request.files:
            print("❌ Voice-to-text error: No audio file provided")
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        print(f"📝 Received audio file: {audio_file.filename}")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_path = temp_audio.name
        
        print(f"🎤 Transcribing audio...")
        
        # Transcribe with SpeechRecognition (uses Google's free API)
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        print(f"✓ Transcribed: {text}")
        
        # Clean up
        os.unlink(temp_path)
        
        return jsonify({
            'success': True,
            'text': text.strip()
        })
    
    except sr.UnknownValueError:
        error_msg = 'Could not understand audio'
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 400
    except sr.RequestError as e:
        error_msg = f'Could not request results from Google: {str(e)}'
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 400
    except Exception as e:
        error_msg = f'Voice recognition error: {str(e)}'
        print(f"❌ {error_msg}")
        # Clean up temp file if it exists
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass
        return jsonify({'success': False, 'error': error_msg}), 400


@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech using Piper TTS executable or pyttsx3 fallback"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        print(f"🔊 Generating speech for: {text[:50]}...")
        
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            output_path = temp_audio.name
        
        # Try Piper executable first (better quality)
        if piper_tts_available:
            try:
                # Run Piper as subprocess
                process = subprocess.Popen(
                    [piper_exe_path, '--model', piper_model_path, '--output_file', output_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(input=text, timeout=30)
                
                if process.returncode == 0 and os.path.exists(output_path):
                    print(f"✓ Speech generated with Piper")
                else:
                    raise Exception(f"Piper failed: {stderr}")
                    
            except Exception as piper_error:
                print(f"⚠️ Piper failed: {piper_error}")
                print("Trying pyttsx3 fallback...")
                # Fall through to pyttsx3
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.save_to_file(text, output_path)
                    engine.runAndWait()
                    print(f"✓ Speech generated with pyttsx3")
                except ImportError:
                    return jsonify({
                        'success': False, 
                        'error': 'No TTS engine available. Install pyttsx3: pip install pyttsx3'
                    }), 400
        else:
            # Use pyttsx3 as fallback (simpler, works everywhere)
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.save_to_file(text, output_path)
                engine.runAndWait()
                print(f"✓ Speech generated with pyttsx3")
            except ImportError:
                return jsonify({
                    'success': False, 
                    'error': 'No TTS engine available. Install pyttsx3: pip install pyttsx3'
                }), 400
        
        # Send file and clean up after
        response = send_file(output_path, mimetype='audio/wav')
        
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(output_path)
            except:
                pass
        
        return response
    
    except Exception as e:
        # Try pyttsx3 as last resort
        try:
            import pyttsx3
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                output_path = temp_audio.name
            
            engine = pyttsx3.init()
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            print(f"✓ Speech generated with pyttsx3 (fallback)")
            
            response = send_file(output_path, mimetype='audio/wav')
            
            @response.call_on_close
            def cleanup():
                try:
                    os.unlink(output_path)
                except:
                    pass
            
            return response
        except:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False, 
                'error': f'Text-to-speech error: {str(e)}. Install pyttsx3 for basic TTS: pip install pyttsx3'
            }), 400


@app.route('/api/check-ai-status', methods=['GET'])
def check_ai_status():
    """Check if AI features are available"""
    ollama_status = False
    ollama_models = []
    
    if ollama_available:
        try:
            # Check if Ollama is running and get available models
            models = ollama.list()
            ollama_status = True
            ollama_models = [m['name'] for m in models.get('models', [])]
        except Exception as e:
            print(f"Ollama check error: {e}")
    
    return jsonify({
        'ollama': ollama_status,
        'models': ollama_models,
        'whisper': speech_recognition_available,
        'tts': piper_tts_available
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
