"""
NFL Data Provider

This module loads NFL statistical data and provides access to it for simulations.
"""

import os
import json
import random

class NFLDataProvider:
    """
    Class for loading and providing NFL statistical data
    """
    
    def __init__(self, data_dir='data/nfl_data'):
        """
        Initialize the data provider
        
        Args:
            data_dir (str): Directory containing NFL data
        """
        self.data_dir = data_dir
        self.tendencies = {}
        self.outcomes = {}
        self.loaded = False
        
    def load_data(self):
        """
        Load NFL statistical data from JSON files
        
        Returns:
            bool: True if data was loaded successfully, False otherwise
        """
        try:
            # Load play tendencies
            tendencies_path = os.path.join(self.data_dir, 'play_tendencies.json')
            with open(tendencies_path, 'r') as f:
                self.tendencies = json.load(f)
            
            # Load play outcomes
            outcomes_path = os.path.join(self.data_dir, 'play_outcomes.json')
            with open(outcomes_path, 'r') as f:
                self.outcomes = json.load(f)
                
            self.loaded = True
            return True
        
        except Exception as e:
            print(f"Error loading NFL data: {str(e)}")
            return False
    
    def get_play_type(self, down, distance):
        """
        Determine play type (pass or run) based on statistical tendencies
        
        Args:
            down (int): Down (1-4)
            distance (int): Yards to go
            
        Returns:
            str: 'pass' or 'run'
        """
        if not self.loaded:
            self.load_data()
        
        # Convert down to string for dictionary lookup
        down_str = str(down)
        
        # Default to reasonable values if data isn't available
        pass_pct = 50
        run_pct = 50
        
        # Get base percentages for this down
        if down_str in self.tendencies:
            pass_pct = self.tendencies[down_str]['pass_percentage']
            run_pct = self.tendencies[down_str]['run_percentage']
            
            # Look for more specific distance-based tendencies
            for key in self.tendencies[down_str]:
                if key.startswith('distance_'):
                    # Extract distance range from key (e.g., "distance_1_to_3")
                    parts = key.split('_')
                    if len(parts) >= 4:
                        try:
                            min_dist = int(parts[1])
                            max_dist = int(parts[3])
                            if min_dist <= distance <= max_dist:
                                pass_pct = self.tendencies[down_str][key]['pass_percentage']
                                run_pct = self.tendencies[down_str][key]['run_percentage']
                                break
                        except (ValueError, IndexError):
                            continue
        
        # Randomly determine play type based on percentages
        if random.random() * 100 < pass_pct:
            return 'pass'
        else:
            return 'run'
    
    def get_yards_gained(self, play_type):
        """
        Determine yards gained for a play based on statistical distributions
        
        Args:
            play_type (str): 'pass' or 'run'
            
        Returns:
            int: Yards gained
        """
        if not self.loaded:
            self.load_data()
        
        # Get yard distribution for this play type
        if play_type in self.outcomes and 'yards_distribution' in self.outcomes[play_type]:
            dist = self.outcomes[play_type]['yards_distribution']
            
            # Convert keys to integers and create a weighted distribution
            yards_values = []
            weights = []
            
            for yards_str, count in dist.items():
                try:
                    yards = int(yards_str)
                    yards_values.append(yards)
                    weights.append(count)
                except ValueError:
                    continue
            
            if yards_values:
                # Choose a yard value based on weighted distribution
                return random.choices(yards_values, weights=weights, k=1)[0]
        
        # Fallback to reasonable defaults if distribution data isn't available
        if play_type == 'pass':
            return random.choices(
                [-5, -2, 0, 3, 7, 12, 20, 35],
                weights=[5, 10, 30, 25, 15, 10, 4, 1],
                k=1
            )[0]
        else:  # run
            return random.choices(
                [-3, -1, 0, 1, 2, 3, 4, 8, 15, 25],
                weights=[5, 7, 10, 15, 20, 20, 10, 8, 4, 1],
                k=1
            )[0]