import requests
from bs4 import BeautifulSoup
import time
import logging
import bz2
import zipfile
import io
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LichessScraper:
    """Scraper for Lichess database dumps"""
    
    BASE_URL = "https://database.lichess.org"
    
    @staticmethod
    def download_monthly_games(year, month, rated=True):
        """
        Download Lichess monthly database
        
        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)
            rated: True for rated games, False for casual
        
        Returns:
            PGN text content
        """
        game_type = "rated" if rated else "casual"
        url = f"{LichessScraper.BASE_URL}/standard/lichess_db_standard_{game_type}_{year}-{month:02d}.pgn.bz2"
        
        logger.info(f"Downloading from {url}")
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size for progress bar
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress bar
            compressed_data = b""
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Downloading {year}-{month:02d}") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    compressed_data += chunk
                    pbar.update(len(chunk))
            
            # Decompress
            logger.info("Decompressing...")
            pgn_data = bz2.decompress(compressed_data)
            
            return pgn_data.decode('utf-8', errors='ignore')
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download: {e}")
            return None
    
    @staticmethod
    def download_year_games(year, rated=True):
        """Download all games from a specific year"""
        all_pgn = ""
        for month in range(1, 13):
            pgn = LichessScraper.download_monthly_games(year, month, rated)
            if pgn:
                all_pgn += pgn
                time.sleep(2)  # Be polite
        return all_pgn


class TWICScraper:
    """Scraper for The Week in Chess (TWIC)"""
    
    BASE_URL = "https://theweekinchess.com"
    
    @staticmethod
    def get_available_issues():
        """Get list of available TWIC issues"""
        try:
            response = requests.get(f"{TWICScraper.BASE_URL}/twic", timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            issues = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'twic' in href.lower() and ('.pgn' in href.lower() or '.zip' in href.lower()):
                    if not href.startswith('http'):
                        href = f"{TWICScraper.BASE_URL}{href}"
                    issues.append(href)
            
            logger.info(f"Found {len(issues)} TWIC issues")
            return issues
        
        except Exception as e:
            logger.error(f"Failed to get TWIC issues: {e}")
            return []
    
    @staticmethod
    def download_issue(url):
        """Download a TWIC issue (PGN or ZIP)"""
        try:
            logger.info(f"Downloading {url}")
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # Check if it's a ZIP file
            if url.endswith('.zip'):
                return TWICScraper._extract_zip(response.content)
            else:
                return response.text
        
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None
    
    @staticmethod
    def _extract_zip(zip_content):
        """Extract PGN from ZIP file"""
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
                pgn_content = ""
                for filename in zf.namelist():
                    if filename.endswith('.pgn'):
                        pgn_content += zf.read(filename).decode('utf-8', errors='ignore')
                return pgn_content
        except Exception as e:
            logger.error(f"Failed to extract ZIP: {e}")
            return None
    
    @staticmethod
    def download_latest(count=10):
        """Download latest N issues"""
        issues = TWICScraper.get_available_issues()
        all_pgn = ""
        
        for url in issues[:count]:
            pgn = TWICScraper.download_issue(url)
            if pgn:
                all_pgn += pgn
            time.sleep(2)  # Be polite
        
        return all_pgn


class ChesscomScraper:
    """Scraper for Chess.com public API"""
    
    BASE_URL = "https://api.chess.com/pub"
    
    @staticmethod
    def get_player_games(username, year, month):
        """
        Get games for a specific player and month
        
        Args:
            username: Chess.com username
            year: Year
            month: Month (1-12)
        
        Returns:
            List of games in PGN format
        """
        url = f"{ChesscomScraper.BASE_URL}/player/{username}/games/{year}/{month:02d}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            games = data.get('games', [])
            
            # Convert to PGN
            pgn_text = ""
            for game in games:
                if 'pgn' in game:
                    pgn_text += game['pgn'] + "\n\n"
            
            return pgn_text
        
        except Exception as e:
            logger.error(f"Failed to get games for {username}: {e}")
            return None
    
    @staticmethod
    def get_titled_players():
        """Get list of titled players (GM, IM, etc.)"""
        try:
            response = requests.get(f"{ChesscomScraper.BASE_URL}/titled/GM", timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('players', [])
        
        except Exception as e:
            logger.error(f"Failed to get titled players: {e}")
            return []


class PGNMentorScraper:
    """Scraper for PGN Mentor free databases"""
    
    BASE_URL = "https://www.pgnmentor.com"
    
    @staticmethod
    def get_available_databases():
        """Get list of available free databases"""
        databases = {
            'players': f"{PGNMentorScraper.BASE_URL}/players.html",
            'events': f"{PGNMentorScraper.BASE_URL}/events.html",
            'openings': f"{PGNMentorScraper.BASE_URL}/openings.html"
        }
        return databases
    
    @staticmethod
    def download_database(category, name):
        """
        Download a specific database
        
        Args:
            category: 'players', 'events', or 'openings'
            name: Database name (e.g., 'Kasparov')
        
        Returns:
            PGN text content
        """
        # Note: This is a simplified version
        # Actual implementation would need to parse the HTML to find download links
        url = f"{PGNMentorScraper.BASE_URL}/files/{name}.zip"
        
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # Extract ZIP
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                pgn_content = ""
                for filename in zf.namelist():
                    if filename.endswith('.pgn'):
                        pgn_content += zf.read(filename).decode('utf-8', errors='ignore')
                return pgn_content
        
        except Exception as e:
            logger.error(f"Failed to download {name}: {e}")
            return None


class GenericPGNDownloader:
    """Generic downloader for direct PGN URLs"""
    
    @staticmethod
    def download(url):
        """Download PGN from any URL"""
        try:
            logger.info(f"Downloading from {url}")
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            
            # Handle different content types
            if 'zip' in content_type or url.endswith('.zip'):
                return GenericPGNDownloader._extract_zip(response.content)
            elif 'bz2' in content_type or url.endswith('.bz2'):
                return bz2.decompress(response.content).decode('utf-8', errors='ignore')
            else:
                return response.text
        
        except Exception as e:
            logger.error(f"Failed to download from {url}: {e}")
            return None
    
    @staticmethod
    def _extract_zip(zip_content):
        """Extract PGN from ZIP"""
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
                pgn_content = ""
                for filename in zf.namelist():
                    if filename.endswith('.pgn'):
                        pgn_content += zf.read(filename).decode('utf-8', errors='ignore')
                return pgn_content
        except Exception as e:
            logger.error(f"Failed to extract ZIP: {e}")
            return None
