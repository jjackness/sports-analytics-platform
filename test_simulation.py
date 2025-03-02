# test_simulation.py
from models.team import Team
from simulation.engine import SimulationEngine

def main():
    # Create teams with the required parameters
    team1 = Team(id="team1", name="Patriots", abbreviation="NE", city="New England")
    team2 = Team(id="team2", name="Jets", abbreviation="NYJ", city="New York")

    # Create simulation engine
    engine = SimulationEngine()

    # Simulate a game
    print(f"Simulating: {team1.name} vs {team2.name}")
    results = engine.simulate_game(team1, team2)
    
    # Print basic results
    print(f"\nFinal Score:")
    print(f"{team1.name}: {results['home_team']['score']}")
    print(f"{team2.name}: {results['away_team']['score']}")
    
    # Print some play statistics
    play_history = results['play_history']
    pass_plays = [p for p in play_history if p['play_type'] == 'pass']
    run_plays = [p for p in play_history if p['play_type'] == 'run']
    
    print(f"\nPlay Statistics:")
    print(f"Total plays: {len(play_history)}")
    print(f"Pass plays: {len(pass_plays)} ({len(pass_plays)/len(play_history)*100:.1f}%)")
    print(f"Run plays: {len(run_plays)} ({len(run_plays)/len(play_history)*100:.1f}%)")
    
    # Save results
    filepath = engine.save_results(results, "test_game")
    print(f"\nResults saved to: {filepath}")

if __name__ == "__main__":
    main()