import chess
import chess.pgn
import chess.engine
import io
from collections import defaultdict


def detect_game_phase(board, move_number):
    """
    Detect game phase based on move number and material on board.
    
    Returns: 'opening', 'middlegame', or 'endgame'
    """
    # Count pieces (excluding kings)
    piece_count = len(board.piece_map()) - 2  # Subtract 2 kings
    
    # Opening: First 10-15 moves
    if move_number <= 10:
        return 'opening'
    
    # Endgame: Few pieces remain (typically ≤ 12 pieces total including kings)
    if piece_count <= 10:
        return 'endgame'
    
    # Check if queens are off the board (common endgame indicator)
    white_queen = len(board.pieces(chess.QUEEN, chess.WHITE))
    black_queen = len(board.pieces(chess.QUEEN, chess.BLACK))
    
    if white_queen == 0 and black_queen == 0 and piece_count <= 14:
        return 'endgame'
    
    # Middle game is everything else
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


def format_evaluation(score):
    """Format chess engine evaluation score."""
    if score is None:
        return "N/A"
    if abs(score) >= 1000:
        mate_in = 10000 // abs(score)
        return f"M{mate_in}" if score > 0 else f"-M{mate_in}"
    return f"{score/100:+.2f}"


def draw_position_bar(eval_score, width=50):
    """Draw a visual bar showing position evaluation."""
    if eval_score is None:
        return "=" * width
    
    # Normalize score to -10 to +10 range
    normalized = max(-10, min(10, eval_score / 100))
    
    # Calculate white advantage (0 to width)
    white_portion = int((normalized + 10) / 20 * width)
    white_portion = max(0, min(width, white_portion))
    
    bar = "█" * white_portion + "░" * (width - white_portion)
    return f"[{bar}] {format_evaluation(eval_score)}"


def display_board(board, title="", show_unicode=True):
    """
    Display the chess board in the terminal.
    
    Args:
        board: chess.Board object
        title: Optional title to display above the board
        show_unicode: Use Unicode pieces (True) or ASCII (False)
    """
    print("\n" + "─" * 40)
    if title:
        print(f"  {title}")
        print("─" * 40)
    
    if show_unicode:
        # Unicode board with borders
        print(board.unicode(borders=True, empty_square='·'))
    else:
        # Simple ASCII representation
        print(board)
    
    print("─" * 40)


