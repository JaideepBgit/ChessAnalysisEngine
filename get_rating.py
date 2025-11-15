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
[Date "2025.11.11"]
[Round "?"]
[White "muhammed1125"]
[Black "jaideepbommidi"]
[Result "0-1"]
[TimeControl "300"]
[WhiteElo "291"]
[BlackElo "310"]
[Termination "jaideepbommidi won by checkmate"]
[Link "https://www.chess.com/game/145399159056"]

1. e4 {[%clk 0:04:59.4][%timestamp 6]} 1... e5 {[%clk 0:04:58.6][%timestamp 14]}
2. Qh5 {[%clk 0:04:57.6][%timestamp 18]} 2... Nc6 {[%clk 0:04:54.4][%timestamp
42]} 3. Bc4 {[%clk 0:04:56.5][%timestamp 11]} 3... Qe7 {[%clk
0:04:52.6][%timestamp 18]} 4. d3 {[%clk 0:04:53.8][%timestamp 27]} 4... Nf6
{[%clk 0:04:50.8][%timestamp 18]} 5. Qf3 {[%clk 0:04:47.9][%timestamp 59]} 5...
d6 {[%clk 0:04:46.3][%timestamp 45]} 6. Nc3 {[%clk 0:04:44.6][%timestamp 33]}
6... g6 {[%clk 0:04:43.3][%timestamp 30]} 7. Nd1 {[%clk 0:04:42.4][%timestamp
22]} 7... Nd4 {[%clk 0:04:38.7][%timestamp 46]} 8. Qg3 {[%clk
0:04:20.8][%timestamp 216]} 8... Nxc2+ {[%clk 0:04:33.6][%timestamp 51]} 9. Kf1
{[%clk 0:04:16.9][%timestamp 39]} 9... Nxa1 {[%clk 0:04:32.4][%timestamp 12]}
10. Nc3 {[%clk 0:04:15.4][%timestamp 15]} 10... Nc2 {[%clk 0:04:26.8][%timestamp
56]} 11. Nd5 {[%clk 0:04:13.7][%timestamp 17]} 11... Nxd5 {[%clk
0:04:19.3][%timestamp 75]} 12. Bxd5 {[%clk 0:04:10.9][%timestamp 28]} 12... Be6
{[%clk 0:04:15.2][%timestamp 41]} 13. Bg5 {[%clk 0:04:05.3][%timestamp 56]}
13... Qd7 {[%clk 0:04:09][%timestamp 62]} 14. Bxe6 {[%clk 0:04:00.2][%timestamp
51]} 14... Qxe6 {[%clk 0:04:05][%timestamp 40]} 15. Nf3 {[%clk
0:03:59.5][%timestamp 7]} 15... Nd4 {[%clk 0:03:59.6][%timestamp 54]} 16. Nxd4
{[%clk 0:03:56.9][%timestamp 26]} 16... exd4 {[%clk 0:03:58.4][%timestamp 12]}
17. f4 {[%clk 0:03:49.2][%timestamp 77]} 17... Bg7 {[%clk 0:03:55.2][%timestamp
32]} 18. f5 {[%clk 0:03:48.3][%timestamp 9]} 18... Qd7 {[%clk
0:03:50][%timestamp 52]} 19. f6 {[%clk 0:03:46][%timestamp 23]} 19... Bf8 {[%clk
0:03:42.8][%timestamp 72]} 20. e5 {[%clk 0:03:38.9][%timestamp 71]} 20... dxe5
{[%clk 0:03:36.4][%timestamp 64]} 21. Qxe5+ {[%clk 0:03:38.7][%timestamp 2]}
21... Be7 {[%clk 0:03:33.1][%timestamp 33]} 22. fxe7 {[%clk
0:03:37.1][%timestamp 16]} 22... f6 {[%clk 0:03:20.8][%timestamp 123]} 23. Qxf6
{[%clk 0:03:34.8][%timestamp 23]} 23... Rg8 {[%clk 0:03:12.8][%timestamp 80]}
24. Qxg6+ {[%clk 0:03:31][%timestamp 38]} 24... Rxg6 {[%clk
0:03:11.3][%timestamp 15]} 25. h4 {[%clk 0:03:24.7][%timestamp 63]} 25... h6
{[%clk 0:03:05.7][%timestamp 56]} 26. g3 {[%clk 0:03:24.1][%timestamp 6]} 26...
hxg5 {[%clk 0:03:03.7][%timestamp 20]} 27. hxg5 {[%clk 0:03:23.1][%timestamp
10]} 27... Qxe7 {[%clk 0:02:58.4][%timestamp 53]} 28. Rh8+ {[%clk
0:03:22.3][%timestamp 8]} 28... Qf8+ {[%clk 0:02:54.5][%timestamp 39]} 29. Rxf8+
{[%clk 0:03:20.9][%timestamp 14]} 29... Kxf8 {[%clk 0:02:53.7][%timestamp 8]}
30. b4 {[%clk 0:03:17.4][%timestamp 35]} 30... Re8 {[%clk 0:02:51][%timestamp
27]} 31. a3 {[%clk 0:03:16.8][%timestamp 6]} 31... Rxg5 {[%clk
0:02:49.1][%timestamp 19]} 32. Kf2 {[%clk 0:03:16.1][%timestamp 7]} 32... b5
{[%clk 0:02:43.4][%timestamp 57]} 33. Kf3 {[%clk 0:03:15.3][%timestamp 8]} 33...
Rf5+ {[%clk 0:02:40.7][%timestamp 27]} 34. Kg4 {[%clk 0:03:13.9][%timestamp 14]}
34... Rf1 {[%clk 0:02:36.5][%timestamp 42]} 35. Kh4 {[%clk 0:03:12.6][%timestamp
13]} 35... Ra1 {[%clk 0:02:34.9][%timestamp 16]} 36. g4 {[%clk
0:03:12][%timestamp 6]} 36... Rxa3 {[%clk 0:02:31.6][%timestamp 33]} 37. Kh5
{[%clk 0:03:10.4][%timestamp 16]} 37... Rxd3 {[%clk 0:02:30.4][%timestamp 12]}
38. g5 {[%clk 0:03:09.9][%timestamp 5]} 38... Rg3 {[%clk 0:02:27.2][%timestamp
32]} 39. Kh6 {[%clk 0:03:09][%timestamp 9]} 39... Kg8 {[%clk
0:02:23.6][%timestamp 36]} 40. g6 {[%clk 0:03:08.2][%timestamp 8]} 40... Re7
{[%clk 0:02:20.1][%timestamp 35]} 41. g7 {[%clk 0:03:06][%timestamp 22]} 41...
Rexg7 {[%clk 0:02:18.5][%timestamp 16]} 42. Kh5 {[%clk 0:03:03.5][%timestamp
25]} 42... R3g5+ {[%clk 0:02:16.4][%timestamp 21]} 43. Kh4 {[%clk
0:03:01.3][%timestamp 22]} 43... Rh7+ {[%clk 0:02:10.7][%timestamp 57]} 44. Kxg5
{[%clk 0:03:00.2][%timestamp 11]} 44... Rh1 {[%clk 0:02:07][%timestamp 37]} 45.
Kf5 {[%clk 0:02:58.5][%timestamp 17]} 45... d3 {[%clk 0:02:06.1][%timestamp 9]}
46. Ke4 {[%clk 0:02:57.7][%timestamp 8]} 46... d2 {[%clk 0:02:05.1][%timestamp
10]} 47. Kd5 {[%clk 0:02:55.6][%timestamp 21]} 47... d1=Q+ {[%clk
0:02:03.7][%timestamp 14]} 48. Kc6 {[%clk 0:02:54.9][%timestamp 7]} 48... Qc1+
{[%clk 0:02:02.1][%timestamp 16]} 49. Kxb5 {[%clk 0:02:54][%timestamp 9]} 49...
Rh5+ {[%clk 0:01:59.5][%timestamp 26]} 50. Ka4 {[%clk 0:02:50.2][%timestamp 38]}
50... c5 {[%clk 0:01:48.6][%timestamp 109]} 51. b5 {[%clk 0:02:44.9][%timestamp
53]} 51... c4 {[%clk 0:01:44.1][%timestamp 45]} 52. Ka5 {[%clk
0:02:44][%timestamp 9]} 52... Qa1+ {[%clk 0:01:39.8][%timestamp 43]} 53. Kb4
{[%clk 0:02:41.2][%timestamp 28]} 53... a5+ {[%clk 0:01:28.7][%timestamp 111]}
54. Kxc4 {[%clk 0:02:37.7][%timestamp 35]} 54... a4 {[%clk 0:01:27.8][%timestamp
9]} 55. Kb4 {[%clk 0:02:35.6][%timestamp 21]} 55... Rh4+ {[%clk
0:01:22.7][%timestamp 51]} 56. Ka5 {[%clk 0:02:33.3][%timestamp 23]} 56... a3
{[%clk 0:01:21.2][%timestamp 15]} 57. b6 {[%clk 0:02:32][%timestamp 13]} 57...
a2 {[%clk 0:01:17.9][%timestamp 33]} 58. b7 {[%clk 0:02:31.5][%timestamp 5]}
58... Qb1 {[%clk 0:01:16.7][%timestamp 12]} 59. Ka6 {[%clk 0:02:29.4][%timestamp
21]} 59... Rh7 {[%clk 0:01:12][%timestamp 47]} 60. Ka7 {[%clk
0:02:27.9][%timestamp 15]} 60... a1=Q+ {[%clk 0:01:09.7][%timestamp 23]} 61. Kb8
{[%clk 0:02:26.1][%timestamp 18]} 61... Rxb7+ {[%clk 0:01:06.5][%timestamp 32]}
62. Kc8 {[%clk 0:02:23.6][%timestamp 25]} 62... Qa8# {[%clk
0:00:59.7][%timestamp 68]} 0-1"""

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
