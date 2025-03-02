"""
NFL Data Generator

This module creates synthetic NFL play-by-play data based on realistic statistics
for use in football simulations when actual NFL data is not accessible.
"""

import os
import json
import random
import time
from datetime import datetime
import csv

class NFLDataGenerator:
    """
    Class for generating synthetic NFL play-by-play data with realistic statistics
    """
    
    def __init__(self, data_dir='data/nfl_data'):
        """
        Initialize the data generator
        
        Args:
            data_dir (str): Directory to store generated NFL data
        """
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Set realistic play distribution parameters
        self.play_distributions = {
            # Down-based play calling percentages (pass vs run)
            'down_tendencies': {
                1: {'pass': 48.3, 'run': 51.7},
                2: {'pass': 56.7, 'run': 43.3},
                3: {'pass': 72.8, 'run': 27.2},
                4: {'pass': 65.2, 'run': 34.8}
            },
            
            # Distance-based adjustments (percentage points to add to pass probability)
            'distance_adjustments': {
                (1, 3): -12.0,    # Short yardage: more likely to run
                (4, 6): -2.0,     # Medium-short distance
                (7, 10): 5.0,     # Medium distance: more likely to pass
                (11, 15): 15.0,   # Long distance: much more likely to pass
                (16, 100): 20.0   # Very long distance: strongly favor passing
            },
            
            # Pass play yard distributions (realistic NFL averages)
            'pass_yards': {
                'incomplete': 27.0,      # % of passes that are incomplete (0 yards)
                'loss': 8.0,             # % of passes that lose yards
                'short': 30.0,           # % of passes that gain 1-5 yards
                'medium': 22.0,          # % of passes that gain 6-15 yards
                'long': 10.0,            # % of passes that gain 16-25 yards
                'explosive': 3.0,        # % of passes that gain 26+ yards
                # Loss distribution when a play loses yards
                'loss_dist': {'min': -1, 'max': -12, 'mean': -3.5},
                # Yard distributions for each category
                'short_dist': {'min': 1, 'max': 5, 'mean': 3.2},
                'medium_dist': {'min': 6, 'max': 15, 'mean': 9.8},
                'long_dist': {'min': 16, 'max': 25, 'mean': 19.5},
                'explosive_dist': {'min': 26, 'max': 80, 'mean': 35.0}
            },
            
            # Run play yard distributions (realistic NFL averages)
            'run_yards': {
                'loss': 12.0,            # % of runs that lose yards
                'no_gain': 10.0,         # % of runs that gain 0 yards
                'short': 55.0,           # % of runs that gain 1-4 yards
                'medium': 15.0,          # % of runs that gain 5-9 yards
                'long': 6.0,             # % of runs that gain 10-19 yards
                'explosive': 2.0,        # % of runs that gain 20+ yards
                # Loss distribution when a play loses yards
                'loss_dist': {'min': -1, 'max': -8, 'mean': -2.3},
                # Yard distributions for each category
                'short_dist': {'min': 1, 'max': 4, 'mean': 2.7},
                'medium_dist': {'min': 5, 'max': 9, 'mean': 6.8},
                'long_dist': {'min': 10, 'max': 19, 'mean': 13.5},
                'explosive_dist': {'min': 20, 'max': 80, 'mean': 28.0}
            }
        }
    
    def generate_random_yards(self, distribution):
        """
        Generate random yards based on a distribution
        
        Args:
            distribution (dict): Dictionary with min, max, and mean values
            
        Returns:
            int: Random yard value
        """
        # Use triangular distribution to bias toward the mean
        return round(random.triangular(
            distribution['min'], 
            distribution['max'], 
            distribution['mean']
        ))
    
    def determine_play_type(self, down, distance):
        """
        Determine play type (pass or run) based on down and distance
        
        Args:
            down (int): Down (1-4)
            distance (int): Yards to go
            
        Returns:
            str: 'pass' or 'run'
        """
        # Get base pass probability for this down
        pass_pct = self.play_distributions['down_tendencies'][down]['pass']
        
        # Adjust based on distance
        for dist_range, adjustment in self.play_distributions['distance_adjustments'].items():
            min_dist, max_dist = dist_range
            if min_dist <= distance <= max_dist:
                pass_pct += adjustment
                break
        
        # Ensure percentage is within bounds
        pass_pct = max(30, min(90, pass_pct))
        
        # Randomly determine play type
        if random.random() * 100 < pass_pct:
            return 'pass'
        else:
            return 'run'
    
    def determine_yards_gained(self, play_type):
        """
        Determine yards gained for a play
        
        Args:
            play_type (str): 'pass' or 'run'
            
        Returns:
            int: Yards gained
        """
        dist_key = f"{play_type}_yards"
        distributions = self.play_distributions[dist_key]
        
        # Generate a random number to determine the play outcome category
        rand_pct = random.random() * 100
        
        # For pass plays
        if play_type == 'pass':
            if rand_pct < distributions['incomplete']:
                return 0  # Incomplete pass
            
            rand_pct -= distributions['incomplete']
            if rand_pct < distributions['loss']:
                return self.generate_random_yards(distributions['loss_dist'])
            
            rand_pct -= distributions['loss']
            if rand_pct < distributions['short']:
                return self.generate_random_yards(distributions['short_dist'])
            
            rand_pct -= distributions['short']
            if rand_pct < distributions['medium']:
                return self.generate_random_yards(distributions['medium_dist'])
            
            rand_pct -= distributions['medium']
            if rand_pct < distributions['long']:
                return self.generate_random_yards(distributions['long_dist'])
            
            # Must be explosive
            return self.generate_random_yards(distributions['explosive_dist'])
        
        # For run plays
        else:
            if rand_pct < distributions['loss']:
                return self.generate_random_yards(distributions['loss_dist'])
            
            rand_pct -= distributions['loss']
            if rand_pct < distributions['no_gain']:
                return 0  # No gain
            
            rand_pct -= distributions['no_gain']
            if rand_pct < distributions['short']:
                return self.generate_random_yards(distributions['short_dist'])
            
            rand_pct -= distributions['short']
            if rand_pct < distributions['medium']:
                return self.generate_random_yards(distributions['medium_dist'])
            
            rand_pct -= distributions['medium']
            if rand_pct < distributions['long']:
                return self.generate_random_yards(distributions['long_dist'])
            
            # Must be explosive
            return self.generate_random_yards(distributions['explosive_dist'])
    
    def generate_play(self, play_id, game_id, down, distance):
        """
        Generate a realistic football play
        
        Args:
            play_id (int): Unique play ID
            game_id (int): Game ID
            down (int): Down (1-4)
            distance (int): Yards to go
            
        Returns:
            dict: Play information
        """
        play_type = self.determine_play_type(down, distance)
        yards_gained = self.determine_yards_gained(play_type)
        
        return {
            'play_id': str(play_id),
            'game_id': str(game_id),
            'play_type': play_type,
            'down': str(down),
            'ydstogo': str(distance),
            'yards_gained': str(yards_gained),
            'first_down': '1' if yards_gained >= distance else '0'
        }
    
    def generate_game(self, game_id, num_plays=150):
        """
        Generate plays for an entire game
        
        Args:
            game_id (int): Game ID
            num_plays (int): Number of plays to generate
            
        Returns:
            list: List of play dictionaries
        """
        plays = []
        
        for play_id in range(1, num_plays + 1):
            # Realistic down and distance distribution
            down = random.choices([1, 2, 3, 4], weights=[40, 30, 25, 5])[0]
            
            # Realistic distance distribution based on down
            if down == 1:
                distance = 10  # First down is almost always 10 yards
            elif down == 2:
                distance = random.choices(
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    weights=[3, 4, 5, 6, 7, 10, 15, 15, 14, 10, 5, 3, 1, 1, 1]
                )[0]
            elif down == 3:
                distance = random.choices(
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20],
                    weights=[10, 12, 12, 10, 8, 7, 6, 5, 5, 10, 5, 4, 3, 3]
                )[0]
            else:  # 4th down
                distance = random.choices(
                    [1, 2, 3, 4, 5, 10, 15],
                    weights=[25, 20, 15, 15, 10, 10, 5]
                )[0]
                
            play = self.generate_play(play_id, game_id, down, distance)
            plays.append(play)
            
        return plays
    
    def generate_season_data(self, num_games=256):  # NFL regular season has 272 games (17 games * 32 teams / 2)
        """
        Generate play-by-play data for an entire season
        
        Args:
            num_games (int): Number of games to generate
            
        Returns:
            list: List of all plays
        """
        all_plays = []
        
        print(f"Generating data for {num_games} NFL games...")
        for game_id in range(1, num_games + 1):
            # Generate random number of plays per game (between 120-170)
            num_plays = random.randint(120, 170)
            game_plays = self.generate_game(game_id, num_plays)
            all_plays.extend(game_plays)
            
            # Show progress
            if game_id % 10 == 0 or game_id == num_games:
                print(f"Generated {game_id} games ({len(all_plays)} plays)...")
                
        print(f"Completed generating {len(all_plays)} plays across {num_games} games")
        return all_plays
    
    def save_plays_to_csv(self, plays, filename='synthetic_pbp.csv'):
        """
        Save plays to a CSV file
        
        Args:
            plays (list): List of play dictionaries
            filename (str): Output filename
        """
        file_path = os.path.join(self.data_dir, filename)
        
        # Get all field names from the plays
        fieldnames = set()
        for play in plays:
            fieldnames.update(play.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(plays)
            
        print(f"Saved {len(plays)} plays to {file_path}")
        return file_path
    
    def extract_play_tendencies(self, plays):
        """
        Extract play-calling tendencies from play data
        
        Args:
            plays (list): List of play dictionaries
            
        Returns:
            dict: Dictionary of play tendencies by down, distance, and field position
        """
        # Group plays by down
        plays_by_down = {}
        for play in plays:
            down = int(play['down'])
            if down not in plays_by_down:
                plays_by_down[down] = []
            plays_by_down[down].append(play)
        
        # Calculate tendencies
        tendencies = {}
        
        for down in range(1, 5):
            if down not in plays_by_down:
                continue
                
            down_plays = plays_by_down[down]
            pass_plays = [p for p in down_plays if p['play_type'] == 'pass']
            run_plays = [p for p in down_plays if p['play_type'] == 'run']
            
            tendencies[down] = {
                'total_plays': len(down_plays),
                'pass_percentage': (len(pass_plays) / len(down_plays)) * 100,
                'run_percentage': (len(run_plays) / len(down_plays)) * 100
            }
            
            # Add distance-based tendencies
            distance_ranges = [(1, 3), (4, 6), (7, 10), (11, 15), (16, 100)]
            
            for dist_min, dist_max in distance_ranges:
                # Filter plays by distance
                dist_plays = [p for p in down_plays if dist_min <= int(p['ydstogo']) <= dist_max]
                
                if not dist_plays:
                    continue
                    
                dist_pass_plays = [p for p in dist_plays if p['play_type'] == 'pass']
                dist_run_plays = [p for p in dist_plays if p['play_type'] == 'run']
                
                key = f"distance_{dist_min}_to_{dist_max}"
                tendencies[down][key] = {
                    'total_plays': len(dist_plays),
                    'pass_percentage': (len(dist_pass_plays) / len(dist_plays)) * 100,
                    'run_percentage': (len(dist_run_plays) / len(dist_plays)) * 100
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
        pass_plays = [p for p in plays if p['play_type'] == 'pass']
        run_plays = [p for p in plays if p['play_type'] == 'run']
        
        outcomes = {}
        
        # Process pass plays
        if pass_plays:
            pass_yards = [int(p['yards_gained']) for p in pass_plays]
            
            # Calculate yards distribution (limited to top 50 values)
            yards_dist = {}
            for yards in pass_yards:
                if str(yards) not in yards_dist:
                    yards_dist[str(yards)] = 0
                yards_dist[str(yards)] += 1
            
            # Sort by frequency and limit to top 50
            yards_dist = {k: v for k, v in sorted(yards_dist.items(), 
                                                key=lambda x: int(x[1]), 
                                                reverse=True)[:50]}
            
            outcomes['pass'] = {
                'count': len(pass_plays),
                'yards_mean': sum(pass_yards) / len(pass_yards),
                'yards_median': sorted(pass_yards)[len(pass_yards) // 2],
                'success_rate': (sum(1 for y in pass_yards if y > 0) / len(pass_yards)) * 100,
                'yards_distribution': yards_dist
            }
        
        # Process run plays
        if run_plays:
            run_yards = [int(p['yards_gained']) for p in run_plays]
            
            # Calculate yards distribution (limited to top 50 values)
            yards_dist = {}
            for yards in run_yards:
                if str(yards) not in yards_dist:
                    yards_dist[str(yards)] = 0
                yards_dist[str(yards)] += 1
            
            # Sort by frequency and limit to top 50
            yards_dist = {k: v for k, v in sorted(yards_dist.items(), 
                                                key=lambda x: int(x[1]), 
                                                reverse=True)[:50]}
            
            outcomes['run'] = {
                'count': len(run_plays),
                'yards_mean': sum(run_yards) / len(run_plays),
                'yards_median': sorted(run_yards)[len(run_yards) // 2],
                'success_rate': (sum(1 for y in run_yards if y > 0) / len(run_plays)) * 100,
                'yards_distribution': yards_dist
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