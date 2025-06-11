"""
Thermodynamic Analyzer for Kimera SWM

Implements thermodynamic analysis and monitoring following the computational tools
specification. Focuses on energy-like quantities, entropy production, and
thermodynamic constraints in the semantic working memory system.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import math

from ..core.geoid import GeoidState


@dataclass
class ThermodynamicState:
    """Container for thermodynamic state measurements"""
    timestamp: datetime
    total_energy: float
    free_energy: float
    entropy_production: float
    temperature: float
    pressure: float
    chemical_potential: float
    work_done: float
    heat_dissipated: float
    efficiency: float
    reversibility_index: float
    landauer_cost: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class ThermodynamicCalculator:
    """
    Advanced thermodynamic calculations for semantic systems
    Following principles from statistical mechanics and information thermodynamics
    """
    
    @staticmethod
    def calculate_semantic_energy(geoids: List[GeoidState]) -> float:
        """
        Calculate total semantic energy of the system
        Based on semantic activation levels and feature interactions
        """
        if not geoids:
            return 0.0
        
        total_energy = 0.0
        
        for geoid in geoids:
            # Individual geoid energy from semantic activations
            geoid_energy = sum(value**2 for value in geoid.semantic_state.values())
            
            # Interaction energy between features (simplified)
            features = list(geoid.semantic_state.values())
            for i in range(len(features)):
                for j in range(i + 1, len(features)):
                    interaction_energy = features[i] * features[j] * 0.1  # Coupling constant
                    geoid_energy += interaction_energy
            
            total_energy += geoid_energy
        
        return total_energy
    
    @staticmethod
    def calculate_free_energy(total_energy: float, entropy: float, temperature: float) -> float:
        """
        Calculate Helmholtz free energy: F = U - TS
        Where U is internal energy, T is temperature, S is entropy
        """
        return total_energy - temperature * entropy
    
    @staticmethod
    def calculate_semantic_temperature(geoids: List[GeoidState]) -> float:
        """
        Calculate semantic temperature based on energy fluctuations
        Higher temperature indicates more random/chaotic semantic states
        """
        if len(geoids) < 2:
            return 1.0  # Default temperature
        
        # Calculate energy variance as temperature indicator
        energies = []
        for geoid in geoids:
            energy = sum(value**2 for value in geoid.semantic_state.values())
            energies.append(energy)
        
        energy_variance = np.var(energies)
        mean_energy = np.mean(energies)
        
        # Temperature proportional to relative energy fluctuations
        if mean_energy > 0:
            temperature = energy_variance / mean_energy
        else:
            temperature = 1.0
        
        return max(temperature, 0.1)  # Minimum temperature
    
    @staticmethod
    def calculate_semantic_pressure(geoids: List[GeoidState], vault_capacity: int) -> float:
        """
        Calculate semantic pressure based on information density
        Higher pressure indicates system approaching capacity limits
        """
        if vault_capacity <= 0:
            return 0.0
        
        # Information content as "volume"
        total_information = 0.0
        for geoid in geoids:
            # Information content from semantic state complexity
            info_content = len(geoid.semantic_state) + sum(geoid.semantic_state.values())
            total_information += info_content
        
        # Pressure = Information / Available_Capacity
        pressure = total_information / vault_capacity
        
        return pressure
    
    @staticmethod
    def calculate_landauer_cost(bit_erasures: int, temperature: float) -> float:
        """
        Calculate Landauer cost for information erasure
        Minimum energy cost = k_B * T * ln(2) per bit erased
        """
        k_b = 1.380649e-23  # Boltzmann constant (J/K)
        ln_2 = 0.693147  # ln(2)
        
        # For semantic systems, use normalized units
        normalized_k_b = 1.0  # Normalized Boltzmann constant
        
        return bit_erasures * normalized_k_b * temperature * ln_2
    
    @staticmethod
    def calculate_entropy_production_rate(entropy_before: float, entropy_after: float, 
                                        time_delta: float) -> float:
        """
        Calculate entropy production rate (dS/dt)
        Positive values indicate irreversible processes
        """
        if time_delta <= 0:
            return 0.0
        
        entropy_change = entropy_after - entropy_before
        return entropy_change / time_delta
    
    @staticmethod
    def calculate_work_and_heat(energy_before: float, energy_after: float,
                              entropy_before: float, entropy_after: float,
                              temperature: float) -> Tuple[float, float]:
        """
        Calculate work done and heat dissipated in semantic transformation
        Based on first law of thermodynamics: dU = Q - W
        """
        energy_change = energy_after - energy_before
        entropy_change = entropy_after - entropy_before
        
        # Heat associated with entropy change
        heat = temperature * entropy_change
        
        # Work from energy balance
        work = heat - energy_change
        
        return work, heat


class ThermodynamicAnalyzer:
    """
    Comprehensive thermodynamic analysis for Kimera SWM
    
    Monitors energy flows, entropy production, and thermodynamic constraints
    in the semantic working memory system.
    """
    
    def __init__(self, history_size: int = 1000, vault_capacity: int = 10000):
        self.history_size = history_size
        self.vault_capacity = vault_capacity
        self.states: deque = deque(maxlen=history_size)
        self.logger = logging.getLogger(__name__)
        
        # Previous state for calculating changes
        self.previous_state: Optional[ThermodynamicState] = None
        
        # System parameters
        self.coupling_strength = 0.1  # Interaction coupling
        self.thermal_reservoir_temp = 1.0  # Background temperature
        
        # Tracking variables
        self.total_work_done = 0.0
        self.total_heat_dissipated = 0.0
        self.total_entropy_produced = 0.0
        self.bit_erasure_count = 0
    
    def analyze_thermodynamic_state(self, geoids: List[GeoidState],
                                  vault_info: Dict[str, Any],
                                  system_entropy: float) -> ThermodynamicState:
        """
        Perform comprehensive thermodynamic analysis of current system state
        """
        timestamp = datetime.now()
        
        # Calculate basic thermodynamic quantities
        total_energy = ThermodynamicCalculator.calculate_semantic_energy(geoids)
        temperature = ThermodynamicCalculator.calculate_semantic_temperature(geoids)
        pressure = ThermodynamicCalculator.calculate_semantic_pressure(geoids, self.vault_capacity)
        
        # Calculate free energy
        free_energy = ThermodynamicCalculator.calculate_free_energy(
            total_energy, system_entropy, temperature
        )
        
        # Calculate chemical potential (energy per geoid)
        chemical_potential = total_energy / len(geoids) if geoids else 0.0
        
        # Calculate changes from previous state
        entropy_production = 0.0
        work_done = 0.0
        heat_dissipated = 0.0
        efficiency = 0.0
        reversibility_index = 1.0
        
        if self.previous_state is not None:
            time_delta = (timestamp - self.previous_state.timestamp).total_seconds()
            
            # Entropy production rate
            entropy_production = ThermodynamicCalculator.calculate_entropy_production_rate(
                self.previous_state.metadata.get('system_entropy', 0.0),
                system_entropy,
                time_delta
            )
            
            # Work and heat calculations
            work_done, heat_dissipated = ThermodynamicCalculator.calculate_work_and_heat(
                self.previous_state.total_energy, total_energy,
                self.previous_state.metadata.get('system_entropy', 0.0), system_entropy,
                temperature
            )
            
            # Thermodynamic efficiency
            if heat_dissipated > 0:
                efficiency = work_done / (work_done + heat_dissipated)
            
            # Reversibility index (0 = irreversible, 1 = reversible)
            if entropy_production >= 0:
                reversibility_index = 1.0 / (1.0 + entropy_production)
            
            # Update totals
            self.total_work_done += work_done
            self.total_heat_dissipated += heat_dissipated
            self.total_entropy_produced += entropy_production * time_delta
        
        # Calculate Landauer cost for information processing
        # Estimate bit erasures from geoid state changes
        bit_erasures = self._estimate_bit_erasures(geoids)
        landauer_cost = ThermodynamicCalculator.calculate_landauer_cost(bit_erasures, temperature)
        
        state = ThermodynamicState(
            timestamp=timestamp,
            total_energy=total_energy,
            free_energy=free_energy,
            entropy_production=entropy_production,
            temperature=temperature,
            pressure=pressure,
            chemical_potential=chemical_potential,
            work_done=work_done,
            heat_dissipated=heat_dissipated,
            efficiency=efficiency,
            reversibility_index=reversibility_index,
            landauer_cost=landauer_cost,
            metadata={
                'system_entropy': system_entropy,
                'geoid_count': len(geoids),
                'vault_info': vault_info,
                'bit_erasures': bit_erasures,
                'total_work_done': self.total_work_done,
                'total_heat_dissipated': self.total_heat_dissipated,
                'total_entropy_produced': self.total_entropy_produced,
                'vault_capacity': self.vault_capacity
            }
        )
        
        self.states.append(state)
        self.previous_state = state
        
        return state
    
    def _estimate_bit_erasures(self, geoids: List[GeoidState]) -> int:
        """
        Estimate number of bits erased in semantic transformations
        Based on changes in semantic state complexity
        """
        if self.previous_state is None:
            return 0
        
        current_complexity = sum(len(geoid.semantic_state) for geoid in geoids)
        previous_complexity = self.previous_state.metadata.get('total_complexity', current_complexity)
        
        # Estimate bit erasures from complexity reduction
        complexity_reduction = max(0, previous_complexity - current_complexity)
        
        # Each reduced feature represents approximately 8 bits (rough estimate)
        estimated_erasures = int(complexity_reduction * 8)
        
        self.bit_erasure_count += estimated_erasures
        return estimated_erasures
    
    def check_thermodynamic_constraints(self, state: ThermodynamicState) -> List[Dict[str, Any]]:
        """
        Check for violations of thermodynamic constraints
        """
        violations = []
        
        # Second Law: Entropy should not decrease in isolated system
        if state.entropy_production < -1e-6:  # Small tolerance for numerical errors
            violations.append({
                'type': 'second_law_violation',
                'description': 'Entropy production is negative',
                'value': state.entropy_production,
                'severity': 'high'
            })
        
        # Energy conservation check
        if self.previous_state is not None:
            energy_change = state.total_energy - self.previous_state.total_energy
            expected_change = state.work_done - state.heat_dissipated
            
            if abs(energy_change - expected_change) > 0.1:  # Tolerance
                violations.append({
                    'type': 'energy_conservation_violation',
                    'description': 'Energy change inconsistent with work-heat balance',
                    'energy_change': energy_change,
                    'expected_change': expected_change,
                    'severity': 'medium'
                })
        
        # Temperature bounds
        if state.temperature < 0.01 or state.temperature > 100:
            violations.append({
                'type': 'temperature_anomaly',
                'description': 'Temperature outside expected range',
                'value': state.temperature,
                'severity': 'medium'
            })
        
        # Pressure bounds
        if state.pressure > 1.0:  # System approaching capacity
            violations.append({
                'type': 'high_pressure_warning',
                'description': 'System pressure indicates near-capacity operation',
                'value': state.pressure,
                'severity': 'low'
            })
        
        return violations
    
    def calculate_thermodynamic_efficiency(self, window_size: int = 100) -> Dict[str, float]:
        """
        Calculate various thermodynamic efficiency measures
        """
        if len(self.states) < 2:
            return {}
        
        recent_states = list(self.states)[-window_size:]
        
        # Carnot efficiency (theoretical maximum)
        avg_temp = np.mean([s.temperature for s in recent_states])
        carnot_efficiency = 1 - self.thermal_reservoir_temp / avg_temp if avg_temp > self.thermal_reservoir_temp else 0
        
        # Actual efficiency
        total_work = sum(s.work_done for s in recent_states)
        total_heat = sum(s.heat_dissipated for s in recent_states)
        actual_efficiency = total_work / (total_work + total_heat) if (total_work + total_heat) > 0 else 0
        
        # Reversibility measure
        avg_reversibility = np.mean([s.reversibility_index for s in recent_states])
        
        # Information processing efficiency
        total_landauer_cost = sum(s.landauer_cost for s in recent_states)
        total_information_processed = sum(s.metadata.get('bit_erasures', 0) for s in recent_states)
        info_efficiency = total_information_processed / total_landauer_cost if total_landauer_cost > 0 else 0
        
        return {
            'carnot_efficiency': carnot_efficiency,
            'actual_efficiency': actual_efficiency,
            'efficiency_ratio': actual_efficiency / carnot_efficiency if carnot_efficiency > 0 else 0,
            'reversibility_index': avg_reversibility,
            'information_efficiency': info_efficiency,
            'total_entropy_produced': self.total_entropy_produced
        }
    
    def get_thermodynamic_trends(self, window_size: int = 100) -> Dict[str, List[float]]:
        """Get thermodynamic trends over recent measurements"""
        if len(self.states) < 2:
            return {}
        
        recent_states = list(self.states)[-window_size:]
        
        return {
            'total_energy': [s.total_energy for s in recent_states],
            'free_energy': [s.free_energy for s in recent_states],
            'temperature': [s.temperature for s in recent_states],
            'pressure': [s.pressure for s in recent_states],
            'entropy_production': [s.entropy_production for s in recent_states],
            'efficiency': [s.efficiency for s in recent_states],
            'reversibility_index': [s.reversibility_index for s in recent_states],
            'landauer_cost': [s.landauer_cost for s in recent_states],
            'timestamps': [s.timestamp.isoformat() for s in recent_states]
        }
    
    def detect_thermodynamic_anomalies(self, threshold_std: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalous thermodynamic behavior"""
        if len(self.states) < 10:
            return []
        
        recent_states = list(self.states)[-50:]
        anomalies = []
        
        # Energy anomalies
        energies = [s.total_energy for s in recent_states]
        energy_mean = np.mean(energies)
        energy_std = np.std(energies)
        
        for state in recent_states[-5:]:
            if abs(state.total_energy - energy_mean) > threshold_std * energy_std:
                anomalies.append({
                    'timestamp': state.timestamp.isoformat(),
                    'type': 'energy_anomaly',
                    'value': state.total_energy,
                    'deviation': abs(state.total_energy - energy_mean) / energy_std,
                    'severity': 'high' if state.total_energy > energy_mean else 'low'
                })
        
        # Temperature anomalies
        temperatures = [s.temperature for s in recent_states]
        temp_mean = np.mean(temperatures)
        temp_std = np.std(temperatures)
        
        for state in recent_states[-5:]:
            if abs(state.temperature - temp_mean) > threshold_std * temp_std:
                anomalies.append({
                    'timestamp': state.timestamp.isoformat(),
                    'type': 'temperature_anomaly',
                    'value': state.temperature,
                    'deviation': abs(state.temperature - temp_mean) / temp_std,
                    'severity': 'medium'
                })
        
        # Efficiency anomalies
        efficiencies = [s.efficiency for s in recent_states if s.efficiency > 0]
        if efficiencies:
            eff_mean = np.mean(efficiencies)
            eff_std = np.std(efficiencies)
            
            for state in recent_states[-5:]:
                if state.efficiency > 0 and abs(state.efficiency - eff_mean) > threshold_std * eff_std:
                    anomalies.append({
                        'timestamp': state.timestamp.isoformat(),
                        'type': 'efficiency_anomaly',
                        'value': state.efficiency,
                        'deviation': abs(state.efficiency - eff_mean) / eff_std,
                        'severity': 'low' if state.efficiency < eff_mean else 'high'
                    })
        
        return anomalies
    
    def export_thermodynamic_data(self) -> List[Dict[str, Any]]:
        """Export thermodynamic measurements for analysis"""
        return [
            {
                'timestamp': s.timestamp.isoformat(),
                'total_energy': s.total_energy,
                'free_energy': s.free_energy,
                'entropy_production': s.entropy_production,
                'temperature': s.temperature,
                'pressure': s.pressure,
                'chemical_potential': s.chemical_potential,
                'work_done': s.work_done,
                'heat_dissipated': s.heat_dissipated,
                'efficiency': s.efficiency,
                'reversibility_index': s.reversibility_index,
                'landauer_cost': s.landauer_cost,
                'metadata': s.metadata
            }
            for s in self.states
        ]