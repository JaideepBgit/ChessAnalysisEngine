import chess
import chess.pgn
import chess.engine
import io


def analyze_game_performance(pgn_string, stockfish_path="/usr/local/bin/stockfish"):
    """
    Analyze a chess game and calculate performance ratings similar to Chess.com.
    
    Args:
        pgn_string: PGN string of the game
        stockfish_path: Path to Stockfish engine executable
    
    Returns:
        Dictionary with White and Black performance metrics
    """
    
    # Parse the PGN
    pgn = io.StringIO(pgn_string)
    game = chess.pgn.read_game(pgn)
    
    # Get player ratings from headers
    white_elo = int(game.headers.get("WhiteElo", 0))
    black_elo = int(game.headers.get("BlackElo", 0))
    
    # Get game result
    result = game.headers.get("Result", "*")
    if result == "1-0":
        white_score = 1.0
        black_score = 0.0
    elif result == "0-1":
        white_score = 0.0
        black_score = 1.0
    else:  # Draw
        white_score = 0.5
        black_score = 0.5
    
    # Initialize Stockfish
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    
    # Analysis parameters
    board = game.board()
    white_errors = []
    black_errors = []
    move_count = 0
    
    # Analyze each position
    for move in game.mainline_moves():
        # Get evaluation before the move
        info_before = engine.analyse(board, chess.engine.Limit(depth=15))
        eval_before = info_before["score"].white().score(mate_score=10000)
        
        # Make the move
        board.push(move)
        
        # Get evaluation after the move
        info_after = engine.analyse(board, chess.engine.Limit(depth=15))
        eval_after = info_after["score"].white().score(mate_score=10000)
        
        # Calculate centipawn loss
        if move_count % 2 == 0:  # White's move
            if eval_before is not None and eval_after is not None:
                error = eval_before - eval_after
                white_errors.append(max(0, error))
        else:  # Black's move
            if eval_before is not None and eval_after is not None:
                error = eval_after - eval_before
                black_errors.append(max(0, error))
        
        move_count += 1
    
    engine.quit()
    
    # Calculate average centipawn loss
    white_avg_loss = sum(white_errors) / len(white_errors) if white_errors else 0
    black_avg_loss = sum(black_errors) / len(black_errors) if black_errors else 0
    
    # Calculate accuracy (Chess.com style)
    white_accuracy = round(max(0, 100 - white_avg_loss/5), 1)
    black_accuracy = round(max(0, 100 - black_avg_loss/5), 1)
    
    # Calculate performance rating using Chess.com-style formula
    # Based on accuracy conversion: approximately 100 rating points per 1% accuracy
    # Range is centered around player's rating with max deviation of ±800
    
    def accuracy_to_performance(accuracy, player_rating):
        """
        Convert accuracy to performance rating (Chess.com style).
        Formula approximation: Each 4% accuracy ≈ 50 Elo
        Max deviation: ±800 from player rating
        """
        # Expected accuracy for the player's rating
        # Using formula: Accuracy ≈ Rating/100 + 64 (for ratings 400-2400)
        expected_accuracy = (player_rating / 100) + 64
        
        # Difference from expected
        accuracy_diff = accuracy - expected_accuracy
        
        # Convert to rating: ~12.5 Elo per 1% accuracy difference
        # This matches "every 4% accuracy = 50 Elo"
        rating_adjustment = accuracy_diff * 12.5
        
        # Cap at ±800
        rating_adjustment = max(-800, min(800, rating_adjustment))
        
        performance = player_rating + rating_adjustment
        return round(performance)
    
    white_performance = accuracy_to_performance(white_accuracy, white_elo)
    black_performance = accuracy_to_performance(black_accuracy, black_elo)
    
    # Calculate FIDE performance rating (for reference)
    if white_score == 1.0:
        white_performance_fide = black_elo + 400
    elif white_score == 0.0:
        white_performance_fide = black_elo - 400
    else:
        white_performance_fide = black_elo
    
    if black_score == 1.0:
        black_performance_fide = white_elo + 400
    elif black_score == 0.0:
        black_performance_fide = white_elo - 400
    else:
        black_performance_fide = white_elo
    
    return {
        "white_elo": white_elo,
        "black_elo": black_elo,
        "white_score": white_score,
        "black_score": black_score,
        "white_avg_centipawn_loss": round(white_avg_loss, 2),
        "black_avg_centipawn_loss": round(black_avg_loss, 2),
        "white_accuracy": white_accuracy,
        "black_accuracy": black_accuracy,
        "white_performance": white_performance,
        "black_performance": black_performance,
        "white_performance_fide": white_performance_fide,
        "black_performance_fide": black_performance_fide,
    }


