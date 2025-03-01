# main.py
import os
import json
import random
from simulation.engine import SimulationEngine
from models.game import GameConditions

def run_demo():
    """Run a demonstration of the simulation framework."""
    print("Football Game Simulation")
    print("=======================")
    
    # Create simulation engine
    sim_engine = SimulationEngine(output_dir="results")
    
    # Create demo teams
    print("Creating demo teams...")
    sim_engine.create_default_teams(num_teams=4)
    
    # Print team info
    team_ids = list(sim_engine.teams.keys())
    print(f"Created {len(team_ids)} teams:")
    for team_id, team in sim_engine.teams.items():
        print(f"  - {team.name} ({team_id})")
        qb = team.get_starter("QB")
        if qb:
            print(f"    QB: {qb.name} (Power: {qb.attributes.throwing_power}, Accuracy: {qb.attributes.throwing_accuracy})")
    
    # Run a single game simulation
    print("\nSimulating a single game...")
    result = sim_engine.simulate_game(team_ids[0], team_ids[1], verbose=True)
    
    print("\nGame Result:")
    print(f"{result['home_team']} {result['home_score']} - {result['away_team']} {result['away_score']}")
    print(f"Winner: {result['winner']}")
    
    # Run multiple simulations
    print("\nRunning multiple simulations...")
    projections = sim_engine.run_multiple_simulations(team_ids[0], team_ids[1], num_sims=10)
    
    print("\nSimulation Results:")
    print(f"Home win probability: {projections['home_win_pct']:.1%}")
    print(f"Away win probability: {projections['away_win_pct']:.1%}")
    print(f"Tie probability: {projections['tie_pct']:.1%}")
    
    print("\nTop Fantasy Projections:")
    for i, player in enumerate(projections['player_projections'][:5]):
        print(f"{i+1}. {player['name']} ({player['team']}, {player['position']}): {player['fantasy_points_avg']:.1f} pts")
    
    # Simulate a mini-season
    print("\nSimulating a mini-season...")
    # Use the balanced season simulator (each team plays 4 games)
    season = sim_engine.simulate_season(num_games_per_team=4, randomize_conditions=True, verbose=True)
    
    print("\nSeason Standings:")
    for i, team in enumerate(season['standings']):
        print(f"{i+1}. {team['team']}: {team['wins']}-{team['losses']}-{team['ties']} ({team['pct']:.3f})")
    
    # Export fantasy projections
    print("\nExporting fantasy projections...")
    all_projections = sim_engine.export_fantasy_projections("results/fantasy_projections.csv")
    
    print("\nDone! Check the 'results' directory for detailed output files.")

def run_custom_simulation():
    """
    Run a custom simulation based on user input.
    This would be expanded with more user interaction.
    """
    print("Custom Football Simulation")
    print("=========================")
    
    # Create simulation engine
    sim_engine = SimulationEngine(output_dir="results")
    
    # Allow loading data or creating test data
    print("1. Create test teams")
    print("2. Load team data from file")
    choice = input("Choose an option: ")
    
    if choice == "1":
        num_teams = int(input("How many teams to create? "))
        sim_engine.create_default_teams(num_teams=num_teams)
    elif choice == "2":
        file_path = input("Enter file path for team data: ")
        if os.path.exists(file_path):
            sim_engine.load_team_data(file_path)
        else:
            print("File not found. Creating 2 test teams instead.")
            sim_engine.create_default_teams(num_teams=2)
    else:
        print("Invalid choice. Creating 2 test teams.")
        sim_engine.create_default_teams(num_teams=2)
    
    # List available teams
    print("\nAvailable Teams:")
    team_ids = list(sim_engine.teams.keys())
    for i, team_id in enumerate(team_ids):
        team = sim_engine.teams[team_id]
        print(f"{i+1}. {team.name} ({team_id})")
    
    # Set up simulation parameters
    print("\nSimulation Options:")
    print("1. Run a single game")
    print("2. Run multiple simulations of same matchup")
    print("3. Simulate a full season")
    sim_choice = input("Choose an option: ")
    
    if sim_choice == "1":
        # Single game
        home_idx = int(input(f"Select home team (1-{len(team_ids)}): ")) - 1
        away_idx = int(input(f"Select away team (1-{len(team_ids)}): ")) - 1
        
        if 0 <= home_idx < len(team_ids) and 0 <= away_idx < len(team_ids):
            verbose = input("Show detailed play-by-play? (y/n): ").lower() == 'y'
            result = sim_engine.simulate_game(team_ids[home_idx], team_ids[away_idx], verbose=verbose)
            
            print("\nGame Result:")
            print(f"{result['home_team']} {result['home_score']} - {result['away_team']} {result['away_score']}")
        else:
            print("Invalid team selection.")
    
    elif sim_choice == "2":
        # Multiple simulations
        home_idx = int(input(f"Select home team (1-{len(team_ids)}): ")) - 1
        away_idx = int(input(f"Select away team (1-{len(team_ids)}): ")) - 1
        
        if 0 <= home_idx < len(team_ids) and 0 <= away_idx < len(team_ids):
            num_sims = int(input("Number of simulations to run: "))
            
            projections = sim_engine.run_multiple_simulations(
                team_ids[home_idx], team_ids[away_idx], num_sims=num_sims
            )
            
            print("\nSimulation Results:")
            print(f"Home win probability: {projections['home_win_pct']:.1%}")
            print(f"Away win probability: {projections['away_win_pct']:.1%}")
            
            print("\nTop Fantasy Projections:")
            for i, player in enumerate(projections['player_projections'][:5]):
                print(f"{i+1}. {player['name']} ({player['position']}): {player['fantasy_points_avg']:.1f} pts")
        else:
            print("Invalid team selection.")
    
    elif sim_choice == "3":
        # Full season
        print("Setting up season...")
        games_per_team = int(input("How many games should each team play? (default: 16): ") or "16")
        
        season = sim_engine.simulate_season(
            num_games_per_team=games_per_team, 
            randomize_conditions=True,
            verbose=input("Show game results? (y/n): ").lower() == 'y'
        )
        
        print("\nSeason Standings:")
        for i, team in enumerate(season['standings']):
            print(f"{i+1}. {team['team']}: {team['wins']}-{team['losses']}-{team['ties']} ({team['pct']:.3f})")
    
    # Export results
    export = input("\nExport fantasy projections? (y/n): ").lower() == 'y'
    if export:
        file_path = input("Enter output file path (or press Enter for default): ")
        if not file_path:
            file_path = "results/fantasy_projections.csv"
        
        sim_engine.export_fantasy_projections(file_path)
        print(f"Projections exported to {file_path}")

if __name__ == "__main__":
    # Choose mode
    print("Select mode:")
    print("1. Run demonstration")
    print("2. Run custom simulation")
    mode = input("Choice: ")
    
    if mode == "2":
        run_custom_simulation()
    else:
        run_demo()