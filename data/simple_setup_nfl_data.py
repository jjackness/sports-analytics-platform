"""
Simple NFL Data Setup Script

This script:
1. Creates the NFL data collector
2. Downloads play-by-play data for recent NFL seasons
3. Extracts play tendencies and outcomes from the data
4. Saves the processed data to JSON files for use in simulations

No special packages are required beyond the Python standard library.
"""

import os
import time
import sys
from simple_nfl_data_collector import SimpleNFLDataCollector

def main():
    # Create a data collector
    print("Creating NFL data collector...")
    collector = SimpleNFLDataCollector()
    
    # Try different seasons in case the most recent isn't available
    seasons_to_try = [2022, 2021, 2020, 2019, 2018]
    
    print("\nAttempting to download NFL play-by-play data...")
    plays = None
    for season in seasons_to_try:
        print(f"\nTrying season {season}...")
        plays = collector.load_season_data(season)
        if plays and len(plays) > 0:
            print(f"✓ Successfully loaded {season} NFL season data with {len(plays)} plays")
            
            # Display sample play
            if plays:
                sample_play = plays[0]
                print(f"\nSample play data (first of {len(plays)} plays):")
                sample_keys = ['play_id', 'play_type', 'down', 'ydstogo', 'yards_gained']
                sample_data = {k: sample_play.get(k, 'N/A') for k in sample_keys if k in sample_play}
                for k, v in sample_data.items():
                    print(f"  {k}: {v}")
            break
        else:
            print(f"✗ Failed to load {season} data")
    
    if plays and len(plays) > 0:
        print("\nExtracting play-calling tendencies...")
        try:
            tendencies = collector.extract_play_tendencies(plays)
            collector.save_tendencies(tendencies)
            print(f"✓ Successfully extracted tendencies:")
            
            # Display a sample of the tendencies
            for down in tendencies:
                print(f"  Down {down}: {tendencies[down]['pass_percentage']:.1f}% pass, {tendencies[down]['run_percentage']:.1f}% run")
        except Exception as e:
            print(f"Error extracting tendencies: {str(e)}")
        
        print("\nExtracting play outcomes...")
        try:
            outcomes = collector.extract_play_outcomes(plays)
            collector.save_outcomes(outcomes)
            
            # Display a sample of the outcomes
            for play_type in outcomes:
                print(f"  {play_type.capitalize()}: avg gain {outcomes[play_type]['yards_mean']:.2f} yards, success rate {outcomes[play_type]['success_rate']:.1f}%")
            print("✓ Successfully extracted play outcomes")
        except Exception as e:
            print(f"Error extracting outcomes: {str(e)}")
        
        # Show where files are saved
        data_dir = collector.data_dir
        print(f"\nNFL data processing complete. Data saved to:")
        print(f"  {os.path.join(data_dir, 'play_tendencies.json')}")
        print(f"  {os.path.join(data_dir, 'play_outcomes.json')}")
    else:
        print("\n✗ Failed to load NFL data for any season.")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    start_time = time.time()
    try:
        main()
    except Exception as e:
        print(f"\nError in main program: {str(e)}")
    elapsed_time = time.time() - start_time
    print(f"\nSetup completed in {elapsed_time:.1f} seconds")