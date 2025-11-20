import sqlite3
import chess.pgn
from io import StringIO
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChessGameDatabase:
    """SQLite database for storing chess games"""
    
    def __init__(self, db_path='chess_games.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
        self.optimize_database()
    
    def create_tables(self):
        """Create database schema"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_name TEXT,
                tournament_location TEXT,
                tournament_date TEXT,
                year INTEGER,
                round TEXT,
                white_player TEXT NOT NULL,
                black_player TEXT NOT NULL,
                white_elo INTEGER,
                black_elo INTEGER,
                result TEXT NOT NULL,
                eco_code TEXT,
                opening_name TEXT,
                time_control TEXT,
                termination TEXT,
                move_count INTEGER,
                pgn_moves TEXT NOT NULL,
                pgn_full TEXT,
                source TEXT,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for fast queries
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_year ON games(year)',
            'CREATE INDEX IF NOT EXISTS idx_white ON games(white_player)',
            'CREATE INDEX IF NOT EXISTS idx_black ON games(black_player)',
            'CREATE INDEX IF NOT EXISTS idx_tournament ON games(tournament_name)',
            'CREATE INDEX IF NOT EXISTS idx_eco ON games(eco_code)',
            'CREATE INDEX IF NOT EXISTS idx_result ON games(result)',
            'CREATE INDEX IF NOT EXISTS idx_date ON games(tournament_date)',
            'CREATE INDEX IF NOT EXISTS idx_source ON games(source)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        self.conn.commit()
        logger.info("Database tables and indexes created")
    
    def optimize_database(self):
        """Optimize database settings"""
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA synchronous=NORMAL')
        cursor.execute('PRAGMA cache_size=10000')
        cursor.execute('PRAGMA temp_store=MEMORY')
        self.conn.commit()
    
    def parse_and_insert_pgn(self, pgn_text, source='unknown', batch_size=1000):
        """Parse PGN text and insert games into database"""
        pgn_io = StringIO(pgn_text)
        games_inserted = 0
        batch_data = []
        
        while True:
            try:
                game = chess.pgn.read_game(pgn_io)
                if game is None:
                    break
                
                headers = game.headers
                
                # Extract data
                white = headers.get('White', 'Unknown')
                black = headers.get('Black', 'Unknown')
                result = headers.get('Result', '*')
                date_str = headers.get('Date', '????.??.??')
                
                # Parse year
                year = None
                if date_str and date_str != '????.??.??':
                    try:
                        year = int(date_str.split('.')[0])
                    except:
                        pass
                
                # Get moves
                moves = ' '.join([str(move) for move in game.mainline_moves()])
                move_count = len(list(game.mainline_moves()))
                
                # Prepare data tuple
                game_data = (
                    headers.get('Event'),
                    headers.get('Site'),
                    date_str,
                    year,
                    headers.get('Round'),
                    white,
                    black,
                    self._parse_elo(headers.get('WhiteElo')),
                    self._parse_elo(headers.get('BlackElo')),
                    result,
                    headers.get('ECO'),
                    headers.get('Opening'),
                    headers.get('TimeControl'),
                    headers.get('Termination'),
                    move_count,
                    moves,
                    str(game),
                    source
                )
                
                batch_data.append(game_data)
                
                # Batch insert for performance
                if len(batch_data) >= batch_size:
                    self._batch_insert(batch_data)
                    games_inserted += len(batch_data)
                    logger.info(f"Inserted {games_inserted} games...")
                    batch_data = []
            
            except Exception as e:
                logger.error(f"Error parsing game: {e}")
                continue
        
        # Insert remaining games
        if batch_data:
            self._batch_insert(batch_data)
            games_inserted += len(batch_data)
        
        self.conn.commit()
        logger.info(f"Total games inserted: {games_inserted}")
        return games_inserted
    
    def _batch_insert(self, batch_data):
        """Insert multiple games at once"""
        cursor = self.conn.cursor()
        cursor.executemany('''
            INSERT INTO games (
                tournament_name, tournament_location, tournament_date,
                year, round, white_player, black_player,
                white_elo, black_elo, result, eco_code, opening_name,
                time_control, termination, move_count, pgn_moves,
                pgn_full, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', batch_data)
    
    def _parse_elo(self, elo_str):
        """Parse ELO rating"""
        if elo_str and elo_str != '?':
            try:
                return int(elo_str)
            except:
                pass
        return None
    
    def query_by_year(self, year):
        """Query games by year"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM games WHERE year = ?', (year,))
        return cursor.fetchall()
    
    def query_by_player(self, player_name):
        """Query games by player"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM games 
            WHERE white_player LIKE ? OR black_player LIKE ?
            ORDER BY tournament_date DESC
        ''', (f'%{player_name}%', f'%{player_name}%'))
        return cursor.fetchall()
    
    def query_by_tournament(self, tournament_name, year=None):
        """Query games by tournament"""
        cursor = self.conn.cursor()
        if year:
            cursor.execute('''
                SELECT * FROM games 
                WHERE tournament_name LIKE ? AND year = ?
            ''', (f'%{tournament_name}%', year))
        else:
            cursor.execute('''
                SELECT * FROM games 
                WHERE tournament_name LIKE ?
            ''', (f'%{tournament_name}%',))
        return cursor.fetchall()
    
    def get_statistics(self):
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM games')
        total_games = cursor.fetchone()[0]
        
        cursor.execute('SELECT MIN(year), MAX(year) FROM games WHERE year IS NOT NULL')
        year_range = cursor.fetchone()
        
        cursor.execute('SELECT COUNT(DISTINCT white_player) + COUNT(DISTINCT black_player) FROM games')
        total_players = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT tournament_name) FROM games WHERE tournament_name IS NOT NULL')
        total_tournaments = cursor.fetchone()[0]
        
        cursor.execute('SELECT source, COUNT(*) FROM games GROUP BY source')
        games_by_source = cursor.fetchall()
        
        return {
            'total_games': total_games,
            'year_range': year_range,
            'total_players': total_players,
            'total_tournaments': total_tournaments,
            'games_by_source': games_by_source
        }
    
    def vacuum(self):
        """Optimize database file size"""
        logger.info("Running VACUUM...")
        self.conn.execute('VACUUM')
        logger.info("VACUUM complete")
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        logger.info("Database connection closed")