# Your PGN
pgn_string = """[Event "Live Chess"]
[Site "Chess.com"]
[Date "2025.11.15"]
[Round "?"]
[White "Cesarsu1000"]
[Black "jaideepbommidi"]
[Result "0-1"]
[TimeControl "300"]
[WhiteElo "299"]
[BlackElo "318"]
[Termination "jaideepbommidi won on time"]
[Link "https://www.chess.com/game/145565031374"]

1. e4 {[%clk 0:04:59.5][%timestamp 5]} 1... e5 {[%clk 0:04:58.5][%timestamp 15]}
2. Nf3 {[%clk 0:04:59.4][%timestamp 1]} 2... Nc6 {[%clk 0:04:56.8][%timestamp
17]} 3. Bc4 {[%clk 0:04:58.9][%timestamp 5]} 3... Nf6 {[%clk
0:04:51.1][%timestamp 57]} 4. d3 {[%clk 0:04:56.3][%timestamp 26]} 4... a6
{[%clk 0:04:47][%timestamp 41]} 5. a3 {[%clk 0:04:54.6][%timestamp 17]} 5... Bc5
{[%clk 0:04:43.4][%timestamp 36]} 6. O-O {[%clk 0:04:50.1][%timestamp 45]} 6...
O-O {[%clk 0:04:42.2][%timestamp 12]} 7. c3 {[%clk 0:04:49.4][%timestamp 7]}
7... d6 {[%clk 0:04:34.7][%timestamp 75]} 8. b4 {[%clk 0:04:47.8][%timestamp
16]} 8... Bb6 {[%clk 0:04:27.6][%timestamp 71]} 9. Nbd2 {[%clk
0:04:42][%timestamp 58]} 9... Qe7 {[%clk 0:04:22.5][%timestamp 51]} 10. Bb2
{[%clk 0:04:19.6][%timestamp 224]} 10... a5 {[%clk 0:04:14][%timestamp 85]} 11.
b5 {[%clk 0:04:15][%timestamp 46]} 11... Nd8 {[%clk 0:04:03.1][%timestamp 109]}
12. a4 {[%clk 0:03:58][%timestamp 170]} 12... Be6 {[%clk 0:03:59.7][%timestamp
34]} 13. Ba3 {[%clk 0:03:28.4][%timestamp 296]} 13... Bxc4 {[%clk
0:03:52.1][%timestamp 76]} 14. dxc4 {[%clk 0:03:14.6][%timestamp 138]} 14... Bc5
{[%clk 0:03:44.7][%timestamp 74]} 15. Bb2 {[%clk 0:03:02.2][%timestamp 124]}
15... c6 {[%clk 0:03:30.5][%timestamp 142]} 16. bxc6 {[%clk
0:02:50.7][%timestamp 115]} 16... bxc6 {[%clk 0:03:17][%timestamp 135]} 17. Nb3
{[%clk 0:02:38.1][%timestamp 126]} 17... Nb7 {[%clk 0:02:53.9][%timestamp 231]}
18. Nxc5 {[%clk 0:02:22.6][%timestamp 155]} 18... Nxc5 {[%clk
0:02:51.9][%timestamp 20]} 19. Ba3 {[%clk 0:02:14.4][%timestamp 82]} 19... Ncxe4
{[%clk 0:02:45.2][%timestamp 67]} 20. Qe1 {[%clk 0:01:47.3][%timestamp 271]}
20... c5 {[%clk 0:02:31.9][%timestamp 133]} 21. Bb2 {[%clk 0:01:36.7][%timestamp
106]} 21... Rab8 {[%clk 0:02:19.8][%timestamp 121]} 22. Ba3 {[%clk
0:01:19.9][%timestamp 168]} 22... Rb3 {[%clk 0:02:05.8][%timestamp 140]} 23. Bc1
{[%clk 0:00:34.1][%timestamp 458]} 23... Rxc3 {[%clk 0:02:00.6][%timestamp 52]}
24. Bb2 {[%clk 0:00:22.4][%timestamp 117]} 24... Rxc4 {[%clk
0:01:49.9][%timestamp 107]} 25. Ba3 {[%clk 0:00:08.5][%timestamp 139]} 25... Rc3
{[%clk 0:01:39.6][%timestamp 103]} 26. Qe2 {[%clk 0:00:00.3][%timestamp 82]}
26... Rb3 {[%clk 0:01:32.5][%timestamp 71]} 0-1"""

# Note: Update stockfish_path to your Stockfish installation
results = analyze_game_performance(pgn_string, stockfish_path=r"C:\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe")

print("=" * 70)
print("GAME ANALYSIS RESULTS (Chess.com-style)")
print("=" * 70)
print()

print(f"White (jaideepbommidi) - Actual Rating: {results['white_elo']}")
print(f"  Game Score: {results['white_score']}")
print(f"  Average Centipawn Loss: {results['white_avg_centipawn_loss']}")
print(f"  Accuracy: {results['white_accuracy']}%")
print(f"  Performance Rating (Chess.com-style): {results['white_performance']}")
print(f"  Performance Rating (FIDE method): {results['white_performance_fide']}")
print()

print(f"Black (ferfl5) - Actual Rating: {results['black_elo']}")
print(f"  Game Score: {results['black_score']}")
print(f"  Average Centipawn Loss: {results['black_avg_centipawn_loss']}")
print(f"  Accuracy: {results['black_accuracy']}%")
print(f"  Performance Rating (Chess.com-style): {results['black_performance']}")
print(f"  Performance Rating (FIDE method): {results['black_performance_fide']}")
print()

print("=" * 70)
print("EXPLANATION:")
print("=" * 70)
print("Chess.com-style method:")
print("  - Based on accuracy compared to expected accuracy for your rating")
print("  - Formula: Expected Accuracy ≈ (Rating/100) + 64")
print("  - Each 4% accuracy difference ≈ 50 Elo")
print("  - Maximum deviation: ±800 from actual rating")
print()
print("FIDE method:")
print("  - Based purely on opponent rating and game result")
print("  - Win: Opponent rating + 400")
print("  - Loss: Opponent rating - 400")
print("  - Draw: Opponent rating")
print("=" * 70)
