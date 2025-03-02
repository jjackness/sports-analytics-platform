from nfl_data_collector import NFLDataCollector

def main():
    # Create a data collector
    collector = NFLDataCollector()
    
    # Try different seasons in case the most recent isn't available
    seasons_to_try = [2022, 2021, 2020]
    
    df = None
    for season in seasons_to_try:
        df = collector.load_season_data(season)
        if df is not None:
            print(f"Successfully loaded {season} season data")
            break
    
    if df is not None:
        # Extract tendencies
        tendencies = collector.extract_play_tendencies(df)
        collector.save_tendencies(tendencies)
        
        # Extract play outcomes
        outcomes = collector.extract_play_outcomes(df)
        collector.save_outcomes(outcomes)
        
        print("NFL data processing complete. Check the data/nfl_data directory for results.")
    else:
        print("Failed to load NFL data for any season.")

if __name__ == "__main__":
    main()