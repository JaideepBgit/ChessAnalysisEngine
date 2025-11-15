import chess
import chess.pgn
import io
import time
import os
import sys


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def animate_chess_game(pgn_string, delay=2.0):
    """
    Animate a chess game in the terminal using ASCII/Unicode.
    
    Args:
        pgn_string: PGN string of the game
        delay: Seconds to display each position
    """
    # Parse the PGN
    pgn = io.StringIO(pgn_string)
    game = chess.pgn.read_game(pgn)
    
    white_name = game.headers.get("White", "White")
    black_name = game.headers.get("Black", "Black")
    
    board = game.board()
    move_number = 1
    
    print(f"\n{'='*60}")
    print(f"  {white_name} vs {black_name}")
    print(f"{'='*60}\n")
    print("Press Ctrl+C to stop animation\n")
    time.sleep(2)
    
    # Show initial position
    clear_screen()
    print(f"\n  Initial Position\n")
    print(board.unicode(borders=True, empty_square='·'))
    print(f"\n{'─'*60}")
    time.sleep(delay)
    
    try:
        # Animate each move
        for move in game.mainline_moves():
            move_san = board.san(move)
            board.push(move)
            
            clear_screen()
            
            # Display move number and move
            if board.turn == chess.WHITE:  # Black just moved
                print(f"\n  Move {move_number}... {move_san} (Black)")
            else:  # White just moved
                print(f"\n  Move {move_number}. {move_san} (White)")
                move_number += 1
            
            # Display board
            print()
            print(board.unicode(borders=True, empty_square='·'))
            
            # Display game info
            print(f"\n{'─'*60}")
            print(f"  Material: White {count_material(board, chess.WHITE)} | "
                  f"Black {count_material(board, chess.BLACK)}")
            print(f"{'─'*60}")
            
            time.sleep(delay)
        
        # Show final result
        result = game.headers.get("Result", "*")
        print(f"\n  Game Result: {result}")
        
        if result == "1-0":
            print(f"  🏆 {white_name} wins!")
        elif result == "0-1":
            print(f"  🏆 {black_name} wins!")
        else:
            print(f"  🤝 Draw")
            
    except KeyboardInterrupt:
        print("\n\nAnimation stopped by user.")


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


if __name__ == "__main__":
    pgn_string = """[Event "Live Chess"]
[Site "Chess.com"]
[Date "2025.11.10"]
[Round "?"]
[White "jaideepbommidi"]
[Black "13ruce"]
[Result "1-0"]

1. d4 b6 2. e3 c5 3. d5 Nf6 4. Nc3 Bb7 5. e4 e6 6. e5 Nxd5 7. Nxd5 exd5 
8. Nf3 Nc6 9. Bg5 Ne7 10. Bb5 Bc6 11. Bxc6 dxc6 12. O-O f6 13. exf6 gxf6 
14. Bxf6 Qd6 15. Bxh8 Ng6 16. Bc3 d4 17. Bd2 Nf4 18. Bxf4 Qxf4 19. Re1+ Be7 
20. g3 Qd6 21. Ne5 O-O-O 22. Nf7 Qf6 23. Nxd8 Kxd8 24. Qe2 Ke8 25. c3 dxc3 
26. bxc3 c4 27. Rab1 b5 28. Red1 Qxc3 29. a3 Qxa3 30. Qh5+ Kf8 31. f4 Qe3+ 
32. Kg2 Bc5 33. Kh3 Qe6+ 34. Qg4 Qh6+ 35. Kg2 Qe6 36. Qxe6 1-0"""
    
    animate_chess_game(pgn_string, delay=1.5)
