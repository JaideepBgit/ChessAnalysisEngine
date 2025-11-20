# Building a Legal Chess Games Database

## Legal Sources for Chess Games

### 1. **Lichess.org** (BEST SOURCE - Fully Legal & Free)
- **License**: Public domain (CC0)
- **Data**: 3+ billion games
- **API**: Yes, well-documented
- **Download**: Monthly database dumps available
- **URL**: database.lichess.org

### 2. **The Week in Chess (TWIC)**
- **License**: Free for download
- **Data**: Professional tournament games since 1994
- **Format**: PGN files
- **Update**: Weekly
- **URL**: theweekinchess.com/twic

### 3. **FICS Games Database**
- **License**: Open
- **Data**: Free Internet Chess Server games
- **Format**: PGN
- **URL**: ficsgames.org

### 4. **PGN Mentor**
- **License**: Free collections
- **Data**: Historical games, opening databases
- **URL**: pgnmentor.com

### 5. **Chess.com Public API**
- **License**: Check terms of service
- **Data**: Public games via API
- **Rate Limits**: Yes
- **URL**: chess.com/news/view/published-data-api

---

## Web Scraping vs API vs Database Dumps

### Recommended Approach by Source:

| Source | Method | Reason |
|--------|--------|--------|
| Lichess | Database Dump | Fastest, legal, complete |
| TWIC | Direct Download | Weekly PGN files |
| Chess.com | API | Respects rate limits |
| Other sites | Check ToS first | May violate terms |

### Web Scraping Legal Guidelines:

**✅ Generally Legal:**
- Publicly accessible data
- Respecting robots.txt
- Reasonable rate limiting
- Not bypassing authentication
- Facts (game moves) not creative content

**❌ Potentially Illegal:**
- Ignoring robots.txt
- Bypassing paywalls
- Violating Terms of Service
- Causing server harm (DDoS)
- Scraping copyrighted annotations

---

## Database Design for Low-Cost, Embeddable Solution

### Recommended: **SQLite** (Perfect for Your Use Case)

**Why SQLite?**
- ✅ **Zero cost** - no server needed
- ✅ **Single file** - easy to distribute in installer
- ✅ **Fast** - can handle millions of games
- ✅ **No configuration** - works out of the box
- ✅ **Cross-platform** - Windows, Mac, Linux
- ✅ **Small footprint** - ~1MB library
- ✅ **ACID compliant** - reliable
- ✅ **SQL support** - powerful queries

**File Size Estimates:**
- 1 million games ≈ 500MB - 1GB (with indexes)
- 10 million games ≈ 5-10GB
- Compresses well with zip/7z

---

## Database Schema Design

### Option 1: Normalized Schema (Recommended for Queries)

```sql
-- Players table (avoid duplication)
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    fide_id INTEGER,
    country TEXT,
    peak_rating INTEGER
);
CREATE INDEX idx_player_name ON players(name);

-- Tournaments table
CREATE TABLE tournaments (
    tournament_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT,
    start_date DATE,
    end_date DATE,
    time_control TEXT,
    category TEXT,
    year INTEGER NOT NULL
);
CREATE INDEX idx_tournament_year ON tournaments(year);
CREATE INDEX idx_tournament_name ON tournaments(name);

-- Openings table (ECO codes)
CREATE TABLE openings (
    opening_id INTEGER PRIMARY KEY AUTOINCREMENT,
    eco_code TEXT UNIQUE,
    name TEXT NOT NULL,
    variation TEXT
);
CREATE INDEX idx_eco_code ON openings(eco_code);

-- Games table (main table)
CREATE TABLE games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER,
    white_player_id INTEGER NOT NULL,
    black_player_id INTEGER NOT NULL,
    opening_id INTEGER,
    result TEXT NOT NULL, -- '1-0', '0-1', '1/2-1/2'
    date DATE,
    round TEXT,
    white_elo INTEGER,
    black_elo INTEGER,
    time_control TEXT,
    termination TEXT, -- 'Normal', 'Time forfeit', etc.
    pgn_moves TEXT NOT NULL, -- Store full PGN moves
    fen_final TEXT, -- Final position
    move_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id),
    FOREIGN KEY (white_player_id) REFERENCES players(player_id),
    FOREIGN KEY (black_player_id) REFERENCES players(player_id),
    FOREIGN KEY (opening_id) REFERENCES openings(opening_id)
);

-- Indexes for fast queries
CREATE INDEX idx_game_date ON games(date);
CREATE INDEX idx_game_white ON games(white_player_id);
CREATE INDEX idx_game_black ON games(black_player_id);
CREATE INDEX idx_game_result ON games(result);
CREATE INDEX idx_game_opening ON games(opening_id);
CREATE INDEX idx_game_tournament ON games(tournament_id);
CREATE INDEX idx_game_year ON games(date); -- For year-based queries

-- Positions table (optional - for position search)
CREATE TABLE positions (
    position_id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    move_number INTEGER NOT NULL,
    fen TEXT NOT NULL,
    evaluation REAL, -- Engine evaluation
    
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);
CREATE INDEX idx_position_fen ON positions(fen);
```

