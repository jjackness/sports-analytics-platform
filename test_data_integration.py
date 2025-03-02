"""
Test Data Integration

This script tests the integration of NFL statistical data with the simulation engine.
It runs a series of test plays to verify that the data is being used correctly.
"""

import os
import sys
import json
from collections import defaultdict

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the data provider
from data.nfl_data_provider import NFLDataProvider

def test_data_loading():
    """Test that the data provider can load data"""
    print("Testing data loading...")
    provider = NFLDataProvider()
    success = provider.load_data()
    
    if success:
        print("✓ Data loaded successfully")
        
        # Print some statistics to verify
        print("\nPlay-calling tendencies:")
        for down in provider.tendencies:
            print(f"  Down {down}: {provider.tendencies[down]['pass_percentage']:.1f}% pass, "
                  f"{provider.tendencies[down]['run_percentage']:.1f}% run")
        
        print("\nPlay outcomes:")
        for play_type in provider.outcomes:
            print(f"  {play_type.capitalize()}: avg gain {provider.outcomes[play_type]['yards_mean']:.2f} yards, "
                  f"success rate {provider.outcomes[play_type]['success_rate']:.1f}%")
    else:
        print("✗ Failed to load data")
    
    return success

def test_play_type_selection():
    """Test the play type selection logic"""
    print("\nTesting play type selection...")
    provider = NFLDataProvider()
    provider.load_data()
    
    # Run 1000 simulations for each down and distance combination
    results = defaultdict(lambda: defaultdict(int))
    
    # Test combinations
    situations = [
        (1, 10),  # 1st and 10
        (2, 5),   # 2nd and 5
        (3, 3),   # 3rd and 3
        (3, 8),   # 3rd and 8
        (4, 1)    # 4th and 1
    ]
    
    trials = 1000
    
    for down, distance in situations:
        key = f"{down}_{distance}"
        
        for _ in range(trials):
            play_type = provider.get_play_type(down, distance)
            results[key][play_type] += 1
    
    # Print results
    print(f"Results after {trials} trials per situation:")
    for situation, counts in results.items():
        down, distance = situation.split('_')
        total = sum(counts.values())
        pass_pct = (counts['pass'] / total) * 100
        run_pct = (counts['run'] / total) * 100
        
        print(f"  {down}_{distance}: {pass_pct:.1f}% pass, {run_pct:.1f}% run")
    
    return True

def test_yards_gained():
    """Test the yards gained calculation"""
    print("\nTesting yards gained calculation...")
    provider = NFLDataProvider()
    provider.load_data()
    
    # Run 1000 simulations for each play type
    pass_yards = []
    run_yards = []
    
    trials = 1000
    
    for _ in range(trials):
        pass_yards.append(provider.get_yards_gained('pass'))
        run_yards.append(provider.get_yards_gained('run'))
    
    # Calculate statistics
    pass_avg = sum(pass_yards) / len(pass_yards)
    run_avg = sum(run_yards) / len(run_yards)
    
    pass_min, pass_max = min(pass_yards), max(pass_yards)
    run_min, run_max = min(run_yards), max(run_yards)
    
    # Print results
    print(f"Results after {trials} trials:")
    print(f"  Pass: avg {pass_avg:.2f} yards (range: {pass_min} to {pass_max})")
    print(f"  Run: avg {run_avg:.2f} yards (range: {run_min} to {run_max})")
    
    # Compare to expected values from the data
    expected_pass_avg = provider.outcomes['pass']['yards_mean']
    expected_run_avg = provider.outcomes['run']['yards_mean']
    
    print(f"\nComparison to expected values:")
    print(f"  Pass: {pass_avg:.2f} vs expected {expected_pass_avg:.2f}")
    print(f"  Run: {run_avg:.2f} vs expected {expected_run_avg:.2f}")
    
    return True

def main():
    """Run all tests"""
    print("=== Testing NFL Data Integration ===\n")
    
    if not test_data_loading():
        print("\nAborted testing due to data loading failure")
        return
    
    test_play_type_selection()
    test_yards_gained()
    
    print("\n=== Testing complete ===")

if __name__ == "__main__":
    main()