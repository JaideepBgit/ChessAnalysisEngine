#!/usr/bin/env python3
"""
Chess Game Database Scraper
Downloads chess games from legal sources and stores them in SQLite database
"""

import argparse
import logging
from database import ChessGameDatabase
from scrapers import LichessScraper, TWICScraper, ChesscomScraper, GenericPGNDownloader
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_lichess_year(db, year, rated=True):
    """Download all Lichess games from a specific year"""
    logger.info(f"Downloading Lichess games for {year}")
    
    for month in range(1, 13):
        logger.info(f"Processing {year}-{month:02d}")
        
        pgn_data = LichessScraper.download_monthly_games(year, month, rated)
        
        if pgn_data:
            count = db.parse_and_insert_pgn(pgn_data, source=f'lichess_{year}')
            logger.info(f"Inserted {count} games from {year}-{month:02d}")
        
        # Be polite - rate limit
        time.sleep(5)


def download_twic_latest(db, count=10):
    """Download latest TWIC issues"""
    logger.info(f"Downloading latest {count} TWIC issues")
    
    issues = TWICScraper.get_available_issues()
    
    for i, url in enumerate(issues[:count]):
        logger.info(f"Processing issue {i+1}/{count}: {url}")
        
        pgn_data = TWICScraper.download_issue(url)
        
        if pgn_data:
            game_count = db.parse_and_insert_pgn(pgn_data, source='twic')
            logger.info(f"Inserted {game_count} games from {url}")
        
        time.sleep(2)


def download_player_games(db, username, year):
    """Download games for a specific Chess.com player"""
    logger.info(f"Downloading games for {username} in {year}")
    
    for month in range(1, 13):
        pgn_data = ChesscomScraper.get_player_games(username, year, month)
        
        if pgn_data:
            count = db.parse_and_insert_pgn(pgn_data, source=f'chesscom_{username}')
            logger.info(f"Inserted {count} games from {year}-{month:02d}")
        
        time.sleep(1)


def download_from_url(db, url, source_name='custom'):
    """Download PGN from any URL"""
    logger.info(f"Downloading from {url}")
    
    pgn_data = GenericPGNDownloader.download(url)
    
    if pgn_data:
        count = db.parse_and_insert_pgn(pgn_data, source=source_name)
        logger.info(f"Inserted {count} games from {url}")


def show_statistics(db):
    """Display database statistics"""
    stats = db.get_statistics()
    
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    print(f"Total Games: {stats['total_games']:,}")
    print(f"Year Range: {stats['year_range'][0]} - {stats['year_range'][1]}")
    print(f"Total Players: {stats['total_players']:,}")
    print(f"Total Tournaments: {stats['total_tournaments']:,}")
    print("\nGames by Source:")
    for source, count in stats['games_by_source']:
        print(f"  {source}: {count:,}")
    print("="*60 + "\n")


def query_year(db, year):
    """Query and display games from a specific year"""
    logger.info(f"Querying games from {year}")
    games = db.query_by_year(year)
    
    print(f"\nFound {len(games)} games from {year}")
    
    if games:
        print("\nSample games:")
        for game in games[:5]:
            print(f"  {game[6]} vs {game[7]} - {game[10]} ({game[3]})")


def query_player(db, player_name):
    """Query and display games for a specific player"""
    logger.info(f"Querying games for {player_name}")
    games = db.query_by_player(player_name)
    
    print(f"\nFound {len(games)} games for {player_name}")
    
    if games:
        print("\nSample games:")
        for game in games[:10]:
            print(f"  {game[6]} vs {game[7]} - {game[10]} ({game[3]})")


def main():
    parser = argparse.ArgumentParser(
        description='Chess Game Database Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download Lichess games from 2025
  python main.py --lichess-year 2025
  
  # Download latest 20 TWIC issues
  python main.py --twic 20
  
  # Download Chess.com player games
  python main.py --chesscom-player hikaru --year 2024
  
  # Download from custom URL
  python main.py --url https://example.com/games.pgn --source "My Source"
  
  # Query games from 2025
  python main.py --query-year 2025
  
  # Query games by player
  python main.py --query-player "Carlsen"
  
  # Show database statistics
  python main.py --stats
        """
    )
    
    parser.add_argument('--db', default='chess_games.db', help='Database file path')
    
    # Download options
    parser.add_argument('--lichess-year', type=int, help='Download Lichess games from specific year')
    parser.add_argument('--lichess-rated', action='store_true', default=True, help='Download rated games (default)')
    parser.add_argument('--twic', type=int, help='Download N latest TWIC issues')
    parser.add_argument('--chesscom-player', help='Chess.com username')
    parser.add_argument('--year', type=int, help='Year for Chess.com player games')
    parser.add_argument('--url', help='Download PGN from URL')
    parser.add_argument('--source', default='custom', help='Source name for URL download')
    
    # Query options
    parser.add_argument('--query-year', type=int, help='Query games from specific year')
    parser.add_argument('--query-player', help='Query games by player name')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    
    # Maintenance
    parser.add_argument('--vacuum', action='store_true', help='Optimize database')
    
    args = parser.parse_args()
    
    # Initialize database
    db = ChessGameDatabase(args.db)
    logger.info(f"Using database: {args.db}")
    
    try:
        # Download operations
        if args.lichess_year:
            download_lichess_year(db, args.lichess_year, args.lichess_rated)
        
        if args.twic:
            download_twic_latest(db, args.twic)
        
        if args.chesscom_player and args.year:
            download_player_games(db, args.chesscom_player, args.year)
        
        if args.url:
            download_from_url(db, args.url, args.source)
        
        # Query operations
        if args.query_year:
            query_year(db, args.query_year)
        
        if args.query_player:
            query_player(db, args.query_player)
        
        if args.stats:
            show_statistics(db)
        
        # Maintenance
        if args.vacuum:
            db.vacuum()
        
        # If no arguments, show help
        if len(vars(args)) == 1:  # Only db argument
            parser.print_help()
    
    finally:
        db.close()


if __name__ == '__main__':
    main()