### Option 2: Denormalized Schema (Faster Inserts, Larger Size)

```sql
-- Single table with all data
CREATE TABLE games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Tournament info
    tournament_name TEXT,
    tournament_location TEXT,
    tournament_date DATE,
    year INTEGER NOT NULL,
    round TEXT,
    
    -- Players
    white_player TEXT NOT NULL,
    black_player TEXT NOT NULL,
    white_elo INTEGER,
    black_elo INTEGER,
    white_fide_id INTEGER,
    black_fide_id INTEGER,
    
    -- Game details
    result TEXT NOT NULL,
    eco_code TEXT,
    opening_name TEXT,
    time_control TEXT,
    termination TEXT,
    move_count INTEGER,
    
    -- Game data
    pgn_moves TEXT NOT NULL,
    pgn_full TEXT, -- Complete PGN with headers
    fen_final TEXT,
    
    -- Metadata
    source TEXT, -- 'lichess', 'twic', etc.
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Essential indexes
CREATE INDEX idx_year ON games(year);
CREATE INDEX idx_white ON games(white_player);
CREATE INDEX idx_black ON games(black_player);
CREATE INDEX idx_tournament ON games(tournament_name);
CREATE INDEX idx_eco ON games(eco_code);
CREATE INDEX idx_result ON games(result);
CREATE INDEX idx_date ON games(tournament_date);

-- Full-text search (optional but powerful)
CREATE VIRTUAL TABLE games_fts USING fts5(
    white_player,
    black_player,
    tournament_name,
    opening_name,
    content=games
);
```

**Recommendation**: Use **Option 2 (Denormalized)** for your use case because:
- Simpler to implement
- Faster imports
- Easier to distribute
- Good enough for millions of games
- Can always normalize later if needed

---

## Web Scraper Architecture

### Technology Stack

```python
# Core libraries
import requests          # HTTP requests
import chess.pgn         # PGN parsing
import sqlite3           # Database
from bs4 import BeautifulSoup  # HTML parsing
import time              # Rate limiting
import logging           # Error tracking

# Optional but recommended
import aiohttp           # Async requests (faster)
import asyncio           # Async operations
from tqdm import tqdm    # Progress bars
import pandas as pd      # Data processing
```

### Scraper Components

```
┌─────────────────────────────────────────────┐
│           Data Collection Layer              │
├─────────────────────────────────────────────┤
│  • Lichess Downloader                       │
│  • TWIC Downloader                          │
│  • Chess.com API Client                     │
│  • Generic Web Scraper (with robots.txt)    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           Processing Layer                   │
├─────────────────────────────────────────────┤
│  • PGN Parser                               │
│  • Data Validator                           │
│  • Deduplicator                             │
│  • ECO Code Classifier                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           Storage Layer                      │
├─────────────────────────────────────────────┤
│  • SQLite Database                          │
│  • Batch Inserter (for speed)              │
│  • Index Manager                            │
└─────────────────────────────────────────────┘
```

---

## Implementation Guide

### Step 1: Lichess Database Download (Easiest Start)

```python
import requests
import bz2
import chess.pgn
import sqlite3
from io import StringIO

def download_lichess_monthly(year, month):
    """
    Download Lichess monthly database
    URL format: https://database.lichess.org/standard/lichess_db_standard_rated_YYYY-MM.pgn.bz2
    """
    url = f"https://database.lichess.org/standard/lichess_db_standard_rated_{year}-{month:02d}.pgn.bz2"
    
    print(f"Downloading {url}...")
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        # Decompress on the fly
        decompressor = bz2.BZ2Decompressor()
        pgn_data = b""
        
        for chunk in response.iter_content(chunk_size=8192):
            pgn_data += decompressor.decompress(chunk)
        
        return pgn_data.decode('utf-8')
    else:
        print(f"Failed to download: {response.status_code}")
        return None
```

### Step 2: TWIC Scraper

```python
import requests
from bs4 import BeautifulSoup
import re

def scrape_twic_archives():
    """
    Scrape The Week in Chess archives
    """
    base_url = "https://theweekinchess.com/twic"
    
    # Get archive page
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all PGN download links
    pgn_links = []
    for link in soup.find_all('a', href=True):
        if link['href'].endswith('.pgn') or link['href'].endswith('.zip'):
            pgn_links.append(link['href'])
    
    return pgn_links

def download_twic_pgn(url):
    """
    Download a TWIC PGN file
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None
```

### Step 3: PGN Parser & Database Inserter

