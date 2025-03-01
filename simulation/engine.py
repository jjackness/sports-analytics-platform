# simulation/engine.py
from typing import Dict, List, Optional, Tuple
import random
import json
import os
import pandas as pd
from datetime import datetime
from models.game import Game, GameConditions
from models.team import Team
from models.player import Player, PlayerAttributes, PlayerStats

class SimulationEngine:
    """
    Manages the simulation of multiple games and collects/analyzes the results.
    This is the central component for running simulations.
    """
    def __init__(self, teams_data: Dict[str, Team] = None, output_dir: str = "simulation_results"):
        self.teams = teams_data or {}
        self.output_dir = output_dir
        self.simulation_history = []
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def load_team_data(self, file_path: str):
        """Load team data from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                teams_data = json.load(f)
                
            for team_id, team_info in teams_data.items():
                # Create team
                team = Team(
                    id=team_id,
                    name=team_info.get('name', ''),
                    abbreviation=team_info.get('abbreviation', ''),
                    city=team_info.get('city', '')
                )
                
                # Add attributes if present
                if 'attributes' in team_info:
                    attrs = team_info['attributes']
                    team.attributes.offensive_scheme = attrs.get('offensive_scheme', 'balanced')
                    team.attributes.defensive_scheme = attrs.get('defensive_scheme', 'balanced')
                    team.attributes.offensive_line_rating = attrs.get('offensive_line_rating', 50)
                    # Add other attributes...
                
                # Load roster
                if 'roster' in team_info:
                    for player_info in team_info['roster']:
                        # Create player
                        player = Player(
                            id=player_info.get('id', f"player_{len(team.roster)}"),
                            name=player_info.get('name', ''),
                            team=team_id,
                            position=player_info.get('position', '')
                        )
                        
                        # Add attributes if present
                        if 'attributes' in player_info:
                            attrs = player_info['attributes']
                            # Set player attributes based on position
                            if player.position == "QB":
                                player.attributes.throwing_power = attrs.get('throwing_power', 50)
                                player.attributes.throwing_accuracy = attrs.get('throwing_accuracy', 50)
                                # Other QB attributes...
                            elif player.position in ["RB", "WR"]:
                                player.attributes.speed = attrs.get('speed', 50)
                                player.attributes.catching = attrs.get('catching', 50)
                                # Other skill position attributes...
                        
                        # Add to team
                        team.add_player(player)
                
                # Add team to engine
                self.teams[team_id] = team
                
            return True
        except Exception as e:
            print(f"Error loading team data: {e}")
            return False
    
    def load_player_data(self, file_path: str):
        """Load player data from a CSV file."""
        try:
            players_df = pd.read_csv(file_path)
            
            for _, row in players_df.iterrows():
                team_id = row.get('team_id')
                
                # Skip if team doesn't exist
                if team_id not in self.teams:
                    continue
                
                # Create player
                player = Player(
                    id=str(row.get('player_id')),
                    name=row.get('name', ''),
                    team=team_id,
                    position=row.get('position', ''),
                    age=row.get('age', 25)
                )
                
                # Set attributes based on available data
                # This would be expanded based on the actual data format
                player.attributes.speed = row.get('speed', 50)
                player.attributes.strength = row.get('strength', 50)
                player.attributes.agility = row.get('agility', 50)
                
                # Position-specific attributes
                if player.position == "QB":
                    player.attributes.throwing_power = row.get('throw_power', 50)
                    player.attributes.throwing_accuracy = row.get('throw_accuracy', 50)
                    player.attributes.decision_making = row.get('decision_making', 50)
                elif player.position in ["RB", "WR", "TE"]:
                    player.attributes.catching = row.get('catching', 50)
                    player.attributes.elusiveness = row.get('elusiveness', 50)
                    player.attributes.route_running = row.get('route_running', 50)
                    player.attributes.breaking_tackles = row.get('break_tackle', 50)
                
                # Add player to team
                self.teams[team_id].add_player(player)
            
            return True
        except Exception as e:
            print(f"Error loading player data: {e}")
            return False
    
    def create_default_teams(self, num_teams: int = 2):
        """Create default teams for testing."""
        positions = ["QB", "RB", "WR", "TE", "OL", "DL", "LB", "CB", "S", "K", "P"]
        
        for i in range(num_teams):
            team_id = f"team_{i+1}"
            team = Team(
                id=team_id,
                name=f"Team {i+1}",
                abbreviation=f"T{i+1}",
                city=f"City {i+1}"
            )
            
            # Set random team attributes
            team.attributes.offensive_line_rating = random.randint(40, 80)
            team.attributes.defensive_line_rating = random.randint(40, 80)
            team.attributes.secondary_rating = random.randint(40, 80)
            team.attributes.special_teams_rating = random.randint(40, 80)
            team.attributes.pass_tendency = random.uniform(0.45, 0.65)  # Modern NFL tends more toward passing
            
            # Create players for each position
            for pos in positions:
                # Create 1-3 players per position
                num_players = 3 if pos in ["WR", "OL", "DL", "LB", "CB"] else 1
                
                for j in range(num_players):
                    player_id = f"{team_id}_{pos}_{j+1}"
                    player = Player(
                        id=player_id,
                        name=f"Player {player_id}",
                        team=team_id,
                        position=pos
                    )
                    
                    # Set random attributes based on position
                    base_rating = random.randint(50, 80)
                    player.attributes.speed = base_rating + random.randint(-10, 10)
                    player.attributes.strength = base_rating + random.randint(-10, 10)
                    player.attributes.agility = base_rating + random.randint(-10, 10)
                    player.attributes.awareness = base_rating + random.randint(-10, 10)
                    
                    if pos == "QB":
                        player.attributes.throwing_power = base_rating + random.randint(-5, 15)
                        player.attributes.throwing_accuracy = base_rating + random.randint(-5, 15)
                        player.attributes.decision_making = base_rating + random.randint(-10, 10)
                    elif pos in ["RB", "WR", "TE"]:
                        player.attributes.catching = base_rating + random.randint(-10, 15)
                        player.attributes.elusiveness = base_rating + random.randint(-10, 15)
                        player.attributes.route_running = base_rating + random.randint(-10, 15)
                        player.attributes.breaking_tackles = base_rating + random.randint(-10, 15)
                    elif pos in ["DL", "LB", "CB", "S"]:
                        player.attributes.tackling = base_rating + random.randint(-5, 15)
                        player.attributes.coverage = base_rating + random.randint(-10, 15)
                        player.attributes.block_shedding = base_rating + random.randint(-10, 15)
                    
                    # Add player to team
                    team.add_player(player)
            
            # Add team to engine
            self.teams[team_id] = team
    
    def simulate_game(self, home_team_id: str, away_team_id: str, 
                      conditions: Optional[GameConditions] = None,
                      verbose: bool = False) -> Dict:
        """Simulate a single game between two teams."""
        # Validate teams exist
        if home_team_id not in self.teams or away_team_id not in self.teams:
            raise ValueError(f"Team not found: {home_team_id if home_team_id not in self.teams else away_team_id}")
        
        # Get teams
        home_team = self.teams[home_team_id]
        away_team = self.teams[away_team_id]
        
        # Create game with default conditions if none provided
        game = Game(
            home_team=home_team,
            away_team=away_team,
            conditions=conditions or GameConditions(),
            verbose=verbose
        )
        
        # Simulate game
        result = game.simulate_game()
        
        # Add to simulation history
        self.simulation_history.append(result)
        
        return result
    
    def simulate_season(self, num_games_per_team: int = 16,
                       randomize_conditions: bool = True,
                       verbose: bool = False) -> Dict:
        """
        Generate a balanced schedule and simulate a full season 
        where each team plays the specified number of games.
        """
        # Generate a balanced schedule
        schedule = []
        team_ids = list(self.teams.keys())
        
        # Track games played per team
        games_per_team = {team_id: 0 for team_id in team_ids}
        
        # Keep scheduling until all teams have played required games
        while min(games_per_team.values()) < num_games_per_team:
            # Find teams that haven't played max games yet
            eligible_teams = [t for t, g in games_per_team.items() if g < num_games_per_team]
            if len(eligible_teams) < 2:
                break
                
            # Randomly select two teams
            home, away = random.sample(eligible_teams, 2)
            
            # Check if these teams would exceed their game limit
            if games_per_team[home] >= num_games_per_team or games_per_team[away] >= num_games_per_team:
                continue
                
            # Add game to schedule
            schedule.append((home, away))
            games_per_team[home] += 1
            games_per_team[away] += 1
        
        if verbose:
            print(f"Generated schedule with {len(schedule)} games")
            for team_id, games in games_per_team.items():
                print(f"  {self.teams[team_id].name}: {games} games")
        
        return self.simulate_season_with_schedule(schedule, randomize_conditions, verbose)
        
    def simulate_season_with_schedule(self, schedule: List[Tuple[str, str]],
                                     randomize_conditions: bool = True,
                                     verbose: bool = False) -> Dict:
        """
        Simulate a full season based on provided schedule.
        Each entry in schedule should be (home_team_id, away_team_id).
        """
        season_results = []
        
        for i, (home_id, away_id) in enumerate(schedule):
            # Create game conditions (randomized if enabled)
            conditions = GameConditions()
            if randomize_conditions:
                # Randomize weather, temperature, etc.
                weathers = ["clear", "rain", "snow", "wind"]
                conditions.weather = random.choice(weathers)
                conditions.temperature = random.randint(20, 90)
                conditions.wind_speed = random.randint(0, 20)
                conditions.week = i // 16 + 1  # Assuming 16 games per week
            
            # Simulate game
            try:
                result = self.simulate_game(home_id, away_id, conditions, verbose)
                season_results.append(result)
                
                if verbose:
                    print(f"Game {i+1}: {result['home_team']} {result['home_score']} - {result['away_team']} {result['away_score']}")
            except ValueError as e:
                print(f"Error simulating game: {e}")
        
        # Compile season stats
        team_records = {}
        for team_id in self.teams:
            team = self.teams[team_id]
            team_records[team_id] = {
                "team": team.name,
                "wins": team.stats.wins,
                "losses": team.stats.losses,
                "ties": team.stats.ties,
                "pct": round((team.stats.wins + 0.5 * team.stats.ties) / 
                       max(1, (team.stats.wins + team.stats.losses + team.stats.ties)), 3),
                "total_yards": team.stats.total_yards,
                "passing_yards": team.stats.passing_yards,
                "rushing_yards": team.stats.rushing_yards
            }
        
        # Sort by win percentage
        sorted_records = sorted(team_records.values(), 
                               key=lambda x: x['pct'], 
                               reverse=True)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"{self.output_dir}/season_results_{timestamp}.json", 'w') as f:
            json.dump({
                "games": season_results,
                "standings": sorted_records
            }, f, indent=4)
        
        return {
            "games": len(season_results),
            "standings": sorted_records
        }
    
    def run_multiple_simulations(self, home_team_id: str, away_team_id: str, 
                                num_sims: int = 100) -> Dict:
        """
        Run multiple simulations of the same matchup to generate statistics.
        This is useful for fantasy projections.
        """
        results = []
        home_wins = 0
        away_wins = 0
        ties = 0
        
        # Run simulations
        for i in range(num_sims):
            result = self.simulate_game(home_team_id, away_team_id)
            results.append(result)
            
            if result['home_score'] > result['away_score']:
                home_wins += 1
            elif result['away_score'] > result['home_score']:
                away_wins += 1
            else:
                ties += 1
        
        # Calculate player stats across simulations
        player_stats = {}
        
        # Process home team players
        home_team = self.teams[home_team_id]
        for player_id, player in home_team.roster.items():
            if player.position in ["QB", "RB", "WR", "TE"]:
                # Calculate average fantasy points
                avg_points = player.get_average_fantasy_points()
                
                # Get detailed stats from historical records
                total_stats = PlayerStats()
                for game_stats in player.historical_stats[-num_sims:]:
                    for attr in vars(game_stats):
                        if not attr.startswith('_'):
                            current = getattr(total_stats, attr, 0)
                            game_value = getattr(game_stats, attr, 0)
                            setattr(total_stats, attr, current + game_value)
                
                # Calculate averages
                avg_stats = {attr: getattr(total_stats, attr) / num_sims 
                            for attr in vars(total_stats) 
                            if not attr.startswith('_')}
                
                player_stats[player_id] = {
                    "name": player.name,
                    "team": home_team.name,
                    "position": player.position,
                    "fantasy_points_avg": avg_points,
                    "stats": avg_stats
                }
        
        # Process away team players
        away_team = self.teams[away_team_id]
        for player_id, player in away_team.roster.items():
            if player.position in ["QB", "RB", "WR", "TE"]:
                # Calculate average fantasy points
                avg_points = player.get_average_fantasy_points()
                
                # Get detailed stats from historical records
                total_stats = PlayerStats()
                for game_stats in player.historical_stats[-num_sims:]:
                    for attr in vars(game_stats):
                        if not attr.startswith('_'):
                            current = getattr(total_stats, attr, 0)
                            game_value = getattr(game_stats, attr, 0)
                            setattr(total_stats, attr, current + game_value)
                
                # Calculate averages
                avg_stats = {attr: getattr(total_stats, attr) / num_sims 
                            for attr in vars(total_stats) 
                            if not attr.startswith('_')}
                
                player_stats[player_id] = {
                    "name": player.name,
                    "team": away_team.name,
                    "position": player.position,
                    "fantasy_points_avg": avg_points,
                    "stats": avg_stats
                }
        
        # Sort players by fantasy points
        sorted_players = sorted(player_stats.values(), 
                               key=lambda x: x['fantasy_points_avg'], 
                               reverse=True)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"{self.output_dir}/simulation_batch_{timestamp}.json", 'w') as f:
            json.dump({
                "matchup": f"{home_team.name} vs {away_team.name}",
                "simulations": num_sims,
                "home_win_pct": home_wins / num_sims,
                "away_win_pct": away_wins / num_sims,
                "tie_pct": ties / num_sims,
                "player_projections": sorted_players
            }, f, indent=4)
        
        return {
            "matchup": f"{home_team.name} vs {away_team.name}",
            "simulations": num_sims,
            "home_win_pct": home_wins / num_sims,
            "away_win_pct": away_wins / num_sims,
            "tie_pct": ties / num_sims,
            "player_projections": sorted_players[:10]  # Top 10 players
        }
    
    def export_fantasy_projections(self, output_file: str = None):
        """
        Export fantasy projections for all players based on simulation history.
        """
        if not self.simulation_history:
            print("No simulations have been run yet.")
            return
        
        player_projections = []
        
        # Process all teams
        for team_id, team in self.teams.items():
            for player_id, player in team.roster.items():
                if player.position in ["QB", "RB", "WR", "TE"]:
                    # Calculate average fantasy points
                    if player.fantasy_points_history:
                        avg_points = sum(player.fantasy_points_history) / len(player.fantasy_points_history)
                        
                        # Calculate consistency (standard deviation)
                        if len(player.fantasy_points_history) > 1:
                            mean = avg_points
                            variance = sum((x - mean) ** 2 for x in player.fantasy_points_history) / len(player.fantasy_points_history)
                            std_dev = variance ** 0.5
                            consistency = 1 - (std_dev / (mean if mean > 0 else 1))  # Normalize
                        else:
                            consistency = 0
                        
                        player_projections.append({
                            "player_id": player_id,
                            "name": player.name,
                            "team": team.name,
                            "position": player.position,
                            "fantasy_points_avg": avg_points,
                            "consistency": consistency,
                            "games_played": len(player.fantasy_points_history)
                        })
        
        # Sort by fantasy points
        sorted_players = sorted(player_projections, 
                               key=lambda x: x['fantasy_points_avg'], 
                               reverse=True)
        
        # Save to file if specified
        if output_file:
            # Make sure the directory exists
            import os
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Add timestamp to filename to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename, ext = os.path.splitext(output_file)
            safe_output_file = f"{filename}_{timestamp}{ext}"
            
            try:
                # Create DataFrame and save to CSV
                df = pd.DataFrame(sorted_players)
                df.to_csv(safe_output_file, index=False)
                print(f"Fantasy projections exported to {safe_output_file}")
            except Exception as e:
                print(f"Error saving projections: {e}")
                print(f"Trying alternative location...")
                # Try saving to current directory as fallback
                alt_file = f"fantasy_projections_{timestamp}.csv"
                try:
                    df.to_csv(alt_file, index=False)
                    print(f"Fantasy projections exported to {alt_file}")
                except Exception as e2:
                    print(f"Could not save file: {e2}")
        
        return sorted_players