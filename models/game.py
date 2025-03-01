# models/game.py
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from .team import Team
from .player import Player

@dataclass
class GameConditions:
    """Environment conditions that affect game simulation."""
    weather: str = "clear"  # clear, rain, snow, wind
    temperature: int = 70  # Fahrenheit
    wind_speed: int = 0  # mph
    field_type: str = "grass"  # grass, turf
    stadium_type: str = "outdoor"  # outdoor, dome, retractable
    altitude: int = 0  # feet above sea level
    
    # Time factors
    time_of_day: str = "afternoon"  # morning, afternoon, night
    is_primetime: bool = False
    
    # Game importance
    is_playoffs: bool = False
    is_divisional_game: bool = False
    week: int = 1
    
    def get_weather_factors(self) -> Dict[str, float]:
        """Return performance modifiers based on weather conditions."""
        factors = {
            "passing_modifier": 1.0,
            "rushing_modifier": 1.0,
            "kicking_modifier": 1.0
        }
        
        # Apply weather effects
        if self.weather == "rain":
            factors["passing_modifier"] *= 0.9
            factors["rushing_modifier"] *= 0.95
            factors["kicking_modifier"] *= 0.85
        elif self.weather == "snow":
            factors["passing_modifier"] *= 0.8
            factors["rushing_modifier"] *= 0.85
            factors["kicking_modifier"] *= 0.7
        
        # Apply wind effects
        if self.wind_speed > 15:
            wind_factor = max(0.7, 1 - (self.wind_speed - 15) / 50)
            factors["passing_modifier"] *= wind_factor
            factors["kicking_modifier"] *= wind_factor
        
        # Apply temperature effects for extreme cold
        if self.temperature < 32:
            cold_factor = max(0.8, 1 - (32 - self.temperature) / 50)
            factors["passing_modifier"] *= cold_factor
            
        return factors

@dataclass
class GameClock:
    """Tracks game time and provides time management methods."""
    quarter: int = 1
    minutes: int = 15
    seconds: int = 0
    is_running: bool = False
    
    # Game configuration
    quarter_length: int = 15  # Minutes per quarter
    
    def advance(self, seconds_elapsed: int):
        """Advance the game clock by specified seconds."""
        if not self.is_running:
            return
            
        total_seconds = self.minutes * 60 + self.seconds - seconds_elapsed
        
        if total_seconds <= 0:
            # End of quarter
            self.quarter += 1
            remaining_seconds = abs(total_seconds)
            
            if self.quarter <= 4:
                self.minutes = self.quarter_length
                self.seconds = 0
                
                # Apply remaining seconds from play that went over
                if remaining_seconds > 0:
                    self.advance(remaining_seconds)
            else:
                # Game over
                self.minutes = 0
                self.seconds = 0
                self.is_running = False
        else:
            # Update minutes and seconds
            self.minutes = total_seconds // 60
            self.seconds = total_seconds % 60
    
    def start(self):
        """Start the clock."""
        self.is_running = True
    
    def stop(self):
        """Stop the clock."""
        self.is_running = False
    
    def reset_for_quarter(self):
        """Reset clock for a new quarter."""
        self.minutes = self.quarter_length
        self.seconds = 0
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.quarter > 4
    
    def time_remaining(self) -> int:
        """Return total seconds remaining in the game."""
        quarters_left = 4 - self.quarter + 1
        return (quarters_left - 1) * self.quarter_length * 60 + self.minutes * 60 + self.seconds
    
    def __str__(self) -> str:
        """String representation of the game clock."""
        return f"Q{self.quarter} {self.minutes}:{self.seconds:02d}"

