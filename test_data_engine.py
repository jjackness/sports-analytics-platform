"""
Test the data-enhanced simulation engine.

This script runs a test simulation to verify that our enhanced engine works
correctly with the NFL data provider.
"""

from models.team import Team
from simulation.engine import SimulationEngine
import json

def main():
    """Run a test simulation with the enhanced engine"""
    print("Testing data-enhanced simulation engine\n")
    
    # Create test teams
    home_team = Team(
        id="NE", 
        name="Patriots", 
        abbreviation="NE", 
        city="New England"
    )
    
    away_team = Team(
        id="KC", 
        name="Chiefs", 
        abbreviation="KC", 
        city="Kansas City"
    )
    
    # Create simulation engine
    engine = SimulationEngine()
    
    # Simulate a single game
    print(f"Simulating: {home_team.name} vs {away_team.name}")
    results = engine.simulate_game(home_team, away_team)
    
    # Print basic results
    print(f"\nFinal Score:")
    print(f"{home_team.name}: {results['home_team']['score']}")
    print(f"{away_team.name}: {results['away_team']['score']}")
    
    # Analyze plays
    plays = results['play_history']
    total_plays = len(plays)
    
    # Count play types
    play_types = {}
    for play in plays:
        play_type = play.get('play_type', 'unknown')
        if play_type not in play_types:
            play_types[play_type] = 0
        play_types[play_type] += 1
    
    # Print play analysis
    print(f"\nPlay Analysis (Total: {total_plays} plays):")
    for play_type, count in play_types.items():
        percentage = (count / total_plays) * 100
        print(f"  {play_type}: {count} plays ({percentage:.1f}%)")
    
    # Analyze by down
    plays_by_down = {1: [], 2: [], 3: [], 4: []}
    for play in plays:
        down = play.get('down')
        if down in plays_by_down:
            plays_by_down[down].append(play)
    
    print("\nPlay Type by Down:")
    for down, down_plays in plays_by_down.items():
        if not down_plays:
            continue
            
        pass_plays = sum(1 for p in down_plays if p.get('play_type') == 'pass')
        run_plays = sum(1 for p in down_plays if p.get('play_type') == 'run')
        other_plays = len(down_plays) - pass_plays - run_plays
        
        total = len(down_plays)
        if total > 0:
            pass_pct = (pass_plays / total) * 100
            run_pct = (run_plays / total) * 100
            other_pct = (other_plays / total) * 100
            
            print(f"  Down {down} ({total} plays): {pass_pct:.1f}% pass, {run_pct:.1f}% run, {other_pct:.1f}% other")
    
    # Save results
    filepath = engine.save_results(results, "test_data_game")
    print(f"\nResults saved to: {filepath}")
    
    # Run multiple game simulation
    num_games = 5
    print(f"\nSimulating {num_games} games between {home_team.name} and {away_team.name}...")
    multi_results = engine.simulate_multiple_games(home_team, away_team, num_games)
    
    # Print multiple game summary
    summary = multi_results['summary']
    print(f"\nMultiple Game Summary:")
    print(f"  {summary['home_team']['name']}: {summary['home_team']['wins']} wins, {summary['home_team']['avg_score']:.1f} avg. points")
    print(f"  {summary['away_team']['name']}: {summary['away_team']['wins']} wins, {summary['away_team']['avg_score']:.1f} avg. points")
    print(f"  Ties: {summary['ties']}")
    
    # Save multiple game results
    filepath = engine.save_results(multi_results, "test_data_multi_game")
    print(f"Multiple game results saved to: {filepath}")

if __name__ == "__main__":
    main()