def analyze_game_performance(pgn_string, target_player, stockfish_path="/usr/local/bin/stockfish", show_boards=True):
    """
    Analyze a chess game with phase-specific accuracy and move-by-move feedback.
    
    Args:
        pgn_string: PGN string of the game
        target_player: Username to focus analysis on
        stockfish_path: Path to Stockfish engine executable
        show_boards: Whether to display board positions for key moves
    
    Returns:
        Dictionary with comprehensive analysis results
    """
    
    # Parse the PGN
    pgn = io.StringIO(pgn_string)
    game = chess.pgn.read_game(pgn)
    
    # Determine which color the target player is
    white_name = game.headers.get("White", "")
    black_name = game.headers.get("Black", "")
    
    if target_player.lower() in white_name.lower():
        target_color = chess.WHITE
        opponent_name = black_name
        print(f"\n🎯 Analyzing {white_name} (White) vs {black_name} (Black)")
    elif target_player.lower() in black_name.lower():
        target_color = chess.BLACK
        opponent_name = white_name
        print(f"\n🎯 Analyzing {black_name} (Black) vs {white_name} (White)")
    else:
        print(f"⚠️  Warning: '{target_player}' not found. Analyzing White player.")
        target_color = chess.WHITE
        opponent_name = black_name
    
    # Get player ratings from headers
    white_elo = int(game.headers.get("WhiteElo", 0))
    black_elo = int(game.headers.get("BlackElo", 0))
    target_elo = white_elo if target_color == chess.WHITE else black_elo
    opponent_elo = black_elo if target_color == chess.WHITE else white_elo
    
    # Get game result
    result = game.headers.get("Result", "*")
    if result == "1-0":
        white_score, black_score = 1.0, 0.0
    elif result == "0-1":
        white_score, black_score = 0.0, 1.0
    else:
        white_score, black_score = 0.5, 0.5
    
    target_score = white_score if target_color == chess.WHITE else black_score
    
    # Initialize Stockfish with optimized settings
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    engine.configure({"Hash": 256, "Threads": 4})  # Adjust based on your system
    
    # Analysis data structures
    board = game.board()
    move_analysis = []
    
    # Phase-specific tracking
    phase_data = {
        'opening': {'errors': [], 'moves': []},
        'middlegame': {'errors': [], 'moves': []},
        'endgame': {'errors': [], 'moves': []}
    }
    
    move_number = 1
    half_move = 0
    
    print("\n" + "="*80)
    print("MOVE-BY-MOVE ANALYSIS")
    print("="*80)
    
    # Analyze each move
    for move in game.mainline_moves():
        current_phase = detect_game_phase(board, move_number)
        is_target_move = (board.turn == target_color)
        
        # Get best move and evaluation before the move
        info_before = engine.analyse(board, chess.engine.Limit(depth=18))
        best_move = info_before.get("pv", [None])[0]
        eval_before = info_before["score"].white().score(mate_score=10000)
        
        # Convert move to SAN BEFORE pushing
        played_move = move
        move_san = board.san(move)
        best_move_san = board.san(best_move) if best_move else None
        
        # Make the move
        board.push(move)
        
        # Get evaluation after the move
        info_after = engine.analyse(board, chess.engine.Limit(depth=18))
        eval_after = info_after["score"].white().score(mate_score=10000)
        
        # Calculate centipawn loss
        if eval_before is not None and eval_after is not None:
            if board.turn == chess.BLACK:  # White just moved
                cp_loss = max(0, eval_before - eval_after)
            else:  # Black just moved
                cp_loss = max(0, eval_after - eval_before)
        else:
            cp_loss = 0
        
        quality, symbol = classify_move_quality(cp_loss)
        
        # Store move analysis
        move_info = {
            'move_number': move_number,
            'half_move': half_move,
            'phase': current_phase,
            'move': played_move.uci(),
            'move_san': move_san,
            'best_move': best_move.uci() if best_move else None,
            'best_move_san': best_move_san,
            'eval_before': eval_before,
            'eval_after': eval_after,
            'cp_loss': cp_loss,
            'quality': quality,
            'symbol': symbol,
            'is_target': is_target_move
        }
        
        # Add to phase tracking
        if is_target_move:
            phase_data[current_phase]['errors'].append(cp_loss)
            phase_data[current_phase]['moves'].append(move_info)
        
        move_analysis.append(move_info)
        
        # Print move analysis (only for target player or significant opponent moves)
        if is_target_move or cp_loss > 50:
            color_indicator = "●" if is_target_move else "○"
            player = target_player if is_target_move else opponent_name
            
            print(f"\nMove {move_number}{'.' if board.turn == chess.BLACK else '...'} "
                  f"{color_indicator} {player} - {current_phase.upper()}")
            print(f"  Played: {move_san} {symbol}")
            
            if best_move and played_move != best_move:
                print(f"  Best:   {best_move_san}")
            
            print(f"  Eval:   {draw_position_bar(eval_after, width=40)}")
            print(f"  Loss:   {cp_loss} centipawns - {quality}")
            
            # Show board for significant moves
            if show_boards and is_target_move and cp_loss > 50:
                display_board(board, f"Position after {move_san}")
            
            # Provide suggestion for target player
            if is_target_move and cp_loss > 25:
                if cp_loss <= 50:
                    suggestion = "Minor inaccuracy. Consider alternative moves."
                elif cp_loss <= 100:
                    suggestion = "Mistake! The position required more careful calculation."
                elif cp_loss <= 300:
                    suggestion = "⚠️  BLUNDER! This move significantly worsened your position."
                else:
                    suggestion = "🚨 SEVERE BLUNDER! This move was critical. Review this carefully."
                
                print(f"  💡 Tip: {suggestion}")
        
        # Update move counter
        if board.turn == chess.WHITE:
            move_number += 1
        half_move += 1
    
    # Show final position
    if show_boards:
        display_board(board, "Final Position")
    
    engine.quit()
    
    # Calculate phase-specific accuracy
    def calculate_phase_accuracy(errors):
        if not errors:
            return 100.0
        avg_loss = sum(errors) / len(errors)
        return round(max(0, 100 - avg_loss/5), 1)
    
    opening_accuracy = calculate_phase_accuracy(phase_data['opening']['errors'])
    middlegame_accuracy = calculate_phase_accuracy(phase_data['middlegame']['errors'])
    endgame_accuracy = calculate_phase_accuracy(phase_data['endgame']['errors'])
    
    # Overall accuracy
    all_errors = (phase_data['opening']['errors'] + 
                  phase_data['middlegame']['errors'] + 
                  phase_data['endgame']['errors'])
    overall_accuracy = calculate_phase_accuracy(all_errors)
    overall_avg_loss = sum(all_errors) / len(all_errors) if all_errors else 0
    
    # Count mistakes by category
    blunders = sum(1 for m in move_analysis if m['is_target'] and m['cp_loss'] >= 300)
    mistakes = sum(1 for m in move_analysis if m['is_target'] and 100 <= m['cp_loss'] < 300)
    inaccuracies = sum(1 for m in move_analysis if m['is_target'] and 50 <= m['cp_loss'] < 100)
    
    return {
        'target_player': target_player,
        'target_color': 'White' if target_color == chess.WHITE else 'Black',
        'opponent': opponent_name,
        'target_elo': target_elo,
        'opponent_elo': opponent_elo,
        'result': result,
        'target_score': target_score,
        'overall_accuracy': overall_accuracy,
        'overall_avg_loss': round(overall_avg_loss, 2),
        'opening_accuracy': opening_accuracy,
        'opening_moves': len(phase_data['opening']['errors']),
        'middlegame_accuracy': middlegame_accuracy,
        'middlegame_moves': len(phase_data['middlegame']['errors']),
        'endgame_accuracy': endgame_accuracy,
        'endgame_moves': len(phase_data['endgame']['errors']),
        'blunders': blunders,
        'mistakes': mistakes,
        'inaccuracies': inaccuracies,
        'move_analysis': move_analysis,
        'phase_data': phase_data
    }


