"""
Chess Game Database Scraper
Downloads chess games from legal sources and stores them in SQLite database
"""

from .database import ChessGameDatabase
from .scrapers import (
    LichessScraper,
    TWICScraper,
    ChesscomScraper,
    GenericPGNDownloader
)

__version__ = '1.0.0'
__all__ = [
    'ChessGameDatabase',
    'LichessScraper',
    'TWICScraper',
    'ChesscomScraper',
    'GenericPGNDownloader'
]
