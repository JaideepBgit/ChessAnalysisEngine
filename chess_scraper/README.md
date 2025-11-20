# Chess Game Database Scraper

A Python tool to download chess games from legal sources and store them in a SQLite database.

## Features

- ✅ Download from **Lichess** (3+ billion games, fully legal)
- ✅ Download from **The Week in Chess (TWIC)** (professional tournaments)
- ✅ Download from **Chess.com** public API
- ✅ Download from any PGN URL
- ✅ SQLite database (single file, embeddable)
- ✅ Fast batch inserts
- ✅ Query by year, player, tournament
- ✅ Automatic deduplication
- ✅ Progress bars

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Download Lichess Games from 2025

```bash
python main.py --lichess-year 2025
```

This will download all rated games from Lichess for the year 2025 (warning: this is a LOT of data, several GB).

### 2. Download Latest TWIC Issues (Recommended Start)

```bash
python main.py --twic 10
```

Downloads the latest 10 issues from The Week in Chess. This gives you high-quality tournament games.

### 3. Download Specific Player Games

```bash
python main.py --chesscom-player hikaru --year 2024
```

### 4. Download from Custom URL

```bash
python main.py --url https://example.com/games.pgn --source "My Tournament"
```

## Query Database

### Get all games from 2025

```bash
python main.py --query-year 2025
```

### Search for player games

```bash
python main.py --query-player "Carlsen"
```

### Show database statistics

```bash
python main.py --stats
```

## Database Schema

The database uses a denormalized schema for simplicity and speed:

```sql
games (
    game_id, tournament_name, tournament_location, tournament_date,
    year, round, white_player, black_player, white_elo, black_elo,
    result, eco_code, opening_name, time_control, termination,
    move_count, pgn_moves, pgn_full, source, imported_at
)
```

Indexes on: year, white_player, black_player, tournament_name, eco_code, result

## Usage Examples

### Build a database for 2024-2025 tournaments

```bash
# Download TWIC (professional tournaments)
python main.py --twic 50

# Download Lichess titled players games
python main.py --lichess-year 2024
python main.py --lichess-year 2025

# Show statistics
python main.py --stats
```

### Query specific data

```python
from database import ChessGameDatabase

db = ChessGameDatabase('chess_games.db')

# Get all games from 2025
games_2025 = db.query_by_year(2025)

# Get Magnus Carlsen games
magnus_games = db.query_by_player('Carlsen')

# Get World Championship games
wc_games = db.query_by_tournament('World Championship', 2024)

# Get statistics
stats = db.get_statistics()
print(f"Total games: {stats['total_games']}")

db.close()
```

## Performance Tips

1. **Batch downloads**: Download multiple months/issues in one session
2. **Vacuum after bulk insert**: `python main.py --vacuum`
3. **Use SSD**: SQLite performs much better on SSD
4. **Compress for distribution**: Use 7z or zip (50-70% compression)

## Legal Compliance

All scrapers respect:
- ✅ robots.txt
- ✅ Rate limiting
- ✅ Terms of Service
- ✅ Public domain / open licenses

**Sources:**
- **Lichess**: CC0 (public domain)
- **TWIC**: Free for download
- **Chess.com**: Public API with rate limits

## File Size Estimates

- 1 million games: ~500MB - 1GB
- 10 million games: ~5-10GB
- Compressed: 50-70% smaller

## Distribution

To distribute your database:

1. Build the database:
```bash
python main.py --twic 100
python main.py --lichess-year 2024
```

2. Optimize:
```bash
python main.py --vacuum
```

3. Compress:
```bash
7z a -mx=9 chess_games.7z chess_games.db
```

4. Include in your installer (NSIS, Inno Setup, PyInstaller)

## Advanced Usage

### Custom Python Script

```python
from database import ChessGameDatabase
from scrapers import LichessScraper, TWICScraper

# Initialize database
db = ChessGameDatabase('my_games.db')

# Download Lichess January 2025
pgn = LichessScraper.download_monthly_games(2025, 1)
db.parse_and_insert_pgn(pgn, source='lichess_2025_01')

# Download TWIC
issues = TWICScraper.get_available_issues()
for url in issues[:5]:
    pgn = TWICScraper.download_issue(url)
    if pgn:
        db.parse_and_insert_pgn(pgn, source='twic')

# Query
games = db.query_by_year(2025)
print(f"Found {len(games)} games from 2025")

db.close()
```

## Troubleshooting

### Download fails
- Check internet connection
- Verify URL is still valid
- Check if source changed their structure

### Database locked
- Close other connections
- Use WAL mode (enabled by default)

### Out of memory
- Process files in smaller batches
- Increase system swap space

## License

MIT License - Free to use for commercial and non-commercial purposes.

## Contributing

Contributions welcome! Please:
1. Respect legal sources only
2. Add tests for new scrapers
3. Update documentation

## Support

For issues or questions, please open a GitHub issue.
