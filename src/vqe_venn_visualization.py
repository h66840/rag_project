"""
VQE Venn Diagram Visualization
This script creates a Venn diagram to visualize the resource requirements
comparison between basic and optimized VQE implementations.
"""

import sys
import os
import json
from typing import Dict, List

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vqe_comparison import VQEComparison

def create_venn_diagram_data() -> Dict:
    """
    Create and run VQE comparison to generate Venn diagram data
    """
    print("Generating VQE comparison data...")
    
    # Run the comparison
    comparison = VQEComparison()
    results = comparison.run_comparison([4, 6, 8])
    
    # Generate Venn diagram data
    venn_data = comparison.generate_venn_data()
    
    return venn_data

def prepare_chart_data(venn_data: Dict) -> List[Dict]:
    """
    Prepare data in the format required for the Venn chart generation
    """
    chart_data = []
    
    # Process the Venn data to create proper chart format
    for item in venn_data['venn_data']:
        chart_data.append({
            'label': item['label'],
            'value': item['value'],
            'sets': item['sets']
        })
    
    return chart_data

def main():
    """
    Main function to create VQE resource comparison Venn diagram
    """
    print("VQE Resource Requirements Comparison - Venn Diagram")
    print("=" * 60)
    
    # Generate comparison data
    venn_data = create_venn_diagram_data()
    
    # Prepare chart data
    chart_data = prepare_chart_data(venn_data)
    
    print(f"\nVenn Diagram Data Summary:")
    print(f"Total data points: {len(chart_data)}")
    print(f"Basic VQE unique resources: {len(venn_data['basic_only'])}")
    print(f"Optimized VQE unique resources: {len(venn_data['optimized_only'])}")
    print(f"Shared resources: {len(venn_data['intersection'])}")
    
    # Display the data that will be used for the Venn diagram
    print(f"\nDetailed Resource Analysis:")
    print(f"\nBasic VQE Only Resources:")
    for resource in venn_data['basic_only']:
        print(f"  - {resource}")
    
    print(f"\nOptimized VQE Only Resources:")
    for resource in venn_data['optimized_only']:
        print(f"  - {resource}")
    
    print(f"\nShared Resources:")
    for resource in venn_data['intersection']:
        print(f"  - {resource}")
    
    return chart_data, venn_data

if __name__ == "__main__":
    chart_data, venn_data = main()
    
    # The chart_data is now ready to be used with the Venn chart generation tool
    print(f"\nChart data prepared for Venn diagram generation.")
    print(f"Data format: {chart_data[:2]}...")  # Show first 2 items as example