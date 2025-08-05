"""
Carbon Footprint Calculator for RAG Project

This module provides carbon footprint calculation capabilities inspired by CO2.js
for estimating the environmental impact of digital services and AI operations.

Based on research from:
- CO2.js (thegreenwebfoundation/co2.js)
- GenAI Carbon Footprint (greenscale-ai/genai-carbon-footprint)
- Cloud Carbon Footprint methodologies
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnergySource(Enum):
    """Energy source types for carbon intensity calculation"""
    RENEWABLE = "renewable"
    GRID_AVERAGE = "grid_average"
    COAL = "coal"
    NATURAL_GAS = "natural_gas"
    NUCLEAR = "nuclear"


class ServiceType(Enum):
    """Types of digital services for carbon calculation"""
    WEB_REQUEST = "web_request"
    DATA_TRANSFER = "data_transfer"
    AI_INFERENCE = "ai_inference"
    DATABASE_QUERY = "database_query"
    STORAGE = "storage"
    COMPUTE = "compute"


@dataclass
class CarbonEmission:
    """Data class for carbon emission results"""
    service_type: ServiceType
    co2_grams: float
    energy_kwh: float
    timestamp: datetime
    metadata: Dict = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['service_type'] = self.service_type.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


class CarbonCalculator:
    """
    Carbon footprint calculator for digital services and AI operations
    
    This calculator estimates CO2 emissions based on:
    - Energy consumption of digital services
    - Carbon intensity of electricity grid
    - Service-specific emission factors
    """
    
    # Carbon intensity factors (gCO2/kWh) by energy source
    CARBON_INTENSITY = {
        EnergySource.RENEWABLE: 50,      # Solar/Wind average
        EnergySource.GRID_AVERAGE: 475,  # Global average
        EnergySource.COAL: 820,          # Coal power
        EnergySource.NATURAL_GAS: 490,   # Natural gas
        EnergySource.NUCLEAR: 12,        # Nuclear power
    }
    
    # Energy consumption factors for different services
    ENERGY_FACTORS = {
        ServiceType.WEB_REQUEST: 0.0006,      # kWh per request
        ServiceType.DATA_TRANSFER: 0.000006,  # kWh per MB
        ServiceType.AI_INFERENCE: 0.002,      # kWh per inference
        ServiceType.DATABASE_QUERY: 0.0001,   # kWh per query
        ServiceType.STORAGE: 0.000004,        # kWh per GB per hour
        ServiceType.COMPUTE: 0.1,             # kWh per CPU hour
    }
    
    def __init__(self, 
                 default_energy_source: EnergySource = EnergySource.GRID_AVERAGE,
                 region: str = "global"):
        """
        Initialize carbon calculator
        
        Args:
            default_energy_source: Default energy source for calculations
            region: Geographic region for regional carbon intensity
        """
        self.default_energy_source = default_energy_source
        self.region = region
        self.calculation_history: List[CarbonEmission] = []
        
        logger.info(f"Carbon calculator initialized for region: {region}")
    
    def calculate_web_request_emissions(self, 
                                      num_requests: int,
                                      energy_source: Optional[EnergySource] = None) -> CarbonEmission:
        """
        Calculate carbon emissions for web requests
        
        Args:
            num_requests: Number of web requests
            energy_source: Energy source override
            
        Returns:
            CarbonEmission object with calculation results
        """
        energy_source = energy_source or self.default_energy_source
        
        # Calculate energy consumption
        energy_kwh = num_requests * self.ENERGY_FACTORS[ServiceType.WEB_REQUEST]
        
        # Calculate CO2 emissions
        carbon_intensity = self.CARBON_INTENSITY[energy_source]
        co2_grams = energy_kwh * carbon_intensity
        
        emission = CarbonEmission(
            service_type=ServiceType.WEB_REQUEST,
            co2_grams=co2_grams,
            energy_kwh=energy_kwh,
            timestamp=datetime.now(),
            metadata={
                "num_requests": num_requests,
                "energy_source": energy_source.value,
                "region": self.region
            }
        )
        
        self.calculation_history.append(emission)
        logger.info(f"Web requests: {num_requests} → {co2_grams:.4f}g CO2")
        
        return emission
    
    def calculate_ai_inference_emissions(self,
                                       num_inferences: int,
                                       model_size: str = "medium",
                                       energy_source: Optional[EnergySource] = None) -> CarbonEmission:
        """
        Calculate carbon emissions for AI model inferences
        
        Args:
            num_inferences: Number of AI inferences
            model_size: Model size category (small, medium, large)
            energy_source: Energy source override
            
        Returns:
            CarbonEmission object with calculation results
        """
        energy_source = energy_source or self.default_energy_source
        
        # Model size multipliers
        size_multipliers = {
            "small": 0.5,
            "medium": 1.0,
            "large": 3.0,
            "xlarge": 10.0
        }
        
        multiplier = size_multipliers.get(model_size, 1.0)
        
        # Calculate energy consumption
        base_energy = self.ENERGY_FACTORS[ServiceType.AI_INFERENCE]
        energy_kwh = num_inferences * base_energy * multiplier
        
        # Calculate CO2 emissions
        carbon_intensity = self.CARBON_INTENSITY[energy_source]
        co2_grams = energy_kwh * carbon_intensity
        
        emission = CarbonEmission(
            service_type=ServiceType.AI_INFERENCE,
            co2_grams=co2_grams,
            energy_kwh=energy_kwh,
            timestamp=datetime.now(),
            metadata={
                "num_inferences": num_inferences,
                "model_size": model_size,
                "energy_source": energy_source.value,
                "region": self.region
            }
        )
        
        self.calculation_history.append(emission)
        logger.info(f"AI inferences: {num_inferences} ({model_size}) → {co2_grams:.4f}g CO2")
        
        return emission
    
    def calculate_data_transfer_emissions(self,
                                        data_mb: float,
                                        energy_source: Optional[EnergySource] = None) -> CarbonEmission:
        """
        Calculate carbon emissions for data transfer
        
        Args:
            data_mb: Amount of data transferred in MB
            energy_source: Energy source override
            
        Returns:
            CarbonEmission object with calculation results
        """
        energy_source = energy_source or self.default_energy_source
        
        # Calculate energy consumption
        energy_kwh = data_mb * self.ENERGY_FACTORS[ServiceType.DATA_TRANSFER]
        
        # Calculate CO2 emissions
        carbon_intensity = self.CARBON_INTENSITY[energy_source]
        co2_grams = energy_kwh * carbon_intensity
        
        emission = CarbonEmission(
            service_type=ServiceType.DATA_TRANSFER,
            co2_grams=co2_grams,
            energy_kwh=energy_kwh,
            timestamp=datetime.now(),
            metadata={
                "data_mb": data_mb,
                "energy_source": energy_source.value,
                "region": self.region
            }
        )
        
        self.calculation_history.append(emission)
        logger.info(f"Data transfer: {data_mb}MB → {co2_grams:.4f}g CO2")
        
        return emission
    
    def calculate_storage_emissions(self,
                                  storage_gb: float,
                                  hours: float = 1.0,
                                  energy_source: Optional[EnergySource] = None) -> CarbonEmission:
        """
        Calculate carbon emissions for data storage
        
        Args:
            storage_gb: Amount of storage in GB
            hours: Duration of storage in hours
            energy_source: Energy source override
            
        Returns:
            CarbonEmission object with calculation results
        """
        energy_source = energy_source or self.default_energy_source
        
        # Calculate energy consumption
        energy_kwh = storage_gb * hours * self.ENERGY_FACTORS[ServiceType.STORAGE]
        
        # Calculate CO2 emissions
        carbon_intensity = self.CARBON_INTENSITY[energy_source]
        co2_grams = energy_kwh * carbon_intensity
        
        emission = CarbonEmission(
            service_type=ServiceType.STORAGE,
            co2_grams=co2_grams,
            energy_kwh=energy_kwh,
            timestamp=datetime.now(),
            metadata={
                "storage_gb": storage_gb,
                "hours": hours,
                "energy_source": energy_source.value,
                "region": self.region
            }
        )
        
        self.calculation_history.append(emission)
        logger.info(f"Storage: {storage_gb}GB for {hours}h → {co2_grams:.4f}g CO2")
        
        return emission
    
    def get_total_emissions(self) -> Dict:
        """
        Get total emissions across all calculations
        
        Returns:
            Dictionary with total emissions summary
        """
        if not self.calculation_history:
            return {
                "total_co2_grams": 0.0,
                "total_energy_kwh": 0.0,
                "calculation_count": 0,
                "by_service_type": {}
            }
        
        total_co2 = sum(emission.co2_grams for emission in self.calculation_history)
        total_energy = sum(emission.energy_kwh for emission in self.calculation_history)
        
        # Group by service type
        by_service = {}
        for emission in self.calculation_history:
            service_name = emission.service_type.value
            if service_name not in by_service:
                by_service[service_name] = {
                    "co2_grams": 0.0,
                    "energy_kwh": 0.0,
                    "count": 0
                }
            by_service[service_name]["co2_grams"] += emission.co2_grams
            by_service[service_name]["energy_kwh"] += emission.energy_kwh
            by_service[service_name]["count"] += 1
        
        return {
            "total_co2_grams": total_co2,
            "total_energy_kwh": total_energy,
            "calculation_count": len(self.calculation_history),
            "by_service_type": by_service,
            "equivalent_tree_months": total_co2 / 21000,  # Trees absorb ~21kg CO2/year
            "equivalent_car_meters": total_co2 / 0.12     # Cars emit ~120g CO2/km
        }
    
    def export_history(self, filename: Optional[str] = None) -> str:
        """
        Export calculation history to JSON file
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            JSON string of calculation history
        """
        history_data = {
            "calculator_config": {
                "default_energy_source": self.default_energy_source.value,
                "region": self.region
            },
            "calculations": [emission.to_dict() for emission in self.calculation_history],
            "summary": self.get_total_emissions(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        json_str = json.dumps(history_data, indent=2)
        
        if filename:
            with open(filename, 'w') as f:
                f.write(json_str)
            logger.info(f"History exported to {filename}")
        
        return json_str
    
    def reset_history(self):
        """Reset calculation history"""
        self.calculation_history.clear()
        logger.info("Calculation history reset")


# Convenience functions for quick calculations
def quick_web_request_carbon(num_requests: int, 
                           energy_source: EnergySource = EnergySource.GRID_AVERAGE) -> float:
    """Quick calculation for web request carbon emissions"""
    calc = CarbonCalculator(energy_source)
    return calc.calculate_web_request_emissions(num_requests).co2_grams


def quick_ai_inference_carbon(num_inferences: int,
                            model_size: str = "medium",
                            energy_source: EnergySource = EnergySource.GRID_AVERAGE) -> float:
    """Quick calculation for AI inference carbon emissions"""
    calc = CarbonCalculator(energy_source)
    return calc.calculate_ai_inference_emissions(num_inferences, model_size).co2_grams


def quick_data_transfer_carbon(data_mb: float,
                             energy_source: EnergySource = EnergySource.GRID_AVERAGE) -> float:
    """Quick calculation for data transfer carbon emissions"""
    calc = CarbonCalculator(energy_source)
    return calc.calculate_data_transfer_emissions(data_mb).co2_grams


# Example usage and demonstration
if __name__ == "__main__":
    print("🌱 Carbon Footprint Calculator for RAG Project")
    print("=" * 50)
    
    # Initialize calculator
    calculator = CarbonCalculator(
        default_energy_source=EnergySource.GRID_AVERAGE,
        region="global"
    )
    
    # Example calculations
    print("\n📊 Example Calculations:")
    
    # Web requests
    web_emission = calculator.calculate_web_request_emissions(1000)
    print(f"1000 web requests: {web_emission.co2_grams:.4f}g CO2")
    
    # AI inferences
    ai_emission = calculator.calculate_ai_inference_emissions(50, "large")
    print(f"50 large AI inferences: {ai_emission.co2_grams:.4f}g CO2")
    
    # Data transfer
    data_emission = calculator.calculate_data_transfer_emissions(500)
    print(f"500MB data transfer: {data_emission.co2_grams:.4f}g CO2")
    
    # Storage
    storage_emission = calculator.calculate_storage_emissions(100, 24)
    print(f"100GB storage for 24h: {storage_emission.co2_grams:.4f}g CO2")
    
    # Total summary
    print("\n📈 Total Emissions Summary:")
    summary = calculator.get_total_emissions()
    print(f"Total CO2: {summary['total_co2_grams']:.4f}g")
    print(f"Total Energy: {summary['total_energy_kwh']:.6f} kWh")
    print(f"Equivalent to {summary['equivalent_tree_months']:.2f} tree-months of CO2 absorption")
    print(f"Equivalent to {summary['equivalent_car_meters']:.1f} meters of car driving")
    
    # Export example
    print("\n💾 Exporting calculation history...")
    json_export = calculator.export_history()
    print("History exported successfully!")
    
    print("\n🌍 Carbon footprint calculation complete!")