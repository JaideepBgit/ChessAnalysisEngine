import chess
import chess.pgn
import chess.engine
import io
import os
import sys

# ANSI Color codes
class Colors:
    RESET = '\033[0m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_RED = '\033[41m'

# Cross-platform keyboard input
if os.name == 'nt':  # Windows
    import msvcrt
    os.system('')  # Enable ANSI colors
    
    def wait_for_key():
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\xe0':
                    key = msvcrt.getch()
                    if key == b'H': return 'UP'
                    elif key == b'P': return 'DOWN'
                    elif key == b'K': return 'LEFT'
                    elif key == b'M': return 'RIGHT'
                elif key == b'\x03': raise KeyboardInterrupt
                elif key == b'\r' or key == b' ': return 'SPACE'
                elif key == b'q': return 'QUIT'
            
else:  # Unix/Linux/Mac
    import termios
    import tty
    
    def wait_for_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'UP'
                    elif ch3 == 'B': return 'DOWN'
                    elif ch3 == 'C': return 'RIGHT'
                    elif ch3 == 'D': return 'LEFT'
            elif ch == '\x03': raise KeyboardInterrupt
            elif ch == '\r' or ch == '\n' or ch == ' ': return 'SPACE'
            elif ch == 'q': return 'QUIT'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_board_lines(board, highlight_move=None, color='blue', flipped=False):
    """
    Get chess board as list of strings with optional move highlighting.
    
    Args:
        board: chess.Board object
        highlight_move: chess.Move to highlight
        color: 'blue' for played move, 'green' for best move
        flipped: If True, show board from black's perspective
    """
    piece_symbols = {
        'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
        'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
        '.': '·'
    }
    
    if color == 'blue':
        from_color = Colors.BG_BLUE
        to_color = Colors.BG_BLUE
    else:
        from_color = Colors.BG_GREEN
        to_color = Colors.BG_GREEN
    
    lines = []
    lines.append("   ┌───────────────────────┐")
    
    # Determine rank order based on orientation
    rank_range = range(7, -1, -1) if not flipped else range(8)
    
    for rank in rank_range:
        row = f" {rank + 1} │"
        
        # Determine file order based on orientation
        file_range = range(8) if not flipped else range(7, -1, -1)
        
        for file in file_range:
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            symbol = piece_symbols[piece.symbol()] if piece else piece_symbols['.']
            
            if highlight_move:
                if square == highlight_move.from_square:
                    symbol = from_color + symbol + Colors.RESET
                elif square == highlight_move.to_square:
                    symbol = to_color + symbol + Colors.RESET
            
            row += ' ' + symbol + ' '  # Add spacing around pieces
        
        lines.append(row + '│')
        if (not flipped and rank > 0) or (flipped and rank < 7):
            lines.append("   ├───────────────────────┤")
    
    lines.append("   └───────────────────────┘")
    
    # File labels
    if not flipped:
        lines.append("     a  b  c  d  e  f  g  h")
    else:
        lines.append("     h  g  f  e  d  c  b  a")
    
    return lines


def draw_side_by_side_boards(board_before_move, played_move, best_move, flipped=False):
    """
    Draw two boards side by side: actual position vs best move position.
    
    Args:
        board_before_move: Board position before the move
        played_move: The move that was actually played
        best_move: The best move according to engine
        flipped: If True, show boards from black's perspective
    """
    board_played = board_before_move.copy()
    board_played.push(played_move)
    
    board_best = board_before_move.copy()
    if best_move and best_move != played_move:
        board_best.push(best_move)
    else:
        board_best = board_played.copy()
    
    played_lines = get_board_lines(board_played, highlight_move=played_move, color='blue', flipped=flipped)
    best_lines = get_board_lines(board_best, highlight_move=best_move, color='green', flipped=flipped)
    
    print(f"\n    {Colors.BLUE}━━━━ YOUR MOVE ━━━━{Colors.RESET}" + " " * 10 + 
          f"{Colors.GREEN}━━━━ BEST MOVE ━━━━{Colors.RESET}")
    
    for played_line, best_line in zip(played_lines, best_lines):
        print(f" {played_line}      {best_line}")


def classify_move_quality(centipawn_loss):
    """Classify move quality based on centipawn loss."""
    if centipawn_loss <= 10:
        return "Excellent ✓"
    elif centipawn_loss <= 25:
        return "Good"
    elif centipawn_loss <= 50:
        return "Inaccuracy ?!"
    elif centipawn_loss <= 100:
        return "Mistake ?"
    elif centipawn_loss <= 300:
        return "Blunder ??"
    else:
        return "Severe Blunder ???"


def calculate_accuracy(centipawn_losses):
    """Calculate accuracy percentage from centipawn losses."""
    if not centipawn_losses:
        return 100.0
    avg_loss = sum(centipawn_losses) / len(centipawn_losses)
    accuracy = max(0, 100 - avg_loss / 5)
    return round(accuracy, 1)


def calculate_performance_rating(accuracy, base_rating, opponent_rating, score):
    """
    Calculate performance rating based on accuracy and game result.
    
    Uses Chess.com-style formula: Accuracy ≈ Rating/100 + 64
    Combined with FIDE performance rating
    """
    accuracy_rating = (accuracy - 64) * 100
    
    if score == 1.0:
        fide_performance = opponent_rating + 400
    elif score == 0.0:
        fide_performance = opponent_rating - 400
    else:
        fide_performance = opponent_rating
    
    performance = int(0.7 * accuracy_rating + 0.3 * fide_performance)
    
    return accuracy_rating, fide_performance, performance


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


def format_evaluation(score):
    """Format chess engine evaluation score."""
    if score is None:
        return "N/A"
    if abs(score) >= 1000:
        mate_in = 10000 // abs(score)
        return f"M{mate_in}" if score > 0 else f"-M{mate_in}"
    return f"{score/100:+.2f}"


def interactive_game_analysis(pgn_string, target_player, stockfish_path):
    """
    Interactive chess game analysis with rating tracking.
    
    Controls:
    - RIGHT ARROW / SPACE: Next move
    - LEFT ARROW: Previous move
    - Q / Ctrl+C: Quit
    """
    # Parse the PGN
    pgn = io.StringIO(pgn_string)
    game = chess.pgn.read_game(pgn)
    
    # Determine target player
    white_name = game.headers.get("White", "White")
    black_name = game.headers.get("Black", "Black")
    
    if target_player.lower() in white_name.lower():
        target_color = chess.WHITE
        opponent_name = black_name
    elif target_player.lower() in black_name.lower():
        target_color = chess.BLACK
        opponent_name = white_name
    else:
        target_color = chess.WHITE
        opponent_name = black_name
    
    # Determine if board should be flipped (show target player at bottom)
    flipped = (target_color == chess.BLACK)
    
    # Get ratings
    white_elo = int(game.headers.get("WhiteElo", 1500))
    black_elo = int(game.headers.get("BlackElo", 1500))
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
    
    # Get all moves
    moves = list(game.mainline_moves())
    
    # Initialize engine
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    engine.configure({"Hash": 256, "Threads": 4})
    
    # Pre-analyze all positions
    print("Analyzing game with Stockfish...")
    board = game.board()
    move_data = []
    
    for idx, move in enumerate(moves):
        info_before = engine.analyse(board, chess.engine.Limit(depth=18))
        best_move = info_before.get("pv", [None])[0]
        eval_before = info_before["score"].white().score(mate_score=10000)
        
        move_san = board.san(move)
        best_move_san = board.san(best_move) if best_move else None
        board_before = board.copy()
        
        board.push(move)
        
        info_after = engine.analyse(board, chess.engine.Limit(depth=18))
        eval_after = info_after["score"].white().score(mate_score=10000)
        
        if eval_before is not None and eval_after is not None:
            if board.turn == chess.BLACK:
                cp_loss = max(0, eval_before - eval_after)
            else:
                cp_loss = max(0, eval_after - eval_before)
        else:
            cp_loss = 0
        
        quality = classify_move_quality(cp_loss)
        is_target = (idx % 2 == (0 if target_color == chess.WHITE else 1))
        
        move_data.append({
            'board_before': board_before,
            'move': move,
            'move_san': move_san,
            'best_move': best_move,
            'best_move_san': best_move_san,
            'eval_before': eval_before,
            'eval_after': eval_after,
            'cp_loss': cp_loss,
            'quality': quality,
            'is_target': is_target
        })
        
        print(f"  Analyzed move {idx + 1}/{len(moves)}")
    
    engine.quit()
    
    # Build position history
    current_position = 0
    board = game.board()
    board_history = [board.copy()]
    
    for move in moves:
        board.push(move)
        board_history.append(board.copy())
    
    # Calculate overall statistics
    target_cp_losses = [m['cp_loss'] for m in move_data if m['is_target']]
    overall_accuracy = calculate_accuracy(target_cp_losses)
    
    # Count move quality
    excellent = sum(1 for m in move_data if m['is_target'] and m['cp_loss'] <= 10)
    good = sum(1 for m in move_data if m['is_target'] and 10 < m['cp_loss'] <= 25)
    inaccuracies = sum(1 for m in move_data if m['is_target'] and 25 < m['cp_loss'] <= 50)
    mistakes = sum(1 for m in move_data if m['is_target'] and 50 < m['cp_loss'] <= 100)
    blunders = sum(1 for m in move_data if m['is_target'] and 100 < m['cp_loss'] <= 300)
    severe_blunders = sum(1 for m in move_data if m['is_target'] and m['cp_loss'] > 300)
    
    # Calculate performance ratings
    accuracy_rating, fide_performance, combined_performance = calculate_performance_rating(
        overall_accuracy, target_elo, opponent_elo, target_score
    )
    
    print("\n✓ Analysis complete! Starting interactive mode...\n")
    print("Controls:")
    print("  RIGHT/SPACE: Next move")
    print("  LEFT: Previous move")
    print("  Q: Quit\n")
    print("Press any key to start...")
    wait_for_key()
    
    try:
        while True:
            clear_screen()
            
            current_board = board_history[current_position]
            
            # Display header
            print(f"\n{'='*90}")
            color_indicator = f"{Colors.BOLD}[YOU]{Colors.RESET}" if target_color == chess.WHITE else ""
            opponent_indicator = f"{Colors.BOLD}[YOU]{Colors.RESET}" if target_color == chess.BLACK else ""
            print(f"  {white_name} ({white_elo}) {color_indicator}  vs  {black_name} ({black_elo}) {opponent_indicator}")
            print(f"{'='*90}")
            
            # Move info and boards
            if current_position == 0:
                print(f"\n  {Colors.BOLD}Initial Position{Colors.RESET}\n")
                lines = get_board_lines(current_board, flipped=flipped)
                for line in lines:
                    print(f"   {line}")
            else:
                data = move_data[current_position - 1]
                move_num = (current_position + 1) // 2
                is_white_move = (current_position % 2 == 1)
                player = white_name if is_white_move else black_name
                
                print(f"\n  {Colors.BOLD}Move {move_num}{'.' if is_white_move else '...'} "
                      f"{data['move_san']} by {player}{Colors.RESET} - {data['quality']}")
                
                draw_side_by_side_boards(
                    data['board_before'],
                    data['move'],
                    data['best_move'],
                    flipped=flipped
                )
                
                print(f"\n  {Colors.BLUE}■{Colors.RESET} Played: {chess.square_name(data['move'].from_square)} → "
                      f"{chess.square_name(data['move'].to_square)} ({data['move_san']})")
                
                if data['best_move'] and data['move'] != data['best_move']:
                    print(f"  {Colors.GREEN}■{Colors.RESET} Best:   {chess.square_name(data['best_move'].from_square)} → "
                          f"{chess.square_name(data['best_move'].to_square)} ({data['best_move_san']})")
                else:
                    print(f"  {Colors.GREEN}■{Colors.RESET} Best move matches played move ✓")
            
            # Stats section
            print(f"\n{'─'*90}")
            print("  POSITION STATS")
            print(f"{'─'*90}")
            print(f"  Material: White {count_material(current_board, chess.WHITE)} | "
                  f"Black {count_material(current_board, chess.BLACK)}")
            
            if current_position > 0:
                data = move_data[current_position - 1]
                print(f"  Evaluation: {format_evaluation(data['eval_after'])}")
                print(f"  CP Loss: {data['cp_loss']} centipawns")
                
                # Calculate running accuracy up to this point
                moves_so_far = [m['cp_loss'] for m in move_data[:current_position] if m['is_target']]
                if moves_so_far:
                    running_accuracy = calculate_accuracy(moves_so_far)
                    print(f"  {target_player}'s Running Accuracy: {running_accuracy}%")
                
                if data['is_target'] and data['cp_loss'] > 25:
                    print(f"\n  💡 {Colors.YELLOW}Suggestion for {target_player}:{Colors.RESET}")
                    if data['cp_loss'] <= 50:
                        print(f"     Minor inaccuracy. Study the position more carefully.")
                    elif data['cp_loss'] <= 100:
                        print(f"     Mistake! This position required deeper calculation.")
                    elif data['cp_loss'] <= 300:
                        print(f"     ⚠️  BLUNDER! This move significantly damaged your position.")
                    else:
                        print(f"     🚨 SEVERE BLUNDER! Critical mistake - review thoroughly!")
            
            # Rating Performance Summary (shown on last position)
            if current_position == len(board_history) - 1:
                print(f"\n{'─'*90}")
                print(f"  {Colors.BOLD}GAME SUMMARY - {target_player}{Colors.RESET}")
                print(f"{'─'*90}")
                print(f"  Current Rating:     {target_elo}")
                print(f"  Opponent Rating:    {opponent_elo}")
                print(f"  Game Result:        {result} ({'WIN ✓' if target_score == 1.0 else 'LOSS ✗' if target_score == 0.0 else 'DRAW ='})") 
                print(f"\n  Overall Accuracy:   {overall_accuracy}%")
                print(f"  Avg CP Loss:        {sum(target_cp_losses)/len(target_cp_losses):.1f}" if target_cp_losses else "  Avg CP Loss:        0.0")
                print(f"\n  Move Quality Breakdown:")
                print(f"    Excellent (≤10):    {excellent}")
                print(f"    Good (11-25):       {good}")
                print(f"    Inaccurate (26-50): {inaccuracies}")
                print(f"    Mistakes (51-100):  {mistakes}")
                print(f"    Blunders (101-300): {blunders}")
                print(f"    Severe (>300):      {severe_blunders}")
                print(f"\n  {Colors.BOLD}PERFORMANCE RATINGS:{Colors.RESET}")
                print(f"    Accuracy-Based:  {int(accuracy_rating)} (from {overall_accuracy}% accuracy)")
                print(f"    Result-Based:    {fide_performance} (FIDE method)")
                print(f"    Combined:        {combined_performance}")
                print(f"\n  {Colors.CYAN}Rating Explanation:{Colors.RESET}")
                print(f"    Your {overall_accuracy}% accuracy suggests you played at ~{int(accuracy_rating)} level.")
                if combined_performance > target_elo:
                    print(f"    {Colors.GREEN}You performed {combined_performance - target_elo} points above your rating! 📈{Colors.RESET}")
                elif combined_performance < target_elo:
                    print(f"    {Colors.RED}You performed {target_elo - combined_performance} points below your rating. 📉{Colors.RESET}")
                else:
                    print(f"    You performed exactly at your rating level.")
            
            # Navigation info
            print(f"\n{'─'*90}")
            print(f"  Position: {current_position}/{len(board_history) - 1}")
            print(f"  Controls: {Colors.CYAN}[←]{Colors.RESET} Previous | "
                  f"{Colors.CYAN}[→/SPACE]{Colors.RESET} Next | "
                  f"{Colors.CYAN}[Q]{Colors.RESET} Quit")
            print(f"{'─'*90}")
            
            # Wait for input
            key = wait_for_key()
            
            if key == 'RIGHT' or key == 'SPACE':
                if current_position < len(board_history) - 1:
                    current_position += 1
            elif key == 'LEFT':
                if current_position > 0:
                    current_position -= 1
            elif key == 'QUIT':
                break
    
    except KeyboardInterrupt:
        pass
    
    clear_screen()
    print("\n✓ Analysis session ended.\n")


if __name__ == "__main__":
    pgn_string = """[Event "Live Chess"]
[Site "Chess.com"]
[Date "2025.11.11"]
[Round "?"]
[White "pretzelaf"]
[Black "jaideepbommidi"]
[Result "1/2-1/2"]
[TimeControl "300"]
[WhiteElo "318"]
[BlackElo "310"]
[Termination "Game drawn by insufficient material"]
[Link "https://www.chess.com/game/145401616710"]

1. e4 {[%clk 0:04:59.1][%timestamp 9]} 1... e5 {[%clk 0:04:59.8][%timestamp 2]}
2. Nf3 {[%clk 0:04:57.7][%timestamp 14]} 2... Nc6 {[%clk 0:04:56.9][%timestamp
29]} 3. d4 {[%clk 0:04:53.2][%timestamp 45]} 3... Bb4+ {[%clk
0:04:50.3][%timestamp 66]} 4. Bd2 {[%clk 0:04:48.4][%timestamp 48]} 4... Bxd2+
{[%clk 0:04:49.1][%timestamp 12]} 5. Qxd2 {[%clk 0:04:46.8][%timestamp 16]} 5...
d6 {[%clk 0:04:46.7][%timestamp 24]} 6. d5 {[%clk 0:04:45.4][%timestamp 14]}
6... Nd4 {[%clk 0:04:39.9][%timestamp 68]} 7. Nxd4 {[%clk 0:04:25.4][%timestamp
200]} 7... exd4 {[%clk 0:04:37.7][%timestamp 22]} 8. Qxd4 {[%clk
0:04:23][%timestamp 24]} 8... Nf6 {[%clk 0:04:32.6][%timestamp 51]} 9. e5 {[%clk
0:04:18.6][%timestamp 44]} 9... dxe5 {[%clk 0:04:20][%timestamp 126]} 10. Qxe5+
{[%clk 0:04:16][%timestamp 26]} 10... Qe7 {[%clk 0:04:13][%timestamp 70]} 11.
Qxe7+ {[%clk 0:04:13.7][%timestamp 23]} 11... Kxe7 {[%clk 0:04:09.4][%timestamp
36]} 12. Bc4 {[%clk 0:04:08.3][%timestamp 54]} 12... c6 {[%clk
0:04:03][%timestamp 64]} 13. dxc6 {[%clk 0:04:01.9][%timestamp 64]} 13... bxc6
{[%clk 0:04:00.2][%timestamp 28]} 14. O-O {[%clk 0:03:59.4][%timestamp 25]}
14... Re8 {[%clk 0:03:51.3][%timestamp 89]} 15. Nc3 {[%clk 0:03:48.5][%timestamp
109]} 15... Rb8 {[%clk 0:03:47.1][%timestamp 42]} 16. b3 {[%clk
0:03:45.4][%timestamp 31]} 16... Be6 {[%clk 0:03:45.2][%timestamp 19]} 17. Bxe6
{[%clk 0:03:37.3][%timestamp 81]} 17... Kxe6 {[%clk 0:03:40.9][%timestamp 43]}
18. Rfe1+ {[%clk 0:03:31.6][%timestamp 57]} 18... Kd7 {[%clk
0:03:37.5][%timestamp 34]} 19. Rxe8 {[%clk 0:03:24.8][%timestamp 68]} 19... Rxe8
{[%clk 0:03:32.8][%timestamp 47]} 20. Rd1+ {[%clk 0:03:22.2][%timestamp 26]}
20... Kc7 {[%clk 0:03:28.1][%timestamp 47]} 21. h3 {[%clk 0:03:14.7][%timestamp
75]} 21... Rd8 {[%clk 0:03:20.3][%timestamp 78]} 22. g4 {[%clk
0:02:56.1][%timestamp 186]} 22... Nd5 {[%clk 0:03:16][%timestamp 43]} 23. Nxd5+
{[%clk 0:02:50.3][%timestamp 58]} 23... cxd5 {[%clk 0:03:13.6][%timestamp 24]}
24. c4 {[%clk 0:02:39.5][%timestamp 108]} 24... dxc4 {[%clk
0:03:10.2][%timestamp 34]} 25. Rxd8 {[%clk 0:02:37.7][%timestamp 18]} 25... Kxd8
{[%clk 0:03:08.2][%timestamp 20]} 26. bxc4 {[%clk 0:02:36.7][%timestamp 10]}
26... Kd7 {[%clk 0:03:06.1][%timestamp 21]} 27. f4 {[%clk 0:02:31.5][%timestamp
52]} 27... Kc6 {[%clk 0:03:02.3][%timestamp 38]} 28. Kf2 {[%clk
0:02:30.6][%timestamp 9]} 28... Kc5 {[%clk 0:03:01.3][%timestamp 10]} 29. Ke3
{[%clk 0:02:22.1][%timestamp 85]} 29... Kxc4 {[%clk 0:03:00.3][%timestamp 10]}
30. g5 {[%clk 0:02:17.6][%timestamp 45]} 30... Kc3 {[%clk 0:02:58.6][%timestamp
17]} 31. h4 {[%clk 0:02:14.8][%timestamp 28]} 31... Kb2 {[%clk
0:02:57.5][%timestamp 11]} 32. f5 {[%clk 0:02:13.8][%timestamp 10]} 32... Kxa2
{[%clk 0:02:55.8][%timestamp 17]} 33. Ke4 {[%clk 0:02:11.7][%timestamp 21]}
33... Kb3 {[%clk 0:02:54.4][%timestamp 14]} 34. Kd5 {[%clk 0:02:10.8][%timestamp
9]} 34... a5 {[%clk 0:02:53.1][%timestamp 13]} 35. f6 {[%clk
0:02:09.1][%timestamp 17]} 35... gxf6 {[%clk 0:02:48.8][%timestamp 43]} 36. gxf6
{[%clk 0:02:07.8][%timestamp 13]} 36... a4 {[%clk 0:02:48.3][%timestamp 5]} 37.
Kd6 {[%clk 0:02:06.7][%timestamp 11]} 37... a3 {[%clk 0:02:47.8][%timestamp 5]}
38. Ke7 {[%clk 0:02:04.8][%timestamp 19]} 38... a2 {[%clk 0:02:46.8][%timestamp
10]} 39. Kxf7 {[%clk 0:02:04.1][%timestamp 7]} 39... a1=Q {[%clk
0:02:45.4][%timestamp 14]} 40. Kg7 {[%clk 0:02:02.8][%timestamp 13]} 40... Qh1
{[%clk 0:02:40.9][%timestamp 45]} 41. f7 {[%clk 0:02:01.1][%timestamp 17]} 41...
Qxh4 {[%clk 0:02:38.9][%timestamp 20]} 42. f8=Q {[%clk 0:01:58.7][%timestamp
24]} 42... Kc3 {[%clk 0:02:37.3][%timestamp 16]} 43. Qc8+ {[%clk
0:01:47.9][%timestamp 108]} 43... Kd4 {[%clk 0:02:35.5][%timestamp 18]} 44. Qd7+
{[%clk 0:01:38.5][%timestamp 94]} 44... Ke5 {[%clk 0:02:33.5][%timestamp 20]}
45. Qb5+ {[%clk 0:01:35.3][%timestamp 32]} 45... Kf4 {[%clk
0:02:32.5][%timestamp 10]} 46. Qb4+ {[%clk 0:01:23.2][%timestamp 121]} 46... Kg5
{[%clk 0:02:30.3][%timestamp 22]} 47. Qxh4+ {[%clk 0:01:19.2][%timestamp 40]}
47... Kxh4 {[%clk 0:02:28.6][%timestamp 17]} 48. Kxh7 {[%clk
0:01:18.2][%timestamp 10]} 1/2-1/2"""
    
    interactive_game_analysis(
        pgn_string, 
        target_player="jaideepbommidi",
        stockfish_path=r"C:\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"
    )
