"""
Simple NFL Data Collector

This module downloads and processes NFL data using simple HTTP requests
instead of requiring specialized packages.
"""

import os
import json
import csv
import urllib.request
from urllib.error import URLError
import gzip
import shutil
from collections import defaultdict

class SimpleNFLDataCollector:
    """
    Class for collecting and processing NFL data using direct HTTP requests
    """
    
    def __init__(self, data_dir='data/nfl_data'):
        """
        Initialize the data collector
        
        Args:
            data_dir (str): Directory to store downloaded NFL data
        """
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def download_season_data(self, season):
        """
        Download play-by-play data for a specific NFL season
        
        Args:
            season (int): NFL season year (e.g., 2022)
            
        Returns:
            list: List of play dictionaries if successful, None otherwise
        """
        print(f"Downloading NFL play-by-play data for {season} season...")
        
        # File paths
        gz_file = os.path.join(self.data_dir, f"pbp_{season}.csv.gz")
        csv_file = os.path.join(self.data_dir, f"pbp_{season}.csv")
        
        # URL for NFL data (from nflverse GitHub repository)
        url = f"https://github.com/nflverse/nflfastR-data/raw/master/data/play_by_play_{season}.csv.gz"
        
        try:
            # Download the gzipped file
            print(f"Downloading from {url}...")
            urllib.request.urlretrieve(url, gz_file)
            
            # Uncompress the gzipped file
            with gzip.open(gz_file, 'rb') as f_in:
                with open(csv_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Read the CSV file
            plays = self.read_csv_to_dict(csv_file)
            print(f"Successfully downloaded {len(plays)} plays from {season}")
            
            return plays
            
        except URLError as e:
            print(f"Error downloading {season} data: {str(e)}")
            return None
        except Exception as e:
            print(f"Error processing {season} data: {str(e)}")
            return None
    
    def read_csv_to_dict(self, csv_file):
        """
        Read a CSV file into a list of dictionaries
        
        Args:
            csv_file (str): Path to CSV file
            
        Returns:
            list: List of dictionaries, one per row
        """
        plays = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                plays.append(row)
        
        return plays
    
    def load_season_data(self, season):
        """
        Load play-by-play data for a season (downloads if not available)
        
        Args:
            season (int): NFL season year
            
        Returns:
            list: List of play dictionaries
        """
        csv_file = os.path.join(self.data_dir, f"pbp_{season}.csv")
        
        # Check if we already have the data locally
        if os.path.exists(csv_file):
            print(f"Loading {season} data from local file...")
            return self.read_csv_to_dict(csv_file)
        else:
            # Download if we don't have it
            return self.download_season_data(season)
    
    def extract_play_tendencies(self, plays):
        """
        Extract play-calling tendencies from play-by-play data
        
        Args:
            plays (list): List of play dictionaries
            
        Returns:
            dict: Dictionary of play tendencies by down, distance, and field position
        """
        # Filter to only include offensive plays (no kickoffs, punts, etc)
        offensive_plays = [p for p in plays if p.get('play_type') in ['pass', 'run']]
        
        # Group plays by down
        plays_by_down = defaultdict(list)
        for play in offensive_plays:
            try:
                down = int(play.get('down', 0))
                if down > 0:
                    plays_by_down[down].append(play)
            except (ValueError, TypeError):
                continue
        
        # Calculate tendencies
        tendencies = {}
        
        for down in range(1, 5):
            down_plays = plays_by_down.get(down, [])
            
            # Skip if no plays for this down
            if not down_plays:
                continue
            
            # Count play types
            pass_plays = sum(1 for p in down_plays if p.get('play_type') == 'pass')
            run_plays = sum(1 for p in down_plays if p.get('play_type') == 'run')
            total_plays = pass_plays + run_plays
            
            if total_plays == 0:
                continue
                
            tendencies[down] = {
                'total_plays': total_plays,
                'pass_percentage': (pass_plays / total_plays) * 100,
                'run_percentage': (run_plays / total_plays) * 100
            }
            
            # Group by distance ranges
            distance_ranges = [(1, 3), (4, 6), (7, 10), (11, 15), (16, 100)]
            
            for dist_min, dist_max in distance_ranges:
                # Filter plays by distance
                dist_plays = []
                for play in down_plays:
                    try:
                        yards_to_go = int(float(play.get('ydstogo', 0)))
                        if dist_min <= yards_to_go <= dist_max:
                            dist_plays.append(play)
                    except (ValueError, TypeError):
                        continue
                
                if not dist_plays:
                    continue
                
                # Count play types within this distance range
                pass_plays = sum(1 for p in dist_plays if p.get('play_type') == 'pass')
                run_plays = sum(1 for p in dist_plays if p.get('play_type') == 'run')
                total_plays = pass_plays + run_plays
                
                if total_plays == 0:
                    continue
                    
                key = f"distance_{dist_min}_to_{dist_max}"
                tendencies[down][key] = {
                    'total_plays': total_plays,
                    'pass_percentage': (pass_plays / total_plays) * 100,
                    'run_percentage': (run_plays / total_plays) * 100
                }
        
        return tendencies
    
    def extract_play_outcomes(self, plays):
        """
        Extract play outcome statistics (yards gained, etc.)
        
        Args:
            plays (list): List of play dictionaries
            
        Returns:
            dict: Dictionary of play outcome statistics
        """
        # Filter to only include offensive plays
        pass_plays = [p for p in plays if p.get('play_type') == 'pass']
        run_plays = [p for p in plays if p.get('play_type') == 'run']
        
        outcomes = {}
        
        # Process pass plays
        if pass_plays:
            # Extract yards gained
            yards_gained = []
            for play in pass_plays:
                try:
                    yards = float(play.get('yards_gained', 0))
                    yards_gained.append(yards)
                except (ValueError, TypeError):
                    continue
            
            if yards_gained:
                # Sort yards for calculating median
                sorted_yards = sorted(yards_gained)
                median_idx = len(sorted_yards) // 2
                
                # Calculate yards distribution
                yards_dist = defaultdict(int)
                for yards in yards_gained:
                    yards_dist[int(yards)] += 1
                
                # Convert to dictionary with string keys (for JSON)
                yards_dist_dict = {str(k): v for k, v in sorted(yards_dist.items(), 
                                                              key=lambda x: x[1], 
                                                              reverse=True)[:50]}
                
                # Calculate success rate (positive yards)
                success_count = sum(1 for y in yards_gained if y > 0)
                
                outcomes['pass'] = {
                    'count': len(yards_gained),
                    'yards_mean': sum(yards_gained) / len(yards_gained),
                    'yards_median': sorted_yards[median_idx],
                    'success_rate': (success_count / len(yards_gained)) * 100,
                    'yards_distribution': yards_dist_dict
                }
        
        # Process run plays
        if run_plays:
            # Extract yards gained
            yards_gained = []
            for play in run_plays:
                try:
                    yards = float(play.get('yards_gained', 0))
                    yards_gained.append(yards)
                except (ValueError, TypeError):
                    continue
            
            if yards_gained:
                # Sort yards for calculating median
                sorted_yards = sorted(yards_gained)
                median_idx = len(sorted_yards) // 2
                
                # Calculate yards distribution
                yards_dist = defaultdict(int)
                for yards in yards_gained:
                    yards_dist[int(yards)] += 1
                
                # Convert to dictionary with string keys (for JSON)
                yards_dist_dict = {str(k): v for k, v in sorted(yards_dist.items(), 
                                                              key=lambda x: x[1], 
                                                              reverse=True)[:50]}
                
                # Calculate success rate (positive yards)
                success_count = sum(1 for y in yards_gained if y > 0)
                
                outcomes['run'] = {
                    'count': len(yards_gained),
                    'yards_mean': sum(yards_gained) / len(yards_gained),
                    'yards_median': sorted_yards[median_idx],
                    'success_rate': (success_count / len(yards_gained)) * 100,
                    'yards_distribution': yards_dist_dict
                }
        
        return outcomes
    
    def save_tendencies(self, tendencies, filename='play_tendencies.json'):
        """Save tendencies to a JSON file"""
        file_path = os.path.join(self.data_dir, filename)
        with open(file_path, 'w') as f:
            json.dump(tendencies, f, indent=2)
        print(f"Saved tendencies to {file_path}")
        
    def save_outcomes(self, outcomes, filename='play_outcomes.json'):
        """Save outcomes to a JSON file"""
        file_path = os.path.join(self.data_dir, filename)
        with open(file_path, 'w') as f:
            json.dump(outcomes, f, indent=2)
        print(f"Saved outcomes to {file_path}")