@dataclass
class GameState:
    """Current state of the game used in simulation."""
    home_score: int = 0
    away_score: int = 0
    
    possession: Optional[str] = None  # ID of team with possession
    down: int = 1
    distance: int = 10
    field_position: int = 20  # Yards from own goal line
    
    # Game situation tracking
    is_redzone: bool = False
    is_two_minute_warning: bool = False
    last_score_team: Optional[str] = None
    home_timeouts: int = 3
    away_timeouts: int = 3
    
    # Play history for analysis
    play_history: List[Dict] = field(default_factory=list)
    
    def update_field_position(self, yards_gained: int):
        """Update field position based on yards gained/lost."""
        self.field_position += yards_gained
        
        # Check for change of possession if past 100
        if self.field_position > 100:
            self.field_position = 100  # At opponent's goal line
        
        # Update redzone status
        self.is_redzone = (self.field_position >= 80)
    
    def update_down_and_distance(self, yards_gained: int):
        """Update down and distance based on play result."""
        # First check if it's a first down
        if yards_gained >= self.distance:
            self.down = 1
            self.distance = 10
            
            # Adjust if near goal line
            if self.field_position > 90:
                self.distance = 100 - self.field_position
        else:
            # Didn't get first down, advance to next down
            self.down += 1
            self.distance -= yards_gained
            
            # Adjust if we gained negative yards
            if self.distance > 10 and self.field_position < 90:
                self.distance = 10
    
    def change_possession(self):
        """Change possession between teams."""
        # Flip field position to other side of field
        self.field_position = 100 - self.field_position
        
        # Reset downs
        self.down = 1
        self.distance = 10
        
        # Minimum 20 yards if backed up
        if self.field_position < 20:
            self.field_position = 20
        
        # Switch possession team
        self.possession = 'away' if self.possession == 'home' else 'home'
    
    def add_play_to_history(self, play_data: Dict):
        """Add a play to the history for later analysis."""
        self.play_history.append(play_data)
    
    def get_score_difference(self) -> int:
        """Get current score differential from possession team perspective."""
        if self.possession == 'home':
            return self.home_score - self.away_score
        else:
            return self.away_score - self.home_score
    
    def get_timeouts_left(self) -> int:
        """Get timeouts left for possession team."""
        return self.home_timeouts if self.possession == 'home' else self.away_timeouts
    
    def is_late_game(self, clock: GameClock) -> bool:
        """Check if it's late in the game (4th quarter or OT)."""
        return clock.quarter >= 4 and clock.minutes < 8

