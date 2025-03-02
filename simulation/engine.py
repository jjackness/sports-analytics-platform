import random
import json
import os
import math
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
        
        # Default player data by team
        self.default_players = {
            "NE": [
                {"id": "NE_QB1", "name": "Mac Jones", "position": "QB", "team_id": "NE"},
                {"id": "NE_RB1", "name": "Rhamondre Stevenson", "position": "RB", "team_id": "NE"},
                {"id": "NE_WR1", "name": "DeVante Parker", "position": "WR", "team_id": "NE"},
                {"id": "NE_WR2", "name": "JuJu Smith-Schuster", "position": "WR", "team_id": "NE"},
                {"id": "NE_TE1", "name": "Hunter Henry", "position": "TE", "team_id": "NE"}
            ],
            "KC": [
                {"id": "KC_QB1", "name": "Patrick Mahomes", "position": "QB", "team_id": "KC"},
                {"id": "KC_RB1", "name": "Isiah Pacheco", "position": "RB", "team_id": "KC"},
                {"id": "KC_WR1", "name": "Rashee Rice", "position": "WR", "team_id": "KC"},
                {"id": "KC_WR2", "name": "Kadarius Toney", "position": "WR", "team_id": "KC"},
                {"id": "KC_TE1", "name": "Travis Kelce", "position": "TE", "team_id": "KC"}
            ],
            "SF": [
                {"id": "SF_QB1", "name": "Brock Purdy", "position": "QB", "team_id": "SF"},
                {"id": "SF_RB1", "name": "Christian McCaffrey", "position": "RB", "team_id": "SF"},
                {"id": "SF_WR1", "name": "Deebo Samuel", "position": "WR", "team_id": "SF"},
                {"id": "SF_WR2", "name": "Brandon Aiyuk", "position": "WR", "team_id": "SF"},
                {"id": "SF_TE1", "name": "George Kittle", "position": "TE", "team_id": "SF"}
            ],
            "BAL": [
                {"id": "BAL_QB1", "name": "Lamar Jackson", "position": "QB", "team_id": "BAL"},
                {"id": "BAL_RB1", "name": "J.K. Dobbins", "position": "RB", "team_id": "BAL"},
                {"id": "BAL_WR1", "name": "Rashod Bateman", "position": "WR", "team_id": "BAL"},
                {"id": "BAL_WR2", "name": "Zay Flowers", "position": "WR", "team_id": "BAL"},
                {"id": "BAL_TE1", "name": "Mark Andrews", "position": "TE", "team_id": "BAL"}
            ]
        }
    
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
    
    def get_players_for_team(self, team_id):
        """
        Get the list of players for a specific team
        
        Args:
            team_id (str): Team ID
            
        Returns:
            list: List of player dictionaries
        """
        return self.default_players.get(team_id, [])
    
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
    
    # Get players for both teams
    home_players = self.get_players_for_team(home_team.id)
    away_players = self.get_players_for_team(away_team.id)
    
    # Initialize player stats
    player_stats = self.initialize_player_stats(home_players + away_players)
    
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
            offensive_players = home_players
            defensive_team = away_team
        else:
            offensive_team = away_team
            offensive_players = away_players
            defensive_team = home_team
        
        # Simulate a play
        play_result = self.simulate_play(game, offensive_team, defensive_team)
        
        # Update player statistics based on the play
        play_result = self.update_player_stats(play_result, offensive_players, player_stats)
        
        play_history.append(play_result)
        play_count += 1
        
        # Update game clock
        game.game_clock -= self.parameters.get('time_between_plays', 40)
        
        # Handle possession changes, scoring, etc.
        self.process_play_result(game, play_result, offensive_team, defensive_team)
    
    # Calculate fantasy points for players
    fantasy_points = self.calculate_fantasy_points_from_stats(player_stats)
    
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
        'total_plays': play_count,
        'player_stats': player_stats,
        'fantasy_points': fantasy_points
    }
    
    # Format player stats for the web interface
    web_player_stats = []
    for player_id, stats in player_stats.items():
        # Create a web-friendly format
        web_stats = {
            'id': player_id,
            'name': stats.get('player_name', 'Unknown'),
            'team': stats.get('team_id', ''),
            'position': stats.get('position', ''),
            'stats': {}
        }
        
        # Add position-specific stats
        if stats.get('position') == 'QB':
            web_stats['stats'] = {
                'pass_att': stats.get('pass_attempts', 0),
                'pass_comp': stats.get('pass_completions', 0),
                'pass_yds': stats.get('pass_yards', 0),
                'pass_tds': stats.get('pass_tds', 0),
                'int': stats.get('interceptions', 0),
                'rush_att': stats.get('rush_attempts', 0),
                'rush_yds': stats.get('rush_yards', 0),
                'rush_tds': stats.get('rush_tds', 0),
                'fantasy_pts': fantasy_points.get(player_id, 0)
            }
        elif stats.get('position') == 'RB':
            web_stats['stats'] = {
                'rush_att': stats.get('rush_attempts', 0),
                'rush_yds': stats.get('rush_yards', 0),
                'rush_tds': stats.get('rush_tds', 0),
                'rec': stats.get('receptions', 0),
                'rec_yds': stats.get('receiving_yards', 0),
                'rec_tds': stats.get('receiving_tds', 0),
                'fumbles': stats.get('fumbles', 0),
                'fantasy_pts': fantasy_points.get(player_id, 0)
            }
        elif stats.get('position') in ['WR', 'TE']:
            web_stats['stats'] = {
                'targets': stats.get('targets', 0),
                'rec': stats.get('receptions', 0),
                'rec_yds': stats.get('receiving_yards', 0),
                'rec_tds': stats.get('receiving_tds', 0),
                'rush_att': stats.get('rush_attempts', 0),
                'rush_yds': stats.get('rush_yards', 0),
                'rush_tds': stats.get('rush_tds', 0),
                'fantasy_pts': fantasy_points.get(player_id, 0)
            }
        
        web_player_stats.append(web_stats)
    
    # Add web-formatted player stats to results
    results['player_stats_web'] = web_player_stats
    
    return results

    def initialize_player_stats(self, players):
        """
        Initialize statistics for all players
        
        Args:
            players (list): List of player dictionaries
            
        Returns:
            dict: Dictionary of player statistics by player ID
        """
        player_stats = {}
        
        for player in players:
            player_id = player["id"]
            position = player["position"]
            
            # Base stats for all players
            stats = {
                "player_id": player_id,
                "player_name": player["name"],
                "team_id": player["team_id"],
                "position": position,
            }
            
            # Position-specific stats
            if position == "QB":
                stats.update({
                    "pass_attempts": 0,
                    "pass_completions": 0,
                    "pass_yards": 0,
                    "pass_tds": 0,
                    "interceptions": 0,
                    "rush_attempts": 0,
                    "rush_yards": 0,
                    "rush_tds": 0
                })
            elif position == "RB":
                stats.update({
                    "rush_attempts": 0,
                    "rush_yards": 0,
                    "rush_tds": 0,
                    "receptions": 0,
                    "receiving_yards": 0,
                    "receiving_tds": 0,
                    "fumbles": 0
                })
            elif position in ["WR", "TE"]:
                stats.update({
                    "targets": 0,
                    "receptions": 0,
                    "receiving_yards": 0,
                    "receiving_tds": 0,
                    "rush_attempts": 0,
                    "rush_yards": 0,
                    "rush_tds": 0
                })
            
            player_stats[player_id] = stats
        
        return player_stats
    
    def update_player_stats(self, play_result, offensive_players, player_stats):
        """
        Update player statistics based on a play result
        
        Args:
            play_result (dict): Play result
            offensive_players (list): List of offensive players
            player_stats (dict): Current player statistics
            
        Returns:
            dict: Updated play result with player IDs
        """
        play_type = play_result.get('play_type')
        yards_gained = play_result.get('yards_gained', 0)
        
        # Only update for regular plays (not punts, field goals)
        if play_type in ['pass', 'run']:
            # Get players by position
            qb = next((p for p in offensive_players if p['position'] == 'QB'), None)
            rbs = [p for p in offensive_players if p['position'] == 'RB']
            wrs = [p for p in offensive_players if p['position'] == 'WR']
            tes = [p for p in offensive_players if p['position'] == 'TE']
            
            # Choose players for this play
            if play_type == 'pass':
                passer = qb
                receivers = wrs + tes
                
                # Choose a random receiver with bias toward WRs
                receiver_weights = [2 if p['position'] == 'WR' else 1 for p in receivers]
                receiver = random.choices(receivers, weights=receiver_weights, k=1)[0] if receivers else None
                
                if passer and receiver and passer['id'] in player_stats and receiver['id'] in player_stats:
                    # Determine if pass is complete (70% completion rate)
                    is_complete = yards_gained > 0
                    
                    # Update passer stats
                    passer_stats = player_stats[passer['id']]
                    passer_stats['pass_attempts'] += 1
                    
                    if is_complete:
                        passer_stats['pass_completions'] += 1
                        passer_stats['pass_yards'] += yards_gained
                        
                        # Update receiver stats
                        receiver_stats = player_stats[receiver['id']]
                        receiver_stats['targets'] += 1
                        receiver_stats['receptions'] += 1
                        receiver_stats['receiving_yards'] += yards_gained
                        
                        # Touchdown
                        if play_result.get('touchdown', False):
                            passer_stats['pass_tds'] += 1
                            receiver_stats['receiving_tds'] += 1
                    else:
                        # Incomplete pass or interception
                        receiver_stats = player_stats[receiver['id']]
                        receiver_stats['targets'] += 1
                    
                    # Update player IDs in play result
                    play_result['passer_id'] = passer['id']
                    play_result['receiver_id'] = receiver['id']
                    
                    # Check for interception
                    if play_result.get('turnover_type') == 'interception':
                        passer_stats['interceptions'] += 1
            
            elif play_type == 'run':
                # Choose a random RB (80% chance) or QB (20% chance)
                if rbs and random.random() < 0.8:
                    runner = random.choice(rbs)
                else:
                    runner = qb
                
                if runner and runner['id'] in player_stats:
                    # Update runner stats
                    runner_stats = player_stats[runner['id']]
                    runner_stats['rush_attempts'] = runner_stats.get('rush_attempts', 0) + 1
                    runner_stats['rush_yards'] = runner_stats.get('rush_yards', 0) + yards_gained
                    
                    # Touchdown
                    if play_result.get('touchdown', False):
                        runner_stats['rush_tds'] = runner_stats.get('rush_tds', 0) + 1
                    
                    # Fumble
                    if play_result.get('turnover_type') == 'fumble':
                        runner_stats['fumbles'] = runner_stats.get('fumbles', 0) + 1
                    
                    # Update player ID in play result
                    play_result['runner_id'] = runner['id']
        
        return play_result
    
    def calculate_fantasy_points_from_stats(self, player_stats):
        """
        Calculate fantasy points for all players based on their statistics
        
        Args:
            player_stats (dict): Player statistics
            
        Returns:
            dict: Fantasy points by player ID
        """
        fantasy_points = {}
        
        for player_id, stats in player_stats.items():
            position = stats.get('position', '')
            points = 0
            
            # Common scoring rules
            # Passing: 1 pt per 25 yards, 4 pts per TD, -2 pts per INT
            # Rushing: 1 pt per 10 yards, 6 pts per TD
            # Receiving: 1 pt per 10 yards, 6 pts per TD, 0.5 pts per reception (PPR)
            
            if position == 'QB':
                points += stats.get('pass_yards', 0) / 25.0
                points += stats.get('pass_tds', 0) * 4
                points -= stats.get('interceptions', 0) * 2
                points += stats.get('rush_yards', 0) / 10.0
                points += stats.get('rush_tds', 0) * 6
            
            elif position == 'RB' or position == 'WR' or position == 'TE':
                points += stats.get('rush_yards', 0) / 10.0
                points += stats.get('rush_tds', 0) * 6
                points += stats.get('receiving_yards', 0) / 10.0
                points += stats.get('receiving_tds', 0) * 6
                points += stats.get('receptions', 0) * 0.5  # PPR format
                points -= stats.get('fumbles', 0) * 2
            
            fantasy_points[player_id] = round(points, 2)
        
        return fantasy_points
    
    def calculate_fantasy_points_for_player(self, stats):
        """
        Calculate fantasy points for a single player based on their statistics
        
        Args:
            stats (dict): Player statistics
            
        Returns:
            float: Fantasy points
        """
        position = stats.get('position', '')
        points = 0
        
        # Common scoring rules
        # Passing: 1 pt per 25 yards, 4 pts per TD, -2 pts per INT
        # Rushing: 1 pt per 10 yards, 6 pts per TD
        # Receiving: 1 pt per 10 yards, 6 pts per TD, 0.5 pts per reception (PPR)
        
        if position == 'QB':
            points += stats.get('pass_yards', 0) / 25.0
            points += stats.get('pass_tds', 0) * 4
            points -= stats.get('interceptions', 0) * 2
            points += stats.get('rush_yards', 0) / 10.0
            points += stats.get('rush_tds', 0) * 6
        
        elif position == 'RB' or position == 'WR' or position == 'TE':
            points += stats.get('rush_yards', 0) / 10.0
            points += stats.get('rush_tds', 0) * 6
            points += stats.get('receiving_yards', 0) / 10.0
            points += stats.get('receiving_tds', 0) * 6
            points += stats.get('receptions', 0) * 0.5  # PPR format
            points -= stats.get('fumbles', 0) * 2
        
        return round(points, 2)
    
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
        all_player_stats = {}
        
        for i in range(num_games):
            game_results = self.simulate_game(home_team, away_team, verbose=verbose)
            all_results.append(game_results)
            
            # Aggregate player stats across games
            for player_id, stats in game_results.get('player_stats', {}).items():
                if player_id not in all_player_stats:
                    # Initialize with a copy of the first game's stats
                    all_player_stats[player_id] = stats.copy()
                    # Add tracking for min/max/games
                    all_player_stats[player_id]['games'] = 1
                    all_player_stats[player_id]['stats_by_game'] = [stats]
                else:
                    # Update cumulative stats
                    all_player_stats[player_id]['games'] += 1
                    all_player_stats[player_id]['stats_by_game'].append(stats)
                    
                    # Update numeric stats
                    for key, value in stats.items():
                        if isinstance(value, (int, float)) and key not in ['player_id', 'games']:
                            all_player_stats[player_id][key] = all_player_stats[player_id].get(key, 0) + value
        
        # Compile summary statistics
        home_wins = sum(1 for r in all_results if r['home_team']['score'] > r['away_team']['score'])
        away_wins = sum(1 for r in all_results if r['away_team']['score'] > r['home_team']['score'])
        ties = sum(1 for r in all_results if r['home_team']['score'] == r['away_team']['score'])
        
        avg_home_score = sum(r['home_team']['score'] for r in all_results) / num_games
        avg_away_score = sum(r['away_team']['score'] for r in all_results) / num_games
        
        # Calculate statistical analysis for player stats
        player_projections = self.analyze_player_stats(all_player_stats, num_games)
        
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
            'ties': ties,
            'player_projections': player_projections
        }
        
        return {
            'summary': summary,
            'games': all_results
        }
    
    def analyze_player_stats(self, all_player_stats, num_games):
        """
        Analyze player statistics across multiple games
        
        Args:
            all_player_stats (dict): Player statistics from all games
            num_games (int): Number of games simulated
            
        Returns:
            dict: Player projections with statistical analysis
        """
        projections = {}
        
        for player_id, stats in all_player_stats.items():
            if 'stats_by_game' not in stats:
                continue
                
            stats_by_game = stats['stats_by_game']
            position = stats.get('position', '')
            
            # Initialize player projection with basic info
            player_proj = {
                'player_id': player_id,
                'player_name': stats.get('player_name', ''),
                'team_id': stats.get('team_id', ''),
                'position': position,
                'games_played': len(stats_by_game)
            }
            
            # Position-specific stat analysis
            stat_keys = []
            
            if position == 'QB':
                stat_keys = ['pass_attempts', 'pass_completions', 'pass_yards', 'pass_tds', 
                            'interceptions', 'rush_attempts', 'rush_yards', 'rush_tds']
            elif position == 'RB':
                stat_keys = ['rush_attempts', 'rush_yards', 'rush_tds', 
                            'receptions', 'receiving_yards', 'receiving_tds', 'fumbles']
            elif position in ['WR', 'TE']:
                stat_keys = ['targets', 'receptions', 'receiving_yards', 'receiving_tds',
                            'rush_attempts', 'rush_yards', 'rush_tds']
            
            # Calculate statistics for each key
            for key in stat_keys:
                values = [game_stats.get(key, 0) for game_stats in stats_by_game]
                
                if not values:
                    continue
                
                # Calculate statistics
                total = sum(values)
                avg = total / len(values) if values else 0
                min_val = min(values) if values else 0
                max_val = max(values) if values else 0
                
                # Calculate standard deviation
                variance = sum((x - avg) ** 2 for x in values) / len(values) if len(values) > 1 else 0
                std_dev = math.sqrt(variance)
                
                # Store analysis in projection
                player_proj[f'{key}_total'] = total
                player_proj[f'{key}_avg'] = avg
                player_proj[f'{key}_min'] = min_val
                player_proj[f'{key}_max'] = max_val
                player_proj[f'{key}_std_dev'] = std_dev
            
            # Calculate fantasy points
            fantasy_points = [self.calculate_fantasy_points_for_player(game_stats) for game_stats in stats_by_game]
            
            if fantasy_points:
                player_proj['fantasy_points_total'] = sum(fantasy_points)
                player_proj['fantasy_points_avg'] = sum(fantasy_points) / len(fantasy_points)
                player_proj['fantasy_points_min'] = min(fantasy_points)
                player_proj['fantasy_points_max'] = max(fantasy_points)
                
                # Standard deviation for fantasy points
                fp_avg = player_proj['fantasy_points_avg']
                fp_variance = sum((x - fp_avg) ** 2 for x in fantasy_points) / len(fantasy_points) if len(fantasy_points) > 1 else 0
                player_proj['fantasy_points_std_dev'] = math.sqrt(fp_variance)
            
            projections[player_id] = player_proj
        
        return projections
    
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
        # Check if game results already have fantasy points calculated
        if 'fantasy_points' in game_results and game_results['fantasy_points']:
            return game_results['fantasy_points']
            
        # Check if game results have player stats
        if 'player_stats' in game_results and game_results['player_stats']:
            return self.calculate_fantasy_points_from_stats(game_results['player_stats'])
        
        # Fall back to simplified calculation if no detailed stats
        fantasy_points = {}
        
        # Get players from both teams
        home_team_id = game_results.get('home_team', {}).get('id')
        away_team_id = game_results.get('away_team', {}).get('id')
        
        if home_team_id:
            home_players = self.get_players_for_team(home_team_id)
            for player in home_players:
                # Generate random fantasy points based on position
                position = player['position']
                player_id = player['id']
                
                if position == 'QB':
                    points = random.uniform(10, 30)
                elif position == 'RB':
                    points = random.uniform(5, 25)
                elif position == 'WR':
                    points = random.uniform(5, 20)
                elif position == 'TE':
                    points = random.uniform(3, 15)
                else:
                    points = random.uniform(1, 10)
                    
                fantasy_points[player_id] = round(points, 2)
        
        if away_team_id:
            away_players = self.get_players_for_team(away_team_id)
            for player in away_players:
                # Generate random fantasy points based on position
                position = player['position']
                player_id = player['id']
                
                if position == 'QB':
                    points = random.uniform(10, 30)
                elif position == 'RB':
                    points = random.uniform(5, 25)
                elif position == 'WR':
                    points = random.uniform(5, 20)
                elif position == 'TE':
                    points = random.uniform(3, 15)
                else:
                    points = random.uniform(1, 10)
                    
                fantasy_points[player_id] = round(points, 2)
        
        return fantasy_points
    
    def generate_fantasy_projections(self, num_simulations=100):
        """
        Generate fantasy football projections based on simulations
        
        Args:
            num_simulations (int): Number of simulations to run
            
        Returns:
            dict: Fantasy projections
        """
        # Get all teams
        team_ids = list(self.teams.keys())
        
        # Create all possible matchups
        matchups = []
        for i, home_id in enumerate(team_ids):
            for away_id in team_ids[i+1:]:
                matchups.append((home_id, away_id))
        
        # Select a subset of matchups to simulate
        num_matchups = min(len(matchups), 5)  # Limit to 5 matchups for efficiency
        selected_matchups = random.sample(matchups, num_matchups)
        
        # Simulate each matchup multiple times
        all_player_stats = {}
        
        for home_id, away_id in selected_matchups:
            home_team = self.get_team(home_id)
            away_team = self.get_team(away_id)
            
            # Simulate fewer games per matchup to stay within limits
            sims_per_matchup = max(1, num_simulations // num_matchups)
            results = self.simulate_multiple_games(home_team, away_team, sims_per_matchup)
            
            # Extract player projections
            if 'summary' in results and 'player_projections' in results['summary']:
                for player_id, proj in results['summary']['player_projections'].items():
                    all_player_stats[player_id] = proj
        
        # Format projections for the web app
        players = []
        for player_id, stats in all_player_stats.items():
            players.append({
                "id": player_id,
                "name": stats.get("player_name", "Unknown"),
                "position": stats.get("position", ""),
                "team": stats.get("team_id", ""),
                "points": stats.get("fantasy_points_avg", 0),
                "min": stats.get("fantasy_points_min", 0),
                "max": stats.get("fantasy_points_max", 0),
                "std_dev": stats.get("fantasy_points_std_dev", 0),
                "games": stats.get("games_played", 0)
            })
        
        # Sort by points
        players.sort(key=lambda x: x["points"], reverse=True)
        
        return {
            "players": players,
            "simulations": num_simulations
        }
    
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
            f.write("id,name,position,team,points,min,max,std_dev,games\n")
            
            for player in projections.get('players', []):
                f.write(f"{player['id']},{player['name']},{player['position']},{player['team']},"
                        f"{player['points']:.2f},{player['min']:.2f},{player['max']:.2f},"
                        f"{player.get('std_dev', 0):.2f},{player.get('games', 0)}\n")
        
        return filepath
    
def run_multiple_simulations(self, home_team, away_team, num_sims=1, verbose=False):
    """
    Alias for simulate_multiple_games to maintain compatibility with web app
    """
    return self.simulate_multiple_games(home_team, away_team, num_games=num_sims, verbose=verbose)    