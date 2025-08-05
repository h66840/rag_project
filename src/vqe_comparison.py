"""
VQE Comparison Analysis
This script compares basic and optimized VQE implementations,
collecting metrics for visualization and analysis.
"""

import numpy as np
import sys
import os
from typing import Dict, List, Tuple
import json

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vqe_basic import BasicVQE, VQEMetrics
from vqe_optimized import OptimizedVQE, OptimizedVQEMetrics

class VQEComparison:
    """
    Class to compare basic and optimized VQE implementations
    """
    
    def __init__(self):
        self.results = {}
        
    def run_comparison(self, qubit_counts: List[int] = [4, 6, 8]) -> Dict:
        """
        Run comparison between basic and optimized VQE for different qubit counts
        
        Args:
            qubit_counts: List of qubit numbers to test
            
        Returns:
            Dictionary containing comparison results
        """
        results = {
            'basic_vqe': {},
            'optimized_vqe': {},
            'comparison_metrics': {}
        }
        
        for n_qubits in qubit_counts:
            print(f"\n=== Comparing VQE implementations for {n_qubits} qubits ===")
            
            # Run Basic VQE
            print("Running Basic VQE...")
            basic_vqe = BasicVQE(num_qubits=n_qubits)
            basic_metrics = basic_vqe.optimize(max_iterations=50)
            
            # Run Optimized VQE
            print("Running Optimized VQE...")
            optimized_vqe = OptimizedVQE(num_qubits=n_qubits, 
                                       use_clustering=True, 
                                       use_adapt=True)
            optimized_metrics = optimized_vqe.optimize(max_iterations=30)
            
            # Store results
            results['basic_vqe'][n_qubits] = self._metrics_to_dict(basic_metrics)
            results['optimized_vqe'][n_qubits] = self._metrics_to_dict(optimized_metrics)
            
            # Calculate comparison metrics
            comparison = self._calculate_comparison_metrics(basic_metrics, optimized_metrics)
            results['comparison_metrics'][n_qubits] = comparison
            
            # Print summary
            self._print_comparison_summary(n_qubits, basic_metrics, optimized_metrics, comparison)
        
        self.results = results
        return results
    
    def _metrics_to_dict(self, metrics) -> Dict:
        """Convert metrics object to dictionary"""
        result = {
            'num_qubits': metrics.num_qubits,
            'circuit_depth': metrics.circuit_depth,
            'num_parameters': metrics.num_parameters,
            'num_cnot_gates': metrics.num_cnot_gates,
            'execution_time': metrics.execution_time,
            'iterations': metrics.iterations,
            'final_energy': metrics.energy_convergence[-1] if metrics.energy_convergence else 0
        }
        
        # Add optimized-specific metrics if available
        if hasattr(metrics, 'qubit_reduction_ratio'):
            result.update({
                'num_clusters': metrics.num_clusters,
                'cluster_sizes': metrics.cluster_sizes,
                'selected_operators': metrics.selected_operators,
                'total_operators_pool': metrics.total_operators_pool,
                'qubit_reduction_ratio': metrics.qubit_reduction_ratio,
                'depth_reduction_ratio': metrics.depth_reduction_ratio
            })
        
        return result
    
    def _calculate_comparison_metrics(self, basic: VQEMetrics, optimized: OptimizedVQEMetrics) -> Dict:
        """Calculate comparison metrics between basic and optimized VQE"""
        
        # Resource reduction calculations
        qubit_reduction = (basic.num_qubits - optimized.num_qubits) / basic.num_qubits
        depth_reduction = (basic.circuit_depth - optimized.circuit_depth) / basic.circuit_depth
        cnot_reduction = (basic.num_cnot_gates - optimized.num_cnot_gates) / basic.num_cnot_gates
        param_reduction = (basic.num_parameters - optimized.num_parameters) / basic.num_parameters
        time_improvement = (basic.execution_time - optimized.execution_time) / basic.execution_time
        
        return {
            'qubit_reduction_percent': qubit_reduction * 100,
            'depth_reduction_percent': depth_reduction * 100,
            'cnot_reduction_percent': cnot_reduction * 100,
            'parameter_reduction_percent': param_reduction * 100,
            'time_improvement_percent': time_improvement * 100,
            'energy_difference': abs(basic.energy_convergence[-1] - optimized.energy_convergence[-1]),
            'convergence_improvement': (basic.iterations - optimized.iterations) / basic.iterations * 100
        }
    
    def _print_comparison_summary(self, n_qubits: int, basic: VQEMetrics, 
                                optimized: OptimizedVQEMetrics, comparison: Dict):
        """Print comparison summary"""
        print(f"\n--- Results for {n_qubits} qubits ---")
        print(f"Basic VQE:")
        print(f"  Qubits: {basic.num_qubits}, Depth: {basic.circuit_depth}, CNOTs: {basic.num_cnot_gates}")
        print(f"  Parameters: {basic.num_parameters}, Time: {basic.execution_time:.3f}s")
        print(f"  Energy: {basic.energy_convergence[-1]:.6f}")
        
        print(f"Optimized VQE:")
        print(f"  Qubits: {optimized.num_qubits}, Depth: {optimized.circuit_depth}, CNOTs: {optimized.num_cnot_gates}")
        print(f"  Parameters: {optimized.num_parameters}, Time: {optimized.execution_time:.3f}s")
        print(f"  Energy: {optimized.energy_convergence[-1]:.6f}")
        print(f"  Clusters: {optimized.num_clusters}, Selected ops: {optimized.selected_operators}/{optimized.total_operators_pool}")
        
        print(f"Improvements:")
        print(f"  Qubit reduction: {comparison['qubit_reduction_percent']:.1f}%")
        print(f"  Depth reduction: {comparison['depth_reduction_percent']:.1f}%")
        print(f"  CNOT reduction: {comparison['cnot_reduction_percent']:.1f}%")
        print(f"  Parameter reduction: {comparison['parameter_reduction_percent']:.1f}%")
        print(f"  Time improvement: {comparison['time_improvement_percent']:.1f}%")
    
    def generate_venn_data(self) -> Dict:
        """
        Generate data for Venn diagram comparing resource requirements
        
        Returns:
            Dictionary with Venn diagram data showing overlaps and differences
            in resource requirements between basic and optimized VQE
        """
        if not self.results:
            raise ValueError("Must run comparison first")
        
        # Aggregate data across all qubit counts
        basic_resources = set()
        optimized_resources = set()
        
        # Define resource categories based on metrics
        for n_qubits, basic_data in self.results['basic_vqe'].items():
            optimized_data = self.results['optimized_vqe'][n_qubits]
            
            # Categorize resources into high/medium/low usage
            # Basic VQE resources
            if basic_data['circuit_depth'] > 50:
                basic_resources.add('High Circuit Depth')
            elif basic_data['circuit_depth'] > 20:
                basic_resources.add('Medium Circuit Depth')
            else:
                basic_resources.add('Low Circuit Depth')
                
            if basic_data['num_cnot_gates'] > 30:
                basic_resources.add('High CNOT Count')
            elif basic_data['num_cnot_gates'] > 10:
                basic_resources.add('Medium CNOT Count')
            else:
                basic_resources.add('Low CNOT Count')
                
            if basic_data['num_parameters'] > 20:
                basic_resources.add('High Parameter Count')
            elif basic_data['num_parameters'] > 10:
                basic_resources.add('Medium Parameter Count')
            else:
                basic_resources.add('Low Parameter Count')
                
            if basic_data['num_qubits'] >= n_qubits:
                basic_resources.add('Full Qubit Usage')
            
            # Optimized VQE resources
            if optimized_data['circuit_depth'] > 50:
                optimized_resources.add('High Circuit Depth')
            elif optimized_data['circuit_depth'] > 20:
                optimized_resources.add('Medium Circuit Depth')
            else:
                optimized_resources.add('Low Circuit Depth')
                
            if optimized_data['num_cnot_gates'] > 30:
                optimized_resources.add('High CNOT Count')
            elif optimized_data['num_cnot_gates'] > 10:
                optimized_resources.add('Medium CNOT Count')
            else:
                optimized_resources.add('Low CNOT Count')
                
            if optimized_data['num_parameters'] > 20:
                optimized_resources.add('High Parameter Count')
            elif optimized_data['num_parameters'] > 10:
                optimized_resources.add('Medium Parameter Count')
            else:
                optimized_resources.add('Low Parameter Count')
                
            if optimized_data['num_qubits'] >= n_qubits:
                optimized_resources.add('Full Qubit Usage')
            else:
                optimized_resources.add('Reduced Qubit Usage')
                
            # Add optimization-specific features
            optimized_resources.add('Clustering Optimization')
            optimized_resources.add('Adaptive Circuit Selection')
        
        # Calculate intersections and unique sets
        intersection = basic_resources.intersection(optimized_resources)
        basic_only = basic_resources - optimized_resources
        optimized_only = optimized_resources - basic_resources
        
        # Create Venn diagram data
        venn_data = []
        
        # Basic VQE only
        for resource in basic_only:
            venn_data.append({
                'label': resource,
                'value': 1,
                'sets': ['Basic VQE']
            })
        
        # Optimized VQE only
        for resource in optimized_only:
            venn_data.append({
                'label': resource,
                'value': 1,
                'sets': ['Optimized VQE']
            })
        
        # Intersection (both)
        for resource in intersection:
            venn_data.append({
                'label': resource,
                'value': 1,
                'sets': ['Basic VQE', 'Optimized VQE']
            })
        
        return {
            'venn_data': venn_data,
            'basic_only': list(basic_only),
            'optimized_only': list(optimized_only),
            'intersection': list(intersection),
            'summary': {
                'basic_total_resources': len(basic_resources),
                'optimized_total_resources': len(optimized_resources),
                'shared_resources': len(intersection),
                'basic_unique_resources': len(basic_only),
                'optimized_unique_resources': len(optimized_only)
            }
        }
    
    def save_results(self, filename: str = 'vqe_comparison_results.json'):
        """Save comparison results to JSON file"""
        if not self.results:
            raise ValueError("No results to save. Run comparison first.")
        
        # Include Venn data in results
        venn_data = self.generate_venn_data()
        self.results['venn_diagram_data'] = venn_data
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to {filename}")
        return filename

