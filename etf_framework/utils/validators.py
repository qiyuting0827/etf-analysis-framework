"""
Data validation utilities
"""

import pandas as pd
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validate data quality and format
    """
    
    @staticmethod
    def validate_ohlcv(data: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate OHLCV data format
        
        Args:
            data: Input data
            
        Returns:
            Tuple of (is_valid, message)
        """
        required_columns = {'open', 'high', 'low', 'close', 'volume'}
        
        if not isinstance(data, pd.DataFrame):
            return False, "Data must be a pandas DataFrame"
        
        if data.empty:
            return False, "Data is empty"
        
        # Check columns
        data_columns = set(col.lower() for col in data.columns)
        if not required_columns.issubset(data_columns):
            missing = required_columns - data_columns
            return False, f"Missing columns: {missing}"
        
        # Check data types
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            col_lower = col.lower()
            if data_columns.__contains__(col_lower):
                if not pd.api.types.is_numeric_dtype(data[col_lower]):
                    return False, f"{col} must be numeric"
        
        # Check for NaN values
        if data[list(required_columns)].isnull().any().any():
            return False, "Data contains NaN values"
        
        # Check price relationships
        data_lower = data.copy()
        data_lower.columns = [col.lower() for col in data_lower.columns]
        
        if (data_lower['high'] < data_lower['low']).any():
            return False, "High price must be >= low price"
        
        if (data_lower['high'] < data_lower['close']).any():
            return False, "High price must be >= close price"
        
        if (data_lower['low'] > data_lower['close']).any():
            return False, "Low price must be <= close price"
        
        return True, "Data validation passed"
    
    @staticmethod
    def validate_parameters(params: dict, param_space: dict) -> Tuple[bool, str]:
        """
        Validate parameters against parameter space
        
        Args:
            params: Parameters to validate
            param_space: Parameter space definition
            
        Returns:
            Tuple of (is_valid, message)
        """
        for param_name, param_value in params.items():
            if param_name not in param_space:
                return False, f"Unknown parameter: {param_name}"
            
            valid_values = param_space[param_name]
            if isinstance(valid_values, (list, tuple)):
                if param_value not in valid_values:
                    return False, f"{param_name} value {param_value} not in {valid_values}"
            elif isinstance(valid_values, dict) and 'min' in valid_values and 'max' in valid_values:
                min_val = valid_values['min']
                max_val = valid_values['max']
                if not (min_val <= param_value <= max_val):
                    return False, f"{param_name} value {param_value} out of range [{min_val}, {max_val}]"
        
        return True, "Parameter validation passed"