```python
import chess.pgn
import sqlite3
from datetime import datetime

class ChessGameDatabase:
    def __init__(self, db_path='chess_games.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create database schema"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_name TEXT,
                tournament_location TEXT,
                tournament_date DATE,
                year INTEGER NOT NULL,
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
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_year ON games(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_white ON games(white_player)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_black ON games(black_player)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tournament ON games(tournament_name)')
        
        self.conn.commit()
    
    def parse_and_insert_pgn(self, pgn_text, source='unknown'):
        """Parse PGN and insert into database"""
        pgn_io = StringIO(pgn_text)
        games_inserted = 0
        
        while True:
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
            moves = str(game.mainline_moves())
            move_count = len(list(game.mainline_moves()))
            
            # Insert into database
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO games (
                    tournament_name, tournament_location, tournament_date,
                    year, round, white_player, black_player,
                    white_elo, black_elo, result, eco_code, opening_name,
                    time_control, termination, move_count, pgn_moves,
                    pgn_full, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                headers.get('Event'),
                headers.get('Site'),
                headers.get('Date'),
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
            ))
            
            games_inserted += 1
            
            if games_inserted % 1000 == 0:
                self.conn.commit()
                print(f"Inserted {games_inserted} games...")
        
        self.conn.commit()
        return games_inserted
    
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
        ''', (f'%{player_name}%', f'%{player_name}%'))
        return cursor.fetchall()
    
    def get_statistics(self):
        """Get database statistics"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM games')
        total_games = cursor.fetchone()[0]
        
        cursor.execute('SELECT MIN(year), MAX(year) FROM games WHERE year IS NOT NULL')
        year_range = cursor.fetchone()
        
        return {
            'total_games': total_games,
            'year_range': year_range
        }
    
    def close(self):
        self.conn.close()
```

### Step 4: Main Scraper Script

```python
def main():
    # Initialize database
    db = ChessGameDatabase('chess_games.db')
    
    # Download TWIC archives
    print("Downloading TWIC archives...")
    twic_links = scrape_twic_archives()
    
    for link in twic_links[:5]:  # Start with first 5
        print(f"Processing {link}...")
        pgn_data = download_twic_pgn(link)
        if pgn_data:
            count = db.parse_and_insert_pgn(pgn_data, source='twic')
            print(f"Inserted {count} games from {link}")
        time.sleep(2)  # Be polite, rate limit
    
    # Get statistics
    stats = db.get_statistics()
    print(f"\nDatabase Statistics:")
    print(f"Total games: {stats['total_games']}")
    print(f"Year range: {stats['year_range']}")
    
    db.close()

if __name__ == '__main__':
    main()
```

---

## Query Examples for Your Database

```python
# Get all games from 2025
games_2025 = db.query_by_year(2025)

# Get all games by Magnus Carlsen
magnus_games = db.query_by_player('Carlsen')

# Get tournament games
cursor.execute('''
    SELECT * FROM games 
    WHERE tournament_name LIKE '%World Championship%'
    AND year = 2024
''')

# Get opening statistics
cursor.execute('''
    SELECT eco_code, opening_name, COUNT(*) as count
    FROM games
    WHERE year = 2025
    GROUP BY eco_code
    ORDER BY count DESC
    LIMIT 10
''')
```

---

## Distribution Strategy

### For Installation File:

1. **Compress the database**:
   ```bash
   7z a -mx=9 chess_games.7z chess_games.db
   ```
   - Compression ratio: ~50-70%

2. **Include in installer**:
   - Use NSIS, Inno Setup, or PyInstaller
   - Extract database on first run
   - Store in user's AppData folder

3. **Update mechanism**:
   - Download delta updates (new games only)
   - Merge into existing database

---

## Legal Compliance Checklist

✅ **Before Scraping:**
- [ ] Check robots.txt
- [ ] Read Terms of Service
- [ ] Verify data license
- [ ] Implement rate limiting
- [ ] Add User-Agent header
- [ ] Respect no-index directives

✅ **For Distribution:**
- [ ] Document data sources
- [ ] Include attribution
- [ ] Provide license file
- [ ] Don't claim copyright on facts
- [ ] Add value (don't just redistribute)

---

## Performance Optimization

### Batch Inserts (10x faster):

```python
def batch_insert_games(self, games_data):
    """Insert multiple games at once"""
    cursor = self.conn.cursor()
    cursor.executemany('''
        INSERT INTO games (...) VALUES (?, ?, ...)
    ''', games_data)
    self.conn.commit()
```

### Indexing Strategy:

```sql
-- Create indexes AFTER bulk insert
CREATE INDEX idx_year ON games(year);
CREATE INDEX idx_white ON games(white_player);
CREATE INDEX idx_black ON games(black_player);

-- Analyze for query optimization
ANALYZE;
```

### Database Optimization:

```sql
-- Vacuum to reclaim space
VACUUM;

-- Enable WAL mode for better concurrency
PRAGMA journal_mode=WAL;

-- Increase cache size
PRAGMA cache_size=10000;
```

---

## Cost Analysis

### Storage Costs (SQLite):
- **1 million games**: ~500MB - 1GB
- **10 million games**: ~5-10GB
- **Compressed**: 50-70% smaller

### Hosting Costs (if offering downloads):
- **AWS S3**: ~$0.023/GB/month
- **Cloudflare R2**: Free egress
- **GitHub Releases**: Free (up to 2GB per file)

### Recommended: Distribute via torrent or direct download

---

## Next Steps

1. Start with TWIC (easiest, legal, quality data)
2. Build SQLite database with denormalized schema
3. Add Lichess data for volume
4. Create query interface
5. Add value-added features (analysis, statistics)
6. Package for distribution

This approach gives you a legal, distributable, low-cost database perfect for coaches and candidates!