@dataclass
class Game:
    """
    Represents a football game simulation between two teams.
    Contains all the logic for simulating plays and game flow.
    """
    home_team: Team
    away_team: Team
    
    # Game components
    conditions: GameConditions = field(default_factory=GameConditions)
    clock: GameClock = field(default_factory=GameClock)
    state: GameState = field(default_factory=GameState)
    
    # Simulation control
    verbose: bool = False
    log_plays: bool = True
    
    def __post_init__(self):
        """Initialize game state after creation."""
        # Set possession to home team to start
        self.state.possession = self.home_team.id
        
        # Prepare teams for the game
        self.home_team.prepare_for_game(is_home=True)
        self.away_team.prepare_for_game(is_home=False)
        
        # Reset stats
        self.home_team.reset_for_new_game()
        self.away_team.reset_for_new_game()
    
    def get_possession_team(self) -> Team:
        """Get the team currently with possession."""
        return self.home_team if self.state.possession == self.home_team.id else self.away_team
    
    def get_defense_team(self) -> Team:
        """Get the team currently on defense."""
        return self.away_team if self.state.possession == self.home_team.id else self.home_team
    
    def simulate_play(self) -> Dict:
        """
        Simulate a single play and return the result.
        Enhanced to track more detailed player statistics.
        """
        offense = self.get_possession_team()
        defense = self.get_defense_team()
        
        # Get key players
        qb = offense.get_starter("QB")
        rb = offense.get_starter("RB")
        wr = offense.get_starter("WR")
        
        # Get key defensive players
        linebacker = defense.get_starter("LB")
        cornerback = defense.get_starter("CB")
        safety = defense.get_starter("S")
        
        # Determine play type (simplified)
        is_pass = random.random() < offense.attributes.pass_tendency
        
        # Basic result calculation
        off_rating = offense.get_offensive_rating()
        def_rating = defense.get_defensive_rating()
        
        # Apply weather factors
        weather_factors = self.conditions.get_weather_factors()
        
        # Base success probability
        success_prob = 0.5 + (off_rating - def_rating) * 0.3
        
        # Play outcome
        result = {}
        result["play_type"] = "pass" if is_pass else "run"
        result["down"] = self.state.down
        result["distance"] = self.state.distance
        result["field_position"] = self.state.field_position
        result["quarter"] = self.clock.quarter
        result["time"] = f"{self.clock.minutes}:{self.clock.seconds:02d}"
        
        # Defensive player involvement (for tracking stats)
        primary_defender = None
        secondary_defenders = []
        
        # Simulate the play
        if is_pass:
            # Pass play
            if qb:
                completion_prob = success_prob * weather_factors["passing_modifier"]
                is_complete = random.random() < completion_prob
                
                # Select target receiver (simplified - could expand to multiple receivers)
                receiver = wr
                
                # Select primary defender
                primary_defender = cornerback
                secondary_defenders = [safety] if safety else []
                
                if is_complete:
                    # Determine yards gained
                    base_yards = random.normalvariate(6, 4)  # Slightly more conservative
                    yards_gained = max(0, int(base_yards * (0.7 + off_rating * 0.3)))
                    
                    # Check for touchdown
                    is_touchdown = self.state.field_position + yards_gained >= 100
                    
                    # Make long touchdowns more rare
                    if is_touchdown and self.state.field_position < 75:
                        # Less likely to score from far away
                        if random.random() > 0.08:  # Only 8% chance of long TD
                            yards_gained = min(yards_gained, 25)  # Cap the gain
                            is_touchdown = False
                    
                    # Update offensive player stats
                    qb.stats.passing_attempts += 1
                    qb.stats.passing_completions += 1
                    qb.stats.passing_yards += yards_gained
                    
                    if receiver:
                        receiver.stats.receiving_targets += 1
                        receiver.stats.receiving_catches += 1
                        receiver.stats.receiving_yards += yards_gained
                    
                    if is_touchdown:
                        qb.stats.passing_tds += 1
                        if receiver:
                            receiver.stats.receiving_tds += 1
                    
                    # Update defensive player stats
                    if primary_defender:
                        primary_defender.stats.tackles += 1
                    
                    result["yards_gained"] = yards_gained
                    result["result"] = "complete"
                    result["passer"] = qb.id if qb else None
                    result["receiver"] = receiver.id if receiver else None
                    result["primary_defender"] = primary_defender.id if primary_defender else None
                else:
                    # Incomplete pass
                    yards_gained = 0
                    
                    # Check for interception
                    int_chance = 0.08 * (1 - qb.attributes.decision_making / 100)
                    is_interception = random.random() < int_chance
                    
                    # Update stats
                    qb.stats.passing_attempts += 1
                    
                    if receiver:
                        receiver.stats.receiving_targets += 1
                    
                    if is_interception:
                        qb.stats.passing_ints += 1
                        result["is_interception"] = True
                        result["result"] = "interception"
                        
                        # Defense stats
                        if primary_defender:
                            primary_defender.stats.interceptions += 1
                    else:
                        result["result"] = "incomplete"
                    
                    result["yards_gained"] = yards_gained
                    result["passer"] = qb.id if qb else None
                    result["receiver"] = receiver.id if receiver else None
                    result["primary_defender"] = primary_defender.id if primary_defender else None
            else:
                # No QB available (extremely rare case)
                result["result"] = "incomplete"
                result["yards_gained"] = 0
        else:
            # Run play
            if rb:
                # Determine yards gained
                base_yards = random.normalvariate(3.5, 2.5)  # More realistic average
                yards_gained = max(-2, int(base_yards * (0.7 + off_rating * 0.3)))
                
                # Select primary defender for the tackle
                primary_defender = linebacker
                secondary_defenders = [safety] if safety else []
                
                # Check for touchdown
                is_touchdown = self.state.field_position + yards_gained >= 100
                
                # Make long touchdowns more rare
                if is_touchdown and self.state.field_position < 80:
                    # Less likely to score from far away
                    if random.random() > 0.1:  # Only 10% chance of long TD
                        yards_gained = min(yards_gained, 20)  # Cap the gain
                        is_touchdown = False
                
                # Update stats
                rb.stats.rushing_attempts += 1
                rb.stats.rushing_yards += yards_gained
                
                if is_touchdown:
                    rb.stats.rushing_tds += 1
                    result["is_touchdown"] = True
                    
                # Update defensive player stats
                if primary_defender:
                    primary_defender.stats.tackles += 1
                    
                if secondary_defenders and yards_gained > 5:
                    # Secondary tackler for longer runs
                    secondary_defenders[0].stats.tackles += 1
                    
                # Check for fumble
                fumble_chance = 0.03 * (1 - rb.attributes.strength / 200)
                is_fumble = random.random() < fumble_chance
                
                if is_fumble:
                    rb.stats.fumbles += 1
                    result["is_fumble"] = True
                    result["result"] = "fumble"
                    
                    # Defense stats
                    if primary_defender:
                        primary_defender.stats.forced_fumbles += 1
                        # 50% chance primary defender recovers the fumble
                        if random.random() > 0.5:
                            primary_defender.stats.fumble_recoveries += 1
                else:
                    result["result"] = "run"
                
                result["yards_gained"] = yards_gained
                result["runner"] = rb.id if rb else None
                result["primary_defender"] = primary_defender.id if primary_defender else None
            else:
                # No RB available (extremely rare case)
                result["result"] = "run"
                result["yards_gained"] = 0
        
        # Clock management (simplified)
        time_elapsed = 30  # Average play time in seconds
        if not (result.get("is_touchdown") or result.get("is_interception") or 
                result.get("is_fumble") or result["result"] == "incomplete"):
            # Clock runs on successful plays
            self.clock.advance(time_elapsed)
        
        # Update game state
        if result.get("is_interception") or result.get("is_fumble"):
            # Turnover - change possession
            self.state.change_possession()
        else:
            # Update down, distance, field position
            yards_gained = result["yards_gained"]
            self.state.update_field_position(yards_gained)
            self.state.update_down_and_distance(yards_gained)
            
            if result.get("is_touchdown"):
                # Handle touchdown
                if self.state.possession == self.home_team.id:
                    self.state.home_score += 7  # Simplified, assuming extra point
                else:
                    self.state.away_score += 7
                
                # Reset after touchdown
                self.state.change_possession()
            elif self.state.down > 4:
                # Turnover on downs
                self.state.change_possession()
        
        # Record play in history
        if self.log_plays:
            self.state.add_play_to_history(result)
        
        # Verbose output
        if self.verbose:
            print(f"Q{self.clock.quarter} {self.clock.minutes}:{self.clock.seconds:02d} - ", end="")
            print(f"{self.state.down} & {self.state.distance} at {self.state.field_position} yard line")
            
            if is_pass:
                print(f"Play: {qb.name if qb else 'QB'} {result['result']} to {receiver.name if receiver else 'receiver'} for {result['yards_gained']} yards")
            else:
                print(f"Play: {rb.name if rb else 'RB'} {result['result']} for {result['yards_gained']} yards")
                
            print(f"Score: {self.home_team.name} {self.state.home_score} - {self.away_team.name} {self.state.away_score}")
            print()
        
        return result
    
    def simulate_game(self) -> Dict:
        """
        Simulate an entire game and return the final statistics.
        Enhanced to include detailed player statistics.
        """
        # Set up game
        self.clock.start()
        
        # Main game loop
        while not self.clock.is_game_over():
            self.simulate_play()
            
            # Check for end of quarter
            if self.clock.seconds == 0 and self.clock.minutes == 0:
                if self.clock.quarter < 4:
                    self.clock.quarter += 1
                    self.clock.reset_for_quarter()
        
        # Game over - process results
        if self.state.home_score > self.state.away_score:
            self.home_team.stats.wins += 1
            self.away_team.stats.losses += 1
            winner = self.home_team
        elif self.state.away_score > self.state.home_score:
            self.away_team.stats.wins += 1
            self.home_team.stats.losses += 1
            winner = self.away_team
        else:
            self.home_team.stats.ties += 1
            self.away_team.stats.ties += 1
            winner = None
        
        # Update team stats from player stats
        self.home_team.update_team_stats_from_players()
        self.away_team.update_team_stats_from_players()
        
        # Collect player statistics
        home_player_stats = []
        away_player_stats = []
        
        # Process offensive players first (QB, RB, WR, TE)
        offensive_positions = ["QB", "RB", "WR", "TE"]
        for player in self.home_team.roster.values():
            if player.position in offensive_positions:
                player_stats = self._extract_player_stats(player)
                if player_stats["has_stats"]:
                    home_player_stats.append(player_stats)
        
        for player in self.away_team.roster.values():
            if player.position in offensive_positions:
                player_stats = self._extract_player_stats(player)
                if player_stats["has_stats"]:
                    away_player_stats.append(player_stats)
        
        # Process defensive players next (LB, DL, CB, S)
        defensive_positions = ["LB", "DL", "CB", "S"]
        for player in self.home_team.roster.values():
            if player.position in defensive_positions:
                player_stats = self._extract_player_stats(player)
                if player_stats["has_stats"]:
                    home_player_stats.append(player_stats)
        
        for player in self.away_team.roster.values():
            if player.position in defensive_positions:
                player_stats = self._extract_player_stats(player)
                if player_stats["has_stats"]:
                    away_player_stats.append(player_stats)
        
        # Save player stats to historical records
        for player in self.home_team.roster.values():
            player.save_game_stats()
        
        for player in self.away_team.roster.values():
            player.save_game_stats()
        
        # Return game summary with detailed player stats
        return {
            "home_team": self.home_team.name,
            "away_team": self.away_team.name,
            "home_score": self.state.home_score,
            "away_score": self.state.away_score,
            "winner": winner.name if winner else "Tie",
            "plays": len(self.state.play_history),
            "home_stats": {
                "total_yards": self.home_team.stats.total_yards,
                "passing_yards": self.home_team.stats.passing_yards,
                "rushing_yards": self.home_team.stats.rushing_yards,
                "turnovers": self.home_team.stats.turnovers,
                "time_of_possession": self.home_team.stats.time_of_possession,
                "first_downs": self.home_team.stats.first_downs
            },
            "away_stats": {
                "total_yards": self.away_team.stats.total_yards,
                "passing_yards": self.away_team.stats.passing_yards,
                "rushing_yards": self.away_team.stats.rushing_yards,
                "turnovers": self.away_team.stats.turnovers,
                "time_of_possession": self.away_team.stats.time_of_possession,
                "first_downs": self.away_team.stats.first_downs
            },
            "home_player_stats": home_player_stats,
            "away_player_stats": away_player_stats
        }
    
    def _extract_player_stats(self, player) -> Dict:
        """
        Extract relevant statistics from a player based on position.
        Returns a dict with player info and stats.
        """
        # Base player info
        player_stats = {
            "id": player.id,
            "name": player.name,
            "position": player.position,
            "team": player.team,
            "has_stats": False  # Flag to indicate if player has any stats worth showing
        }
        
        # Add relevant stats based on position type
        if player.position in ["QB", "RB", "WR", "TE"]:
            # Offensive player stats
            stats = {}
            
            # QB stats
            if player.position == "QB":
                stats["passing_attempts"] = player.stats.passing_attempts
                stats["passing_completions"] = player.stats.passing_completions
                stats["passing_yards"] = player.stats.passing_yards
                stats["passing_tds"] = player.stats.passing_tds
                stats["passing_ints"] = player.stats.passing_ints
                stats["comp_pct"] = round(player.stats.passing_completions / player.stats.passing_attempts * 100, 1) if player.stats.passing_attempts > 0 else 0
                stats["yards_per_attempt"] = round(player.stats.passing_yards / player.stats.passing_attempts, 1) if player.stats.passing_attempts > 0 else 0
                
                # QB rushing
                stats["rushing_attempts"] = player.stats.rushing_attempts
                stats["rushing_yards"] = player.stats.rushing_yards
                stats["rushing_tds"] = player.stats.rushing_tds
                
                # Set flag if QB has any stats
                if player.stats.passing_attempts > 0 or player.stats.rushing_attempts > 0:
                    player_stats["has_stats"] = True
                    
            # RB stats
            elif player.position == "RB":
                stats["rushing_attempts"] = player.stats.rushing_attempts
                stats["rushing_yards"] = player.stats.rushing_yards
                stats["rushing_tds"] = player.stats.rushing_tds
                stats["yards_per_carry"] = round(player.stats.rushing_yards / player.stats.rushing_attempts, 1) if player.stats.rushing_attempts > 0 else 0
                
                # RB receiving
                stats["receiving_targets"] = player.stats.receiving_targets
                stats["receiving_catches"] = player.stats.receiving_catches
                stats["receiving_yards"] = player.stats.receiving_yards
                stats["receiving_tds"] = player.stats.receiving_tds
                
                # Set flag if RB has any stats
                if player.stats.rushing_attempts > 0 or player.stats.receiving_targets > 0:
                    player_stats["has_stats"] = True
                    
            # WR/TE stats
            elif player.position in ["WR", "TE"]:
                stats["receiving_targets"] = player.stats.receiving_targets
                stats["receiving_catches"] = player.stats.receiving_catches
                stats["receiving_yards"] = player.stats.receiving_yards
                stats["receiving_tds"] = player.stats.receiving_tds
                stats["yards_per_catch"] = round(player.stats.receiving_yards / player.stats.receiving_catches, 1) if player.stats.receiving_catches > 0 else 0
                stats["catch_rate"] = round(player.stats.receiving_catches / player.stats.receiving_targets * 100, 1) if player.stats.receiving_targets > 0 else 0
                
                # WR/TE rushing (e.g., jet sweeps, end-arounds)
                stats["rushing_attempts"] = player.stats.rushing_attempts
                stats["rushing_yards"] = player.stats.rushing_yards
                stats["rushing_tds"] = player.stats.rushing_tds
                
                # Set flag if WR/TE has any stats
                if player.stats.receiving_targets > 0 or player.stats.rushing_attempts > 0:
                    player_stats["has_stats"] = True
                    
        elif player.position in ["LB", "DL", "CB", "S"]:
            # Defensive player stats
            stats = {}
            stats["tackles"] = player.stats.tackles
            stats["sacks"] = player.stats.sacks
            stats["interceptions"] = player.stats.interceptions
            stats["forced_fumbles"] = player.stats.forced_fumbles
            stats["fumble_recoveries"] = player.stats.fumble_recoveries
            stats["defensive_tds"] = player.stats.defensive_tds
            
            # Set flag if defensive player has any stats
            if (player.stats.tackles > 0 or player.stats.sacks > 0 or player.stats.interceptions > 0 or
                player.stats.forced_fumbles > 0 or player.stats.fumble_recoveries > 0):
                player_stats["has_stats"] = True
        
        # Add stats to player_stats dict
        player_stats["stats"] = stats
        
        # Add fantasy points
        player_stats["fantasy_points"] = player.stats.calculate_fantasy_points()
        
        return player_stats