def main():
    """Main function to run VQE comparison"""
    print("VQE Optimization Comparison Analysis")
    print("=" * 50)
    
    # Initialize comparison
    comparison = VQEComparison()
    
    # Run comparison for different qubit counts
    qubit_counts = [4, 6, 8]
    results = comparison.run_comparison(qubit_counts)
    
    # Generate and display Venn diagram data
    print("\n=== Venn Diagram Data ===")
    venn_data = comparison.generate_venn_data()
    
    print(f"Resource Analysis Summary:")
    print(f"  Basic VQE total resources: {venn_data['summary']['basic_total_resources']}")
    print(f"  Optimized VQE total resources: {venn_data['summary']['optimized_total_resources']}")
    print(f"  Shared resources: {venn_data['summary']['shared_resources']}")
    print(f"  Basic VQE unique: {venn_data['summary']['basic_unique_resources']}")
    print(f"  Optimized VQE unique: {venn_data['summary']['optimized_unique_resources']}")
    
    print(f"\nBasic VQE only resources: {venn_data['basic_only']}")
    print(f"Optimized VQE only resources: {venn_data['optimized_only']}")
    print(f"Shared resources: {venn_data['intersection']}")
    
    # Save results
    filename = comparison.save_results()
    
    print(f"\nComparison complete! Results saved to {filename}")
    print("Use this data to create the Venn diagram visualization.")
    
    return comparison

if __name__ == "__main__":
    main()