def print_summary(results):
    """Print formatted summary of analysis."""
    print("\n" + "="*80)
    print("📊 PERFORMANCE SUMMARY")
    print("="*80)
    
    print(f"\nPlayer: {results['target_player']} ({results['target_color']})")
    print(f"Rating: {results['target_elo']}")
    print(f"Result: {results['result']} - {'WIN' if results['target_score'] == 1.0 else 'LOSS' if results['target_score'] == 0.0 else 'DRAW'}")
    
    print(f"\n{'='*80}")
    print("ACCURACY BY PHASE")
    print(f"{'='*80}")
    print(f"  Opening:    {results['opening_accuracy']:5.1f}%  ({results['opening_moves']} moves)")
    print(f"  Middlegame: {results['middlegame_accuracy']:5.1f}%  ({results['middlegame_moves']} moves)")
    print(f"  Endgame:    {results['endgame_accuracy']:5.1f}%  ({results['endgame_moves']} moves)")
    print(f"  Overall:    {results['overall_accuracy']:5.1f}%")
    
    print(f"\n{'='*80}")
    print("MOVE QUALITY BREAKDOWN")
    print(f"{'='*80}")
    print(f"  Inaccuracies (?!): {results['inaccuracies']}")
    print(f"  Mistakes (?):      {results['mistakes']}")
    print(f"  Blunders (??):     {results['blunders']}")
    print(f"  Avg CP Loss:       {results['overall_avg_loss']:.2f}")
    
    # Key suggestions
    print(f"\n{'='*80}")
    print("💡 KEY SUGGESTIONS")
    print(f"{'='*80}")
    
    if results['opening_accuracy'] < 85:
        print("  📚 Opening: Study opening theory more. Your early-game moves need improvement.")
    if results['middlegame_accuracy'] < 85:
        print("  ⚔️  Middlegame: Work on tactical awareness and calculation during complex positions.")
    if results['endgame_accuracy'] < 85:
        print("  ♟️  Endgame: Practice endgame technique and pawn promotion strategies.")
    
    if results['blunders'] > 0:
        print(f"  🚨 You had {results['blunders']} blunder(s). Review these moves carefully!")
    
    if results['overall_accuracy'] >= 90:
        print("  ⭐ Excellent game! Your accuracy was very high.")
    elif results['overall_accuracy'] >= 80:
        print("  ✓ Good game overall, but there's room for improvement.")
    else:
        print("  ⚠️  This game had significant errors. Focus on calculation and pattern recognition.")
    
    print("="*80)


