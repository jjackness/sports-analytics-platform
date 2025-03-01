# data_processing/data_import.py
import pandas as pd
import os
import requests
from typing import List, Dict, Optional, Union
import json

class DataImporter:
    """
    Handles importing NFL data from various sources including:
    - Local CSV files
    - Remote APIs (when implemented)
    - Cached data
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize with path to data directory."""
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def import_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Import data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            **kwargs: Additional arguments to pass to pandas.read_csv
            
        Returns:
            DataFrame containing the data
        """
        try:
            return pd.read_csv(file_path, **kwargs)
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return pd.DataFrame()
    
    def download_and_cache_data(self, url: str, cache_file: str, force_refresh: bool = False) -> pd.DataFrame:
        """
        Download data from a URL and cache it locally.
        
        Args:
            url: URL to download data from
            cache_file: Local file path to cache the data
            force_refresh: Whether to force a download even if cache exists
            
        Returns:
            DataFrame containing the data
        """
        # Check if cache exists and we're not forcing a refresh
        cache_path = os.path.join(self.data_dir, cache_file)
        if os.path.exists(cache_path) and not force_refresh:
            print(f"Loading cached data from {cache_path}")
            return self.import_csv(cache_path)
        
        # Download data
        try:
            print(f"Downloading data from {url}")
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Save to cache
            with open(cache_path, 'wb') as f:
                f.write(response.content)
                
            # Return as DataFrame
            return pd.read_csv(cache_path)
        except Exception as e:
            print(f"Error downloading data: {e}")
            return pd.DataFrame()
    
    # Future methods for API integrations
    def import_nflfastr_data(self, seasons: List[int], force_refresh: bool = False):
        """
        Placeholder for future integration with nflfastR data.
        This would download play-by-play data for specified seasons.
        
        For now, this method will print an info message as we haven't 
        implemented the actual API integration yet.
        """
        print(f"This method will import play-by-play data for seasons: {seasons}")
        print("This feature is not implemented yet.")
        print("You'll need to install the nfl_data_py package when we implement it.")