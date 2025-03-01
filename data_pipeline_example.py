# data_pipeline_example.py
from data_processing.data_import import DataImporter
from data_processing.data_analysis import PlayByPlayAnalyzer
from data_processing.data_export import DataExporter
import pandas as pd
import os

def run_data_pipeline_example():
    """
    Example of a complete data pipeline:
    1. Import data
    2. Analyze it
    3. Export results for use in simulation
    """
    print("NFL Data Pipeline Example")
    print("=========================")
    
    # Initialize components
    importer = DataImporter(data_dir="data")
    analyzer = PlayByPlayAnalyzer()
    exporter = DataExporter(output_dir="results")
    
    # Step 1: Load sample data
    # In a real implementation, we would use the NFL API or nflfastR
    # For this example, we'll check if we have sample data or use a simple DataFrame
    sample_data_path = os.path.join("data", "sample_pbp.csv")
    
    if os.path.exists(sample_data_path):
        print(f"Loading sample data from {sample_data_path}")
        pbp_data = importer.import_csv(sample_data_path)
    else:
        print("Creating simple sample data for demonstration")
        # Create a simple sample dataframe with guaranteed equal lengths
        num_rows = 100
        data = {
            'game_id': list(range(1, num_rows + 1)),
            'play_id': list(range(1, num_rows + 1)),
            'posteam': ['NE', 'KC', 'SF', 'BAL', 'DAL'] * 20,
            'defteam': ['KC', 'SF', 'DAL', 'CIN', 'PHI'] * 20,
            'down': [1, 2, 3, 4] * 25,
            'ydstogo': [10] * 50 + [5] * 25 + [2] * 15 + [1] * 10,  # Exactly 100 elements
            'play_type': ['run', 'pass'] * 50,  # Exactly 100 elements
            'yards_gained': [0] * 20 + [3] * 30 + [7] * 20 + [12] * 15 + [25] * 10 + [-2] * 5,  # Exactly 100 elements
            'touchdown': [0] * 95 + [1] * 5,  # Exactly 100 elements
            'turnover': [0] * 98 + [1] * 2,  # Exactly 100 elements
        }
        
        # Double-check all arrays have the same length
        for key, value in data.items():
            print(f"  {key}: {len(value)} elements")
        pbp_data = pd.DataFrame(data)
        
        # Save sample data for future use
        os.makedirs("data", exist_ok=True)
        pbp_data.to_csv(sample_data_path, index=False)
        print(f"Saved sample data to {sample_data_path}")
    
    # Step 2: Analyze the data
    print("\nAnalyzing play-by-play data...")
    analyzer.load_data(pbp_data)
    
    # Analyze play calling tendencies
    play_calling = analyzer.analyze_play_calling()
    print("\nPlay calling tendencies by down and distance:")
    print(play_calling.head())
    
    # Analyze run play outcomes
    run_outcomes = analyzer.analyze_play_outcomes(play_type='run')
    print("\nRun play outcome statistics:")
    for key, value in run_outcomes.items():
        print(f"  {key}: {value}")
    
    # Analyze pass play outcomes
    pass_outcomes = analyzer.analyze_play_outcomes(play_type='pass')
    print("\nPass play outcome statistics:")
    for key, value in pass_outcomes.items():
        print(f"  {key}: {value}")
    
    # Step 3: Export results for use in simulation
    print("\nExporting results...")
    
    # Export play calling tendencies
    if not play_calling.empty:
        exporter.export_csv(play_calling, "play_calling_tendencies.csv")
    
    # Export play outcome distributions as simulation parameters
    simulation_params = {
        "run_play": run_outcomes,
        "pass_play": pass_outcomes,
        "source_data": {
            "sample_size": len(pbp_data),
            "teams_included": pbp_data['posteam'].unique().tolist(),
            "plays_analyzed": len(pbp_data)
        }
    }
    
    exporter.export_simulation_params(simulation_params)
    
    print("\nData pipeline complete!")
    print("The exported data can now be used to make the simulation more realistic.")

if __name__ == "__main__":
    run_data_pipeline_example()