# Main execution
if __name__ == "__main__":
    pgn_string = """[Event "Live Chess"]
[Site "Chess.com"]
[Date "2025.11.10"]
[Round "?"]
[White "jaideepbommidi"]
[Black "13ruce"]
[Result "1-0"]
[TimeControl "300"]
[WhiteElo "286"]
[BlackElo "286"]
[Termination "jaideepbommidi won by resignation"]
[Link "https://www.chess.com/game/145364453634"]

1. d4 {[%clk 0:04:56.6][%timestamp 34]} 1... b6 {[%clk 0:04:52.5][%timestamp
75]} 2. e3 {[%clk 0:04:48.2][%timestamp 84]} 2... c5 {[%clk
0:04:51.4][%timestamp 11]} 3. d5 {[%clk 0:04:37.7][%timestamp 105]} 3... Nf6
{[%clk 0:04:46][%timestamp 54]} 4. Nc3 {[%clk 0:04:24.2][%timestamp 135]} 4...
Bb7 {[%clk 0:04:37.7][%timestamp 83]} 5. e4 {[%clk 0:04:20.3][%timestamp 39]}
5... e6 {[%clk 0:04:33.1][%timestamp 46]} 6. e5 {[%clk 0:04:08][%timestamp 123]}
6... Nxd5 {[%clk 0:04:29.9][%timestamp 32]} 7. Nxd5 {[%clk 0:04:01.9][%timestamp
61]} 7... exd5 {[%clk 0:04:28.4][%timestamp 15]} 8. Nf3 {[%clk
0:03:55.6][%timestamp 63]} 8... Nc6 {[%clk 0:04:17.1][%timestamp 113]} 9. Bg5
{[%clk 0:03:52][%timestamp 36]} 9... Ne7 {[%clk 0:04:08.5][%timestamp 86]} 10.
Bb5 {[%clk 0:03:31.1][%timestamp 209]} 10... Bc6 {[%clk 0:04:04][%timestamp 45]}
11. Bxc6 {[%clk 0:03:26.6][%timestamp 45]} 11... dxc6 {[%clk
0:04:02.6][%timestamp 14]} 12. O-O {[%clk 0:03:08.9][%timestamp 177]} 12... f6
{[%clk 0:03:52.2][%timestamp 104]} 13. exf6 {[%clk 0:03:05.8][%timestamp 31]}
13... gxf6 {[%clk 0:03:48.9][%timestamp 33]} 14. Bxf6 {[%clk
0:03:02.2][%timestamp 36]} 14... Qd6 {[%clk 0:03:41.4][%timestamp 75]} 15. Bxh8
{[%clk 0:02:55.9][%timestamp 63]} 15... Ng6 {[%clk 0:03:40.1][%timestamp 13]}
16. Bc3 {[%clk 0:02:44.5][%timestamp 114]} 16... d4 {[%clk 0:03:38][%timestamp
21]} 17. Bd2 {[%clk 0:02:41.4][%timestamp 31]} 17... Nf4 {[%clk
0:03:31.9][%timestamp 61]} 18. Bxf4 {[%clk 0:02:33.1][%timestamp 83]} 18... Qxf4
{[%clk 0:03:30.5][%timestamp 14]} 19. Re1+ {[%clk 0:02:32.2][%timestamp 9]}
19... Be7 {[%clk 0:03:28.6][%timestamp 19]} 20. g3 {[%clk 0:02:14.9][%timestamp
173]} 20... Qd6 {[%clk 0:03:12.4][%timestamp 162]} 21. Ne5 {[%clk
0:01:56.3][%timestamp 186]} 21... O-O-O {[%clk 0:03:09.1][%timestamp 33]} 22.
Nf7 {[%clk 0:01:51.9][%timestamp 44]} 22... Qf6 {[%clk 0:02:59][%timestamp 101]}
23. Nxd8 {[%clk 0:01:45.6][%timestamp 63]} 23... Kxd8 {[%clk
0:02:56.2][%timestamp 28]} 24. Qe2 {[%clk 0:01:34][%timestamp 116]} 24... Ke8
{[%clk 0:02:23][%timestamp 332]} 25. c3 {[%clk 0:01:28.6][%timestamp 54]} 25...
dxc3 {[%clk 0:02:19.3][%timestamp 37]} 26. bxc3 {[%clk 0:01:25.7][%timestamp
29]} 26... c4 {[%clk 0:02:15.4][%timestamp 39]} 27. Rab1 {[%clk
0:01:19][%timestamp 67]} 27... b5 {[%clk 0:02:13.3][%timestamp 21]} 28. Red1
{[%clk 0:01:11.7][%timestamp 73]} 28... Qxc3 {[%clk 0:02:10.4][%timestamp 29]}
29. a3 {[%clk 0:01:05.1][%timestamp 66]} 29... Qxa3 {[%clk 0:02:07.9][%timestamp
25]} 30. Qh5+ {[%clk 0:01:02.6][%timestamp 25]} 30... Kf8 {[%clk
0:02:04][%timestamp 39]} 31. f4 {[%clk 0:00:59.2][%timestamp 34]} 31... Qe3+
{[%clk 0:01:56.2][%timestamp 78]} 32. Kg2 {[%clk 0:00:55.4][%timestamp 38]}
32... Bc5 {[%clk 0:01:52.3][%timestamp 39]} 33. Kh3 {[%clk 0:00:51.4][%timestamp
40]} 33... Qe6+ {[%clk 0:01:44.6][%timestamp 77]} 34. Qg4 {[%clk
0:00:48.5][%timestamp 29]} 34... Qh6+ {[%clk 0:01:40.9][%timestamp 37]} 35. Kg2
{[%clk 0:00:46.1][%timestamp 24]} 35... Qe6 {[%clk 0:01:30.1][%timestamp 108]}
36. Qxe6 {[%clk 0:00:43.9][%timestamp 22]} 1-0"""

    # Update stockfish_path to your installation
    # For Windows: r"C:\path\to\stockfish.exe"
    # For Mac/Linux: "/usr/local/bin/stockfish"
    
    results = analyze_game_performance(
        pgn_string, 
        target_player="jaideepbommidi",
        stockfish_path=r"C:\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe",
        show_boards=True  # Set to False to hide boards
    )
    
    print_summary(results)
