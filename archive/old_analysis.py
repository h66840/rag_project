#!/usr/bin/env python3
"""
Legacy Analysis Script - DEPRECATED
====================================

This script contains old analysis functions that are no longer maintained.
It has been replaced by newer, more efficient analysis modules.

Created: 2023-01-15
Deprecated: 2024-12-20
Reason: Performance issues and outdated dependencies

TODO: Remove after migration to new analysis framework is complete.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.warn("This script is deprecated. Use the new analysis modules instead.", 
              DeprecationWarning, stacklevel=2)

class LegacyAnalyzer:
    """
    Legacy data analyzer - DO NOT USE IN NEW CODE
    """
    
    def __init__(self, data_path=None):
        self.data_path = data_path
        self.data = None
        print("WARNING: Using deprecated LegacyAnalyzer class")
    
    def load_data(self, file_path):
        """Load data from CSV file - DEPRECATED"""
        try:
            self.data = pd.read_csv(file_path)
            print(f"Loaded {len(self.data)} records from {file_path}")
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
        return True
    
    def basic_stats(self):
        """Calculate basic statistics - DEPRECATED"""
        if self.data is None:
            print("No data loaded")
            return None
        
        stats = {
            'count': len(self.data),
            'columns': list(self.data.columns),
            'memory_usage': self.data.memory_usage(deep=True).sum(),
            'null_counts': self.data.isnull().sum().to_dict()
        }
        
        return stats
    
    def correlation_matrix(self):
        """Generate correlation matrix - DEPRECATED"""
        if self.data is None:
            return None
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            print("No numeric columns found")
            return None
        
        return self.data[numeric_cols].corr()
    
    def export_results(self, output_path):
        """Export analysis results - DEPRECATED"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.basic_stats(),
            'correlation': self.correlation_matrix().to_dict() if self.correlation_matrix() is not None else None
        }
        
        # This is inefficient - should use proper JSON serialization
        with open(output_path, 'w') as f:
            f.write(str(results))
        
        print(f"Results exported to {output_path}")

def run_legacy_analysis(input_file, output_file):
    """
    Main function to run legacy analysis - DEPRECATED
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output results file
    """
    print("=" * 50)
    print("RUNNING LEGACY ANALYSIS - DEPRECATED")
    print("=" * 50)
    
    analyzer = LegacyAnalyzer()
    
    if not analyzer.load_data(input_file):
        return False
    
    print("\nCalculating statistics...")
    stats = analyzer.basic_stats()
    if stats:
        print(f"Processed {stats['count']} records")
        print(f"Memory usage: {stats['memory_usage']} bytes")
    
    print("\nCalculating correlations...")
    corr_matrix = analyzer.correlation_matrix()
    if corr_matrix is not None:
        print(f"Correlation matrix shape: {corr_matrix.shape}")
    
    print("\nExporting results...")
    analyzer.export_results(output_file)
    
    print("\nLegacy analysis complete!")
    print("WARNING: Please migrate to new analysis framework")
    
    return True

if __name__ == "__main__":
    # Example usage - DO NOT USE IN PRODUCTION
    print("This is a deprecated script!")
    print("Please use the new analysis modules instead.")
    
    # Uncomment to run (NOT RECOMMENDED)
    # run_legacy_analysis("data/sample.csv", "results/legacy_output.txt")