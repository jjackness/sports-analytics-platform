import pandas as pd
import os
import json
from datetime import datetime

class NFLDataCollector:
    """
    Class for collecting and processing NFL data using nfl_data_py package
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
        Download play-by-play data for a specific NFL season using nfl_data_py
        
        Args:
            season (int): NFL season year (e.g., 2022)
            
        Returns:
            pandas.DataFrame: Play-by-play data for the season
        """
        print(f"Downloading NFL play-by-play data for {season} season...")
        
        try:
            # Import the package here to ensure it's only needed when downloading
            import nfl_data_py as nfl
            
            # Use nfl_data_py to fetch play-by-play data
            df = nfl.import_pbp_data([season])
            
            # Save to our data directory
            output_file = os.path.join(self.data_dir, f"pbp_{season}.csv")
            df.to_csv(output_file, index=False)
            
            print(f"Successfully downloaded {len(df)} plays from {season}")
            return df
            
        except Exception as e:
            print(f"Error downloading {season} data: {str(e)}")
            return None
    
    def load_season_data(self, season):
        """
        Load play-by-play data for a season (downloads if not available)
        
        Args:
            season (int): NFL season year
            
        Returns:
            pandas.DataFrame: Play-by-play data
        """
        file_path = os.path.join(self.data_dir, f"pbp_{season}.csv")
        
        # Check if we already have the data locally
        if os.path.exists(file_path):
            print(f"Loading {season} data from local file...")
            return pd.read_csv(file_path, low_memory=False)
        else:
            # Download if we don't have it
            return self.download_season_data(season)
    
    def extract_play_tendencies(self, df):
        """
        Extract play-calling tendencies from play-by-play data
        
        Args:
            df (pandas.DataFrame): Play-by-play data
            
        Returns:
            dict: Dictionary of play tendencies by down, distance, and field position
        """
        # Filter to only include offensive plays (no kickoffs, punts, etc)
        # Note: nfl_data_py uses 'play_type_nfl' instead of 'play_type'
        if 'play_type_nfl' in df.columns:
            play_type_col = 'play_type_nfl'
        elif 'play_type' in df.columns:
            play_type_col = 'play_type'
        else:
            print("Warning: Could not find play type column")
            return {}
            
        offensive_plays = df[df[play_type_col].isin(['PASS', 'RUSH', 'pass', 'run'])]
        
        # Standardize play types
        offensive_plays['std_play_type'] = offensive_plays[play_type_col].apply(
            lambda x: 'pass' if x.upper() == 'PASS' else 'run'
        )
        
        # Group by down, distance ranges, and field position
        tendencies = {}
        
        # Process by down
        for down in range(1, 5):
            down_plays = offensive_plays[offensive_plays['down'] == down]
            
            # Skip if no plays for this down
            if len(down_plays) == 0:
                continue
                
            tendencies[down] = {
                'total_plays': len(down_plays),
                'pass_percentage': len(down_plays[down_plays['std_play_type'] == 'pass']) / len(down_plays) * 100,
                'run_percentage': len(down_plays[down_plays['std_play_type'] == 'run']) / len(down_plays) * 100
            }
            
            # Add distance-based tendencies
            distance_ranges = [(1, 3), (4, 6), (7, 10), (11, 15), (16, 100)]
            for dist_min, dist_max in distance_ranges:
                dist_plays = down_plays[(down_plays['ydstogo'] >= dist_min) & (down_plays['ydstogo'] <= dist_max)]
                
                if len(dist_plays) == 0:
                    continue
                    
                key = f"distance_{dist_min}_to_{dist_max}"
                tendencies[down][key] = {
                    'total_plays': len(dist_plays),
                    'pass_percentage': len(dist_plays[dist_plays['std_play_type'] == 'pass']) / len(dist_plays) * 100,
                    'run_percentage': len(dist_plays[dist_plays['std_play_type'] == 'run']) / len(dist_plays) * 100
                }
        
        return tendencies
    
    def extract_play_outcomes(self, df):
        """
        Extract play outcome statistics (yards gained, etc.)
        
        Args:
            df (pandas.DataFrame): Play-by-play data
            
        Returns:
            dict: Dictionary of play outcome statistics
        """
        # Identify play type column
        if 'play_type_nfl' in df.columns:
            play_type_col = 'play_type_nfl'
        elif 'play_type' in df.columns:
            play_type_col = 'play_type'
        else:
            print("Warning: Could not find play type column")
            return {}
        
        # Identify yards gained column
        if 'yards_gained' in df.columns:
            yards_col = 'yards_gained'
        elif 'yards_gained_nfl' in df.columns:
            yards_col = 'yards_gained_nfl'
        else:
            print("Warning: Could not find yards gained column")
            return {}
        
        # Filter to only include offensive plays
        offensive_plays = df[df[play_type_col].isin(['PASS', 'RUSH', 'pass', 'run'])].copy()
        
        # Standardize play types
        offensive_plays['std_play_type'] = offensive_plays[play_type_col].apply(
            lambda x: 'pass' if x.upper() == 'PASS' else 'run'
        )
        
        # Clean up NaN values in yards
        offensive_plays[yards_col] = offensive_plays[yards_col].fillna(0)
        
        outcomes = {}
        
        for play_type in ['pass', 'run']:
            type_plays = offensive_plays[offensive_plays['std_play_type'] == play_type]
            
            if len(type_plays) == 0:
                continue
                
            # Calculate yards distribution but limit to prevent huge JSON files
            yards_dist = type_plays[yards_col].value_counts().to_dict()
            # Convert keys to strings for JSON compatibility and limit to most common values
            yards_dist = {str(k): int(v) for k, v in sorted(yards_dist.items(), key=lambda x: x[1], reverse=True)[:50]}
            
            outcomes[play_type] = {
                'count': len(type_plays),
                'yards_mean': float(type_plays[yards_col].mean()),
                'yards_median': float(type_plays[yards_col].median()),
                'success_rate': float(len(type_plays[type_plays[yards_col] > 0]) / len(type_plays) * 100),
                'yards_distribution': yards_dist
            }
        
        return outcomes
    
    def save_tendencies(self, tendencies, filename='play_tendencies.json'):
        """Save tendencies to a JSON file"""
        with open(os.path.join(self.data_dir, filename), 'w') as f:
            json.dump(tendencies, f, indent=2)
        
    def save_outcomes(self, outcomes, filename='play_outcomes.json'):
        """Save outcomes to a JSON file"""
        with open(os.path.join(self.data_dir, filename), 'w') as f:
            json.dump(outcomes, f, indent=2)