# data_processing/data_analysis.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns

class PlayByPlayAnalyzer:
    """
    Analyzes play-by-play data to extract patterns and probabilities
    for use in the simulation engine.
    """
    
    def __init__(self, pbp_data: Optional[pd.DataFrame] = None):
        """Initialize with optional play-by-play data."""
        self.pbp_data = pbp_data
    
    def load_data(self, pbp_data: pd.DataFrame):
        """Load play-by-play data for analysis."""
        self.pbp_data = pbp_data
    
    def analyze_play_calling(self, team: Optional[str] = None) -> pd.DataFrame:
        """
        Analyze play-calling tendencies by down and distance.
        
        Args:
            team: Optional team abbreviation to filter by
            
        Returns:
            DataFrame with play call percentages by situation
        """
        if self.pbp_data is None:
            print("No data loaded. Please load data first.")
            return pd.DataFrame()
        
        # Create a copy to avoid modifying the original
        df = self.pbp_data.copy()
        
        # Filter by team if specified
        if team:
            df = df[df['posteam'] == team]
        
        # Check if we have required columns
        required_cols = ['down', 'ydstogo', 'play_type']
        if not all(col in df.columns for col in required_cols):
            print(f"Missing required columns. Need: {required_cols}")
            return pd.DataFrame()
        
        # Group by down, distance buckets, and play type
        try:
            # Create distance buckets
            df['distance_bucket'] = pd.cut(
                df['ydstogo'], 
                bins=[0, 2, 5, 10, 15, 100],
                labels=['Short (1-2)', 'Medium (3-5)', 'Standard (6-10)', 'Long (11-15)', 'Very Long (16+)']
            )
            
            # Group and calculate percentages
            play_call_counts = df.groupby(['down', 'distance_bucket', 'play_type']).size().unstack(fill_value=0)
            play_call_pct = play_call_counts.div(play_call_counts.sum(axis=1), axis=0) * 100
            
            return play_call_pct.round(2)
        except Exception as e:
            print(f"Error analyzing play calling: {e}")
            return pd.DataFrame()
    
    def analyze_play_outcomes(self, play_type: str = 'run') -> Dict:
        """
        Analyze the distribution of outcomes for a specific play type.
        
        Args:
            play_type: Type of play ('run', 'pass', etc.)
            
        Returns:
            Dictionary with outcome statistics
        """
        if self.pbp_data is None:
            print("No data loaded. Please load data first.")
            return {}
        
        # Create a copy and filter to the play type
        df = self.pbp_data.copy()
        df = df[df['play_type'] == play_type]
        
        # Check if we have yards gained column
        if 'yards_gained' not in df.columns:
            print("Missing required column: yards_gained")
            return {}
        
        # Calculate statistics
        try:
            stats = {
                'mean': df['yards_gained'].mean(),
                'median': df['yards_gained'].median(),
                'std': df['yards_gained'].std(),
                'min': df['yards_gained'].min(),
                'max': df['yards_gained'].max(),
                'percentile_25': df['yards_gained'].quantile(0.25),
                'percentile_75': df['yards_gained'].quantile(0.75),
                'success_rate': (df['yards_gained'] >= df['ydstogo']).mean() * 100,
                'touchdown_rate': df['touchdown'].mean() * 100 if 'touchdown' in df.columns else None,
                'turnover_rate': df['turnover'].mean() * 100 if 'turnover' in df.columns else None,
                'sample_size': len(df)
            }
            
            return stats
        except Exception as e:
            print(f"Error analyzing play outcomes: {e}")
            return {}
    
    def plot_yards_distribution(self, play_type: str = 'run', save_path: Optional[str] = None):
        """
        Plot the distribution of yards gained for a specific play type.
        
        Args:
            play_type: Type of play ('run', 'pass', etc.)
            save_path: Optional path to save the plot
        """
        if self.pbp_data is None:
            print("No data loaded. Please load data first.")
            return
        
        # Filter to play type
        df = self.pbp_data[self.pbp_data['play_type'] == play_type]
        
        # Check if we have data
        if len(df) == 0:
            print(f"No data for play type: {play_type}")
            return
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        sns.histplot(df['yards_gained'], kde=True, bins=30)
        plt.title(f'Distribution of Yards Gained - {play_type.capitalize()} Plays')
        plt.xlabel('Yards Gained')
        plt.ylabel('Frequency')
        
        # Add vertical lines for key statistics
        plt.axvline(df['yards_gained'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {df["yards_gained"].mean():.2f}')
        plt.axvline(df['yards_gained'].median(), color='green', linestyle='-', 
                   label=f'Median: {df["yards_gained"].median():.2f}')
        
        plt.legend()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
        
        plt.show()