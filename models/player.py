# models/player.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class PlayerStats:
    """Container for player statistics that can be updated during simulation."""
    # Offensive stats
    passing_attempts: int = 0
    passing_completions: int = 0
    passing_yards: int = 0
    passing_tds: int = 0
    passing_ints: int = 0
    
    rushing_attempts: int = 0
    rushing_yards: int = 0
    rushing_tds: int = 0
    
    receiving_targets: int = 0
    receiving_catches: int = 0
    receiving_yards: int = 0
    receiving_tds: int = 0
    
    fumbles: int = 0
    
    # Defensive stats
    tackles: int = 0
    sacks: int = 0
    interceptions: int = 0
    forced_fumbles: int = 0
    fumble_recoveries: int = 0
    defensive_tds: int = 0
    
    def calculate_fantasy_points(self, scoring_system='standard') -> float:
        """Calculate fantasy points based on the stats and specified scoring system."""
        points = 0
        
        if scoring_system == 'standard':
            # Passing
            points += self.passing_yards * 0.04  # 1 point per 25 yards
            points += self.passing_tds * 4
            points -= self.passing_ints * 2
            
            # Rushing
            points += self.rushing_yards * 0.1  # 1 point per 10 yards
            points += self.rushing_tds * 6
            
            # Receiving
            points += self.receiving_yards * 0.1  # 1 point per 10 yards
            points += self.receiving_catches * 0  # 0 points in standard
            points += self.receiving_tds * 6
            
            # Misc
            points -= self.fumbles * 2
            
        elif scoring_system == 'ppr':
            # Same as standard but with PPR
            points += self.passing_yards * 0.04
            points += self.passing_tds * 4
            points -= self.passing_ints * 2
            
            points += self.rushing_yards * 0.1
            points += self.rushing_tds * 6
            
            points += self.receiving_yards * 0.1
            points += self.receiving_catches * 1  # 1 point per reception
            points += self.receiving_tds * 6
            
            points -= self.fumbles * 2
            
        # We can add more scoring systems as needed
        
        return points
    
    def reset(self):
        """Reset all stats to zero."""
        for attr in self.__dict__:
            setattr(self, attr, 0)

@dataclass
class PlayerAttributes:
    """Player attributes that influence performance in simulations."""
    # General attributes (0-100 scale)
    speed: int = 50
    strength: int = 50
    agility: int = 50
    awareness: int = 50
    
    # Position-specific attributes (0-100 scale)
    # QB attributes
    throwing_power: int = 50
    throwing_accuracy: int = 50
    decision_making: int = 50
    
    # RB/WR attributes
    catching: int = 50
    elusiveness: int = 50
    route_running: int = 50
    breaking_tackles: int = 50
    
    # Defensive attributes
    tackling: int = 50
    coverage: int = 50
    block_shedding: int = 50
    
    # Special attributes for simulation effects
    clutch: int = 50  # Performance in critical situations
    injury_prone: int = 50  # Likelihood of injury
    consistency: int = 50  # Consistency of performance
    
    # Custom attributes dict for future expansion
    custom: Dict[str, float] = field(default_factory=dict)

@dataclass
class Player:
    """
    Represents a football player with identity, attributes, and statistics.
    This model is designed to be used in simulations.
    """
    # Identity
    id: str
    name: str
    team: str
    position: str
    age: int = 25
    
    # Core components
    attributes: PlayerAttributes = field(default_factory=PlayerAttributes)
    stats: PlayerStats = field(default_factory=PlayerStats)
    
    # Historical data for learning
    historical_stats: List[PlayerStats] = field(default_factory=list)
    
    # Performance modifiers
    injury_status: Optional[str] = None
    game_status: str = "active"  # active, questionable, doubtful, out
    confidence: float = 1.0  # Multiplier for performance (0.5 = playing at 50%)
    
    # Track fantasy points for DFS analysis
    fantasy_points_history: List[float] = field(default_factory=list)
    
    def predict_performance(self, opponent, game_conditions):
        """
        Predict player performance against specific opponent and conditions.
        This is a placeholder for future ML-based prediction.
        """
        # In the future, this could use ML models to predict performance
        # For now, return a simple estimate based on attributes
        base_value = sum([
            getattr(self.attributes, attr) 
            for attr in self.attributes.__dict__ 
            if not attr.startswith('_') and attr != 'custom'
        ]) / 1000  # Normalize
        
        return base_value * self.confidence
    
    def save_game_stats(self):
        """Save current game stats to historical record."""
        self.historical_stats.append(self.stats)
        
        # Calculate and save fantasy points
        fp = self.stats.calculate_fantasy_points()
        self.fantasy_points_history.append(fp)
        
        # Reset current stats for next game
        self.stats = PlayerStats()
        
    def get_average_fantasy_points(self):
        """Calculate the player's average fantasy points over their history."""
        if not self.fantasy_points_history:
            return 0
        return sum(self.fantasy_points_history) / len(self.fantasy_points_history)