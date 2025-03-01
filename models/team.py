# models/team.py
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from .player import Player

@dataclass
class TeamStats:
    """Container for team-level statistics."""
    # Offensive stats
    points_scored: int = 0
    total_yards: int = 0
    passing_yards: int = 0
    rushing_yards: int = 0
    first_downs: int = 0
    third_down_conversions: int = 0
    third_down_attempts: int = 0
    fourth_down_conversions: int = 0
    fourth_down_attempts: int = 0
    turnovers: int = 0
    time_of_possession: int = 0  # In seconds
    
    # Defensive stats
    points_allowed: int = 0
    yards_allowed: int = 0
    passing_yards_allowed: int = 0
    rushing_yards_allowed: int = 0
    sacks: int = 0
    interceptions: int = 0
    fumbles_recovered: int = 0
    
    # Game results
    wins: int = 0
    losses: int = 0
    ties: int = 0
    
    def reset_game_stats(self):
        """Reset stats that apply to a single game."""
        for attr in self.__dict__:
            if attr not in ['wins', 'losses', 'ties']:
                setattr(self, attr, 0)

@dataclass
class TeamAttributes:
    """Team-level attributes that influence simulation outcomes."""
    # Team identity factors
    home_field_advantage: float = 1.1  # Multiplier for home performance
    dome_team: bool = False  # Is this a dome team?
    altitude: int = 0  # Stadium altitude in feet
    
    # Coaching influence
    offensive_scheme: str = "balanced"  # balanced, air_raid, west_coast, run_heavy, etc.
    defensive_scheme: str = "balanced"  # 4-3, 3-4, tampa_2, etc.
    coaching_quality: int = 50  # 0-100 scale
    
    # Team composition factors
    offensive_line_rating: int = 50  # 0-100 scale
    defensive_line_rating: int = 50  # 0-100 scale
    secondary_rating: int = 50  # 0-100 scale
    special_teams_rating: int = 50  # 0-100 scale
    
    # Team tendencies
    pass_tendency: float = 0.55  # 0.0 = always run, 1.0 = always pass (modern NFL averages ~55% pass)
    blitz_tendency: float = 0.2  # Frequency of blitzing
    aggressive_fourth_down: float = 0.3  # Likelihood of going for it on 4th down
    
    # Custom attributes for future expansion
    custom: Dict[str, float] = field(default_factory=dict)

@dataclass
class Team:
    """
    Represents a football team with roster, attributes, and statistics.
    Contains methods for team operations during simulation.
    """
    # Identity
    id: str
    name: str
    abbreviation: str
    city: str
    
    # Components
    roster: Dict[str, Player] = field(default_factory=dict)
    attributes: TeamAttributes = field(default_factory=TeamAttributes)
    stats: TeamStats = field(default_factory=TeamStats)
    
    # Depth chart by position
    depth_chart: Dict[str, List[str]] = field(default_factory=dict)
    
    # Current game state
    current_injuries: List[str] = field(default_factory=list)  # List of injured player IDs
    
    def add_player(self, player: Player):
        """Add a player to the team roster."""
        self.roster[player.id] = player
        
        # Update depth chart
        if player.position not in self.depth_chart:
            self.depth_chart[player.position] = []
        
        if player.id not in self.depth_chart[player.position]:
            self.depth_chart[player.position].append(player.id)
    
    def get_starter(self, position: str) -> Optional[Player]:
        """Get the starting player for a given position."""
        if position in self.depth_chart and self.depth_chart[position]:
            player_id = self.depth_chart[position][0]
            if player_id in self.roster:
                return self.roster[player_id]
        return None
    
    def get_offensive_rating(self) -> float:
        """Calculate the team's overall offensive rating."""
        # Get key offensive players
        qb = self.get_starter("QB")
        rb = self.get_starter("RB")
        wr1 = self.get_starter("WR")
        
        # Base rating on player attributes and team factors
        base_rating = self.attributes.offensive_line_rating * 0.3
        
        if qb:
            qb_rating = (qb.attributes.throwing_accuracy + qb.attributes.throwing_power + 
                         qb.attributes.decision_making) / 3
            base_rating += qb_rating * 0.3
        
        if rb:
            rb_rating = (rb.attributes.speed + rb.attributes.elusiveness + 
                         rb.attributes.breaking_tackles) / 3
            base_rating += rb_rating * 0.2
        
        if wr1:
            wr_rating = (wr1.attributes.speed + wr1.attributes.catching + 
                         wr1.attributes.route_running) / 3
            base_rating += wr_rating * 0.2
        
        # Coaching adjustment
        base_rating *= (0.7 + (self.attributes.coaching_quality / 100 * 0.3))
        
        return base_rating / 100  # Normalize to 0-1 scale
    
    def get_defensive_rating(self) -> float:
        """Calculate the team's overall defensive rating."""
        # Base on team defensive attributes
        base_rating = (
            self.attributes.defensive_line_rating * 0.4 +
            self.attributes.secondary_rating * 0.4 +
            self.attributes.coaching_quality * 0.2
        )
        
        return base_rating / 100  # Normalize to 0-1 scale
    
    def prepare_for_game(self, is_home: bool = False):
        """
        Prepare the team for a game, setting appropriate modifiers
        based on home/away status, injuries, etc.
        """
        game_modifier = self.attributes.home_field_advantage if is_home else 1.0
        
        # Apply game modifier to each player
        for player_id, player in self.roster.items():
            # Skip injured players
            if player_id in self.current_injuries:
                player.game_status = "out"
                player.confidence = 0.0
                continue
            
            # Set active players with confidence based on team situation
            player.game_status = "active"
            player.confidence = game_modifier * (0.8 + (player.attributes.consistency / 500))
    
    def update_team_stats_from_players(self):
        """Aggregate player stats to team level."""
        # Reset certain team stats
        self.stats.passing_yards = 0
        self.stats.rushing_yards = 0
        self.stats.sacks = 0
        self.stats.interceptions = 0
        
        # Aggregate from players
        for player in self.roster.values():
            self.stats.passing_yards += player.stats.passing_yards
            self.stats.rushing_yards += player.stats.rushing_yards
            self.stats.sacks += player.stats.sacks
            self.stats.interceptions += player.stats.interceptions
        
        # Update total yards
        self.stats.total_yards = self.stats.passing_yards + self.stats.rushing_yards
    
    def reset_for_new_game(self):
        """Reset the team for a new game simulation."""
        self.stats.reset_game_stats()
        
        # Reset all player game stats
        for player in self.roster.values():
            player.stats = player.stats.__class__()  # Create a new empty stats object