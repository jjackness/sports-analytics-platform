import random
import json
import os
from datetime import datetime
import uuid
from data.nfl_data_provider import NFLDataProvider

class SimulationEngine:
    """
    Engine for simulating football games
    """
    
    def __init__(self, parameters=None, output_dir="results"):
        """
        Initialize the simulation engine with optional parameters
        
        Args:
            parameters (dict, optional): Simulation parameters
            output_dir (str): Directory to save simulation results
        """
        # Set default parameters if none provided
        if parameters is None:
            parameters = {
                'quarters': 4,
                'quarter_length': 15,  # in minutes
                'time_between_plays': 40,  # in seconds
                'first_down_distance': 10
            }
        
        self.parameters = parameters
        self.output_dir = output_dir
        
        # Team management (for web app compatibility)
        self.teams = {}
        self.default_teams = [
            {"id": "NE", "name": "Patriots", "abbreviation": "NE", "city": "New England"},
            {"id": "KC", "name": "Chiefs", "abbreviation": "KC", "city": "Kansas City"},
            {"id": "SF", "name": "49ers", "abbreviation": "SF", "city": "San Francisco"},
            {"id": "BAL", "name": "Ravens", "abbreviation": "BAL", "city": "Baltimore"}
        ]
        self.load_default_teams()
        
        # Add NFL data provider
        self.data_provider = NFLDataProvider()
        self.data_provider.load_data()
        
        # Initialize random state
        random.seed(datetime.now().timestamp())
    
    def load_default_teams(self):
        """Load default teams if no teams are provided"""
        from models.team import Team
        
        for team_data in self.default_teams:
            team = Team(
                id=team_data["id"],
                name=team_data["name"],
                abbreviation=team_data["abbreviation"],
                city=team_data["city"]
            )
            self.teams[team.id] = team
    
    def load_teams(self, teams_data):
        """
        Load teams from data
        
        Args:
            teams_data (list): List of team data dictionaries
        """
        from models.team import Team
        
        for team_data in teams_data:
            team = Team(
                id=team_data.get("id"),
                name=team_data.get("name"),
                abbreviation=team_data.get("abbreviation", ""),
                city=team_data.get("city", "")
            )
            self.teams[team.id] = team
    
    def get_team(self, team_id):
        """
        Get a team by ID
        
        Args:
            team_id (str): Team ID
            
        Returns:
            Team: Team object or None if not found
        """
        return self.teams.get(team_id)
    
    def simulate_game(self, home_team, away_team, verbose=False):
        """
        Simulate a complete football game between two teams
        
        Args:
            home_team (Team or str): Home team or team ID
            away_team (Team or str): Away team or team ID
            verbose (bool): Whether to include detailed play-by-play information
            
        Returns:
            dict: Game results
        """
        from models.game import Game
        
        # Handle string team IDs by getting the actual team objects
        if isinstance(home_team, str):
            home_team = self.get_team(home_team)
        if isinstance(away_team, str):
            away_team = self.get_team(away_team)
            
        # Ensure we have valid team objects
        if not home_team or not away_team:
            raise ValueError("Invalid team(s) provided for simulation")
        
        # Create a new game object using your existing Game class
        game = Game(home_team=home_team, away_team=away_team)
        game.home_score = 0
        game.away_score = 0
        
        # Initialization based on your existing code structure
        game.current_possession = random.choice([home_team.id, away_team.id])
        game.field_position = 25  # Starting at the 25 yard line
        game.current_down = 1
        game.yards_to_first = 10
        game.game_clock = self.parameters['quarters'] * self.parameters['quarter_length'] * 60  # in seconds
        
        # Tracking for play history
        play_history = []
        
        # Play until game ends
        max_plays = 150  # Safety limit to prevent infinite loops
        play_count = 0
        
        while game.game_clock > 0 and play_count < max_plays:
            # Get offensive and defensive teams
            if game.current_possession == home_team.id:
                offensive_team = home_team
                defensive_team = away_team
            else:
                offensive_team = away_team
                defensive_team = home_team
            
            # Simulate a play
            play_result = self.simulate_play(game, offensive_team, defensive_team)
            play_history.append(play_result)
            play_count += 1
            
            # Update game clock
            game.game_clock -= self.parameters.get('time_between_plays', 40)
            
            # Handle possession changes, scoring, etc.
            self.process_play_result(game, play_result, offensive_team, defensive_team)
        
        # Prepare game results
        results = {
            'game_id': str(uuid.uuid4()),
            'date': datetime.now().isoformat(),
            'home_team': {
                'id': home_team.id,
                'name': home_team.name,
                'score': game.home_score
            },
            'away_team': {
                'id': away_team.id,
                'name': away_team.name,
                'score': game.away_score
            },
            'play_history': play_history if verbose else [],
            'total_plays': play_count
        }
        
        return results
    
    def process_play_result(self, game, play_result, offensive_team, defensive_team):
        """
        Process the result of a play and update the game state accordingly
        """
        # If touchdown was scored
        if play_result.get('touchdown', False):
            # Update score
            if game.current_possession == game.home_team.id:
                game.home_score += 7  # Assuming extra point is good
            else:
                game.away_score += 7
            
            # Reset position after touchdown
            game.current_possession = defensive_team.id
            game.field_position = 25  # Touchback
            game.current_down = 1
            game.yards_to_first = 10
            return
        
        # If possession change occurred
        if play_result.get('possession_change', False):
            game.current_possession = defensive_team.id
            game.field_position = 100 - game.field_position  # Flip field position
            game.current_down = 1
            game.yards_to_first = 10
            return
        
        # Normal play - update down and distance
        yards_gained = play_result.get('yards_gained', 0)
        
        # Update field position
        game.field_position += yards_gained
        
        # Check if first down achieved
        if yards_gained >= game.yards_to_first:
            game.current_down = 1
            game.yards_to_first = min(10, 100 - game.field_position)  # Adjust if near goal line
        else:
            game.current_down += 1
            game.yards_to_first -= yards_gained
            
            # Check for turnover on downs
            if game.current_down > 4:
                game.current_possession = defensive_team.id
                game.field_position = 100 - game.field_position
                game.current_down = 1
                game.yards_to_first = 10
    
    def simulate_play(self, game, offensive_team, defensive_team):
        """
        Simulate a single play
        """
        # Get current situation
        down = game.current_down
        distance = game.yards_to_first
        field_position = game.field_position
        
        # Check for field goal attempt on 4th down
        if down == 4 and field_position >= 60:  # Within reasonable field goal range
            # Field goal attempt
            if random.random() < 0.75 - ((100 - field_position - 17) * 0.02):  # Simple model
                # Field goal is good
                if game.current_possession == game.home_team.id:
                    game.home_score += 3
                else:
                    game.away_score += 3
                
                return {
                    'play_type': 'field_goal',
                    'yards_gained': 0,
                    'down': down,
                    'distance': distance,
                    'field_position': field_position,
                    'possession_change': True,
                    'touchdown': False,
                    'result': 'field_goal_good'
                }
            else:
                # Field goal is missed
                return {
                    'play_type': 'field_goal',
                    'yards_gained': 0,
                    'down': down,
                    'distance': distance,
                    'field_position': field_position,
                    'possession_change': True,
                    'touchdown': False,
                    'result': 'field_goal_missed'
                }
        
        # Check for punt on 4th down
        if down == 4 and field_position < 60:  # Not in field goal range
            # Punt
            punt_distance = random.randint(35, 50)
            new_position = min(95, 100 - (100 - field_position + punt_distance))
            
            return {
                'play_type': 'punt',
                'yards_gained': 0,
                'down': down,
                'distance': distance,
                'field_position': field_position,
                'possession_change': True,
                'touchdown': False,
                'result': 'punt',
                'punt_distance': punt_distance
            }
        
        # Regular play - use data provider for play type and yards gained
        play_type = self.data_provider.get_play_type(down, distance)
        yards_gained = self.data_provider.get_yards_gained(play_type)
        
        # Initialize play result
        play_result = {
            'play_type': play_type,
            'yards_gained': yards_gained,
            'down': down,
            'distance': distance,
            'field_position': field_position,
            'possession_change': False,
            'touchdown': False
        }
        
        # Check for touchdown
        if field_position + yards_gained >= 100:
            play_result['touchdown'] = True
            play_result['yards_gained'] = 100 - field_position  # Adjust yards gained
            play_result['result'] = 'touchdown'
        
        # Random turnovers
        elif play_type == 'pass' and random.random() < 0.03:  # 3% interception chance
            play_result['possession_change'] = True
            play_result['turnover_type'] = 'interception'
            play_result['result'] = 'interception'
        elif play_type == 'run' and random.random() < 0.015:  # 1.5% fumble chance
            play_result['possession_change'] = True
            play_result['turnover_type'] = 'fumble'
            play_result['result'] = 'fumble'
        else:
            play_result['result'] = 'normal'
        
        return play_result
    
    def simulate_multiple_games(self, home_team, away_team, num_games=1, verbose=False):
        """
        Simulate multiple games between the same teams
        
        Args:
            home_team (Team or str): Home team or team ID
            away_team (Team or str): Away team or team ID
            num_games (int): Number of games to simulate
            verbose (bool): Whether to include detailed play-by-play information
            
        Returns:
            dict: Results of multiple game simulations
        """
        # Handle string team IDs
        if isinstance(home_team, str):
            home_team = self.get_team(home_team)
        if isinstance(away_team, str):
            away_team = self.get_team(away_team)
            
        # Ensure we have valid team objects
        if not home_team or not away_team:
            raise ValueError("Invalid team(s) provided for simulation")
            
        all_results = []
        
        for i in range(num_games):
            game_results = self.simulate_game(home_team, away_team, verbose=verbose)
            all_results.append(game_results)
        
        # Compile summary statistics
        home_wins = sum(1 for r in all_results if r['home_team']['score'] > r['away_team']['score'])
        away_wins = sum(1 for r in all_results if r['away_team']['score'] > r['home_team']['score'])
        ties = sum(1 for r in all_results if r['home_team']['score'] == r['away_team']['score'])
        
        avg_home_score = sum(r['home_team']['score'] for r in all_results) / num_games
        avg_away_score = sum(r['away_team']['score'] for r in all_results) / num_games
        
        summary = {
            'num_games': num_games,
            'home_team': {
                'id': home_team.id,
                'name': home_team.name,
                'wins': home_wins,
                'avg_score': avg_home_score
            },
            'away_team': {
                'id': away_team.id,
                'name': away_team.name,
                'wins': away_wins,
                'avg_score': avg_away_score
            },
            'ties': ties
        }
        
        return {
            'summary': summary,
            'games': all_results
        }
    
    def simulate_season(self, teams, schedule):
        """
        Simulate a complete season with multiple teams
        
        Args:
            teams (list): List of Team objects
            schedule (list): List of game matchups as (home_id, away_id) tuples
            
        Returns:
            dict: Season results
        """
        # Create a team lookup by ID for easy access
        team_dict = {team.id: team for team in teams}
        
        # Store all game results
        game_results = []
        
        # Store team standings
        standings = {team.id: {
            'team_id': team.id,
            'team_name': team.name,
            'wins': 0,
            'losses': 0,
            'ties': 0,
            'points_for': 0,
            'points_against': 0
        } for team in teams}
        
        # Simulate each game in the schedule
        for home_id, away_id in schedule:
            # Get team objects (handle potential string IDs)
            home_team = team_dict.get(home_id) or self.get_team(home_id)
            away_team = team_dict.get(away_id) or self.get_team(away_id)
            
            if not home_team or not away_team:
                raise ValueError(f"Invalid team IDs in schedule: {home_id}, {away_id}")
            
            result = self.simulate_game(home_team, away_team)
            game_results.append(result)
            
            # Update standings
            home_score = result['home_team']['score']
            away_score = result['away_team']['score']
            
            standings[home_id]['points_for'] += home_score
            standings[home_id]['points_against'] += away_score
            
            standings[away_id]['points_for'] += away_score
            standings[away_id]['points_against'] += home_score
            
            if home_score > away_score:
                standings[home_id]['wins'] += 1
                standings[away_id]['losses'] += 1
            elif away_score > home_score:
                standings[away_id]['wins'] += 1
                standings[home_id]['losses'] += 1
            else:
                standings[home_id]['ties'] += 1
                standings[away_id]['ties'] += 1
        
        # Convert standings to a sorted list
        standings_list = list(standings.values())
        standings_list.sort(key=lambda x: (x['wins'], x['points_for'] - x['points_against']), reverse=True)
        
        return {
            'games': game_results,
            'standings': standings_list
        }
    
    def save_results(self, results, file_prefix="simulation_batch"):
        """
        Save simulation results to a JSON file
        
        Args:
            results (dict): Simulation results
            file_prefix (str): Prefix for the filename
            
        Returns:
            str: Path to the saved file
        """
        # Generate a unique filename based on current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{file_prefix}_{timestamp}.json"
        
        # Ensure the results directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save the results
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        return filepath
    
    def load_play_calling_tendencies(self, filename="play_calling_tendencies.csv"):
        """
        Load play-calling tendencies from a CSV file (for web app compatibility)
        
        Args:
            filename (str): CSV filename
            
        Returns:
            dict: Play-calling tendencies
        """
        # This function now just uses our data provider but maintains the interface
        # for web app compatibility
        if not self.data_provider.loaded:
            self.data_provider.load_data()
        
        return self.data_provider.tendencies
    
    def save_play_calling_tendencies(self, tendencies, filename=None):
        """
        Save play-calling tendencies to a CSV file (for web app compatibility)
        
        Args:
            tendencies (dict): Play-calling tendencies
            filename (str, optional): Output filename
            
        Returns:
            str: Path to the saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"play_calling_{timestamp}.csv"
        
        # Ensure the results directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save the tendencies
        filepath = os.path.join(self.output_dir, filename)
        
        # Since our tendencies are now in a different format, we'll create a simplified
        # CSV version for backward compatibility
        with open(filepath, 'w') as f:
            f.write("down,distance,pass_percentage,run_percentage\n")
            
            for down in self.data_provider.tendencies:
                base_pass = self.data_provider.tendencies[down]['pass_percentage']
                base_run = self.data_provider.tendencies[down]['run_percentage']
                
                f.write(f"{down},all,{base_pass:.1f},{base_run:.1f}\n")
                
                # Write distance-specific rows
                for key in self.data_provider.tendencies[down]:
                    if key.startswith('distance_'):
                        # Extract distance range from key (e.g., "distance_1_to_3")
                        parts = key.split('_')
                        if len(parts) >= 4:
                            try:
                                min_dist = int(parts[1])
                                max_dist = int(parts[3])
                                dist_range = f"{min_dist}-{max_dist}"
                                
                                pass_pct = self.data_provider.tendencies[down][key]['pass_percentage']
                                run_pct = self.data_provider.tendencies[down][key]['run_percentage']
                                
                                f.write(f"{down},{dist_range},{pass_pct:.1f},{run_pct:.1f}\n")
                            except (ValueError, IndexError):
                                continue
        
        return filepath
    
    def calculate_fantasy_points(self, game_results):
        """
        Calculate fantasy points for players in a game
        
        Args:
            game_results (dict): Game results
            
        Returns:
            dict: Fantasy points by player
        """
        # Simplified fantasy points calculation for compatibility
        # In the future, we can enhance this with real player stats
        
        fantasy_points = {
            "QB1": random.randint(10, 30),
            "RB1": random.randint(5, 25),
            "WR1": random.randint(5, 25),
            "TE1": random.randint(2, 15),
            "K1": random.randint(3, 12)
        }
        
        return fantasy_points
    
    def generate_fantasy_projections(self, num_simulations=100):
        """
        Generate fantasy football projections based on simulations
        
        Args:
            num_simulations (int): Number of simulations to run
            
        Returns:
            dict: Fantasy projections
        """
        # Simplified fantasy projections for compatibility
        projections = {
            "players": [
                {"id": "QB1", "name": "Patrick Mahomes", "position": "QB", "points": 22.5},
                {"id": "RB1", "name": "Christian McCaffrey", "position": "RB", "points": 20.8},
                {"id": "WR1", "name": "Justin Jefferson", "position": "WR", "points": 18.3},
                {"id": "TE1", "name": "Travis Kelce", "position": "TE", "points": 13.7},
                {"id": "K1", "name": "Harrison Butker", "position": "K", "points": 8.5}
            ]
        }
        
        return projections
    
    def save_fantasy_projections(self, projections, filename=None):
        """
        Save fantasy projections to a CSV file
        
        Args:
            projections (dict): Fantasy projections
            filename (str, optional): Output filename
            
        Returns:
            str: Path to the saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fantasy_projections_{timestamp}.csv"
        
        # Ensure the results directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save the projections
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write("id,name,position,points\n")
            
            for player in projections.get('players', []):
                f.write(f"{player['id']},{player['name']},{player['position']},{player['points']}\n")
        
        return filepath