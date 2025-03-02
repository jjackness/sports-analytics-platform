"""
NFL Data Generation Script

This script:
1. Creates the NFL data generator
2. Generates synthetic play-by-play data based on realistic NFL statistics
3. Extracts play tendencies and outcomes from the generated data
4. Saves the data to CSV and JSON files for use in simulations

No special packages are required beyond the Python standard library.
"""

import os
import time
import sys
from nfl_data_generator import NFLDataGenerator

def main():
    # Create a data generator
    print("Creating NFL data generator...")
    generator = NFLDataGenerator()
    
    # Number of games to generate (default is 256, a bit less than a full NFL season)
    num_games = 100  # Reduced for faster execution
    
    # Generate play data
    plays = generator.generate_season_data(num_games)
    
    if plays and len(plays) > 0:
        # Save to CSV
        csv_file = generator.save_plays_to_csv(plays)
        
        print("\nExtracting play-calling tendencies...")
        try:
            tendencies = generator.extract_play_tendencies(plays)
            generator.save_tendencies(tendencies)
            print(f"✓ Successfully extracted tendencies:")
            
            # Display a sample of the tendencies
            for down in tendencies:
                print(f"  Down {down}: {tendencies[down]['pass_percentage']:.1f}% pass, {tendencies[down]['run_percentage']:.1f}% run")
        except Exception as e:
            print(f"Error extracting tendencies: {str(e)}")
        
        print("\nExtracting play outcomes...")
        try:
            outcomes = generator.extract_play_outcomes(plays)
            generator.save_outcomes(outcomes)
            
            # Display a sample of the outcomes
            for play_type in outcomes:
                print(f"  {play_type.capitalize()}: avg gain {outcomes[play_type]['yards_mean']:.2f} yards, success rate {outcomes[play_type]['success_rate']:.1f}%")
            print("✓ Successfully extracted play outcomes")
        except Exception as e:
            print(f"Error extracting outcomes: {str(e)}")
        
        # Show where files are saved
        data_dir = generator.data_dir
        print(f"\nNFL data generation complete. Data saved to:")
        print(f"  {csv_file}")
        print(f"  {os.path.join(data_dir, 'play_tendencies.json')}")
        print(f"  {os.path.join(data_dir, 'play_outcomes.json')}")
        print("\nNote: This data is synthetic but follows realistic NFL statistical patterns")
    else:
        print("\n✗ Failed to generate NFL data.")

if __name__ == "__main__":
    start_time = time.time()
    try:
        main()
    except Exception as e:
        print(f"\nError in main program: {str(e)}")
    elapsed_time = time.time() - start_time
    print(f"\nGeneration completed in {elapsed_time:.1f} seconds")