# data_processing/data_export.py
import pandas as pd
import json
import os
import numpy as np
from typing import Dict, List, Any, Optional
import pickle

# Custom JSON encoder to handle NumPy data types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

class DataExporter:
    """
    Handles exporting processed data for use in the simulation engine.
    """
    
    def __init__(self, output_dir: str = "results"):
        """Initialize with path to output directory."""
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def export_csv(self, data: pd.DataFrame, filename: str, **kwargs) -> str:
        """
        Export DataFrame to CSV.
        
        Args:
            data: DataFrame to export
            filename: Name of the output file
            **kwargs: Additional arguments to pass to DataFrame.to_csv
            
        Returns:
            Path to the exported file
        """
        # Make sure filename has .csv extension
        if not filename.endswith('.csv'):
            filename = f"{filename}.csv"
        
        # Create full path
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            data.to_csv(output_path, **kwargs)
            print(f"Data exported to {output_path}")
            return output_path
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return ""
    
    def export_json(self, data: Dict, filename: str, **kwargs) -> str:
        """
        Export dictionary to JSON.
        
        Args:
            data: Dictionary to export
            filename: Name of the output file
            **kwargs: Additional arguments to pass to json.dump
            
        Returns:
            Path to the exported file
        """
        # Make sure filename has .json extension
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        # Create full path
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            with open(output_path, 'w') as f:
                json.dump(data, f, cls=NumpyEncoder, **kwargs)
            print(f"Data exported to {output_path}")
            return output_path
        except Exception as e:
            print(f"Error exporting JSON: {e}")
            return ""
    
    def export_simulation_params(self, params: Dict, filename: str = "simulation_params.json") -> str:
        """
        Export simulation parameters in a format readable by the simulation engine.
        
        Args:
            params: Dictionary of simulation parameters
            filename: Name of the output file
            
        Returns:
            Path to the exported file
        """
        # Add timestamp
        import datetime
        params['exported_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Export as JSON
        return self.export_json(params, filename, indent=4)
    
    def export_model(self, model: Any, filename: str) -> str:
        """
        Export a trained model using pickle.
        
        Args:
            model: Model object to export
            filename: Name of the output file
            
        Returns:
            Path to the exported file
        """
        # Make sure filename has .pkl extension
        if not filename.endswith('.pkl'):
            filename = f"{filename}.pkl"
        
        # Create full path
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            with open(output_path, 'wb') as f:
                pickle.dump(model, f)
            print(f"Model exported to {output_path}")
            return output_path
        except Exception as e:
            print(f"Error exporting model: {e}")
            return ""