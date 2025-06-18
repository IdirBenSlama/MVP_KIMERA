"""
Physical Grounding System
Connects concepts to physical properties and constraints
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PhysicalState(Enum):
    """Physical states of matter"""
    SOLID = "solid"
    LIQUID = "liquid"
    GAS = "gas"
    PLASMA = "plasma"
    UNKNOWN = "unknown"

@dataclass
class PhysicalProperties:
    """Physical properties of a concept"""
    mass: Optional[float] = None  # kg
    volume: Optional[float] = None  # m³
    density: Optional[float] = None  # kg/m³
    temperature: Optional[float] = None  # Kelvin
    state: PhysicalState = PhysicalState.UNKNOWN
    hardness: Optional[float] = None  # Mohs scale 0-10
    elasticity: Optional[float] = None  # Young's modulus
    conductivity: Optional[Dict[str, float]] = None  # thermal, electrical
    
    def calculate_density(self):
        """Calculate density from mass and volume"""
        if self.mass is not None and self.volume is not None and self.volume > 0:
            self.density = self.mass / self.volume
        return self.density

@dataclass
class PhysicalInteraction:
    """Represents physical interaction between concepts"""
    interaction_type: str  # collision, attraction, repulsion, etc.
    strength: float  # 0.0 to 1.0
    range: Optional[float] = None  # meters
    energy: Optional[float] = None  # joules
    reversible: bool = True

@dataclass
class PhysicalConstraint:
    """Physical constraint on a concept"""
    constraint_type: str  # gravity, friction, inertia, etc.
    description: str
    mathematical_form: Optional[str] = None
    parameters: Dict[str, float] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class PhysicalGroundingSystem:
    """
    System for grounding concepts in physical reality.
    Maps abstract concepts to physical properties and constraints.
    """
    
    def __init__(self):
        # Physical knowledge base
        self.physical_knowledge = {}
        
        # Physical laws and constants
        self.physical_constants = {
            'gravity': 9.81,  # m/s²
            'speed_of_light': 299792458,  # m/s
            'planck_constant': 6.62607015e-34,  # J⋅s
            'avogadro_number': 6.02214076e23,  # mol⁻¹
            'gas_constant': 8.314462618,  # J/(mol⋅K)
        }
        
        # Initialize with basic physical knowledge
        self._init_physical_knowledge()
        
        logger.info("Physical Grounding System initialized")
    
    def _init_physical_knowledge(self):
        """Initialize basic physical properties of common concepts"""
        # Substances
        self.physical_knowledge['water'] = PhysicalProperties(
            density=1000.0,  # kg/m³ at 4°C
            state=PhysicalState.LIQUID,
            temperature=293.15,  # 20°C in Kelvin
            conductivity={'thermal': 0.6, 'electrical': 0.0001}
        )
        
        self.physical_knowledge['ice'] = PhysicalProperties(
            density=917.0,  # kg/m³
            state=PhysicalState.SOLID,
            temperature=273.15,  # 0°C
            hardness=1.5,  # Mohs scale
            conductivity={'thermal': 2.2, 'electrical': 1e-8}
        )
        
        self.physical_knowledge['air'] = PhysicalProperties(
            density=1.225,  # kg/m³ at sea level
            state=PhysicalState.GAS,
            temperature=293.15,
            conductivity={'thermal': 0.024, 'electrical': 0.0}
        )
        
        self.physical_knowledge['iron'] = PhysicalProperties(
            density=7874.0,  # kg/m³
            state=PhysicalState.SOLID,
            hardness=4.0,
            elasticity=211e9,  # Pa
            conductivity={'thermal': 80.4, 'electrical': 1.0e7}
        )
        
        self.physical_knowledge['wood'] = PhysicalProperties(
            density=700.0,  # kg/m³ (average)
            state=PhysicalState.SOLID,
            hardness=2.5,
            elasticity=10e9,
            conductivity={'thermal': 0.15, 'electrical': 1e-16}
        )
        
        # Objects
        self.physical_knowledge['car'] = PhysicalProperties(
            mass=1500.0,  # kg (average)
            volume=10.0,  # m³ (approximate)
            state=PhysicalState.SOLID,
            density=1500.0,
            hardness=5.0  # Mixed materials
        )
        
        self.physical_knowledge['feather'] = PhysicalProperties(
            mass=0.005,  # kg
            volume=0.0001,  # m³
            density=50.0,
            state=PhysicalState.SOLID,
            hardness=0.5
        )
        
        # Forces and fields
        self.physical_knowledge['gravity'] = {
            'type': 'force_field',
            'strength': self.physical_constants['gravity'],
            'range': float('inf'),
            'direction': 'downward',
            'formula': 'F = m * g'
        }
        
        self.physical_knowledge['magnetism'] = {
            'type': 'force_field',
            'strength': 'variable',
            'range': 'inverse_square',
            'direction': 'dipolar',
            'formula': 'F = (μ₀/4π) * (m₁*m₂/r²)'
        }
    
    def map_properties(self, concept: str, 
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Map a concept to its physical properties.
        
        Args:
            concept: The concept to map
            context: Optional context information
            
        Returns:
            Dictionary of physical properties
        """
        logger.debug(f"Mapping physical properties for: {concept}")
        
        # Check direct mapping
        if concept.lower() in self.physical_knowledge:
            known = self.physical_knowledge[concept.lower()]
            
            if isinstance(known, PhysicalProperties):
                properties = self._properties_to_dict(known)
            else:
                # Force field or other non-material concept
                properties = known.copy()
                properties['confidence'] = 0.9
        else:
            # Infer properties
            properties = self._infer_physical_properties(concept, context)
        
        # Add interactions and constraints
        properties['interactions'] = self._identify_interactions(concept, properties)
        properties['constraints'] = self._identify_constraints(concept, properties)
        
        return properties
    
    def _properties_to_dict(self, props: PhysicalProperties) -> Dict[str, Any]:
        """Convert PhysicalProperties to dictionary"""
        return {
            'mass': props.mass,
            'volume': props.volume,
            'density': props.density or props.calculate_density(),
            'temperature': props.temperature,
            'state': props.state.value,
            'hardness': props.hardness,
            'elasticity': props.elasticity,
            'conductivity': props.conductivity,
            'confidence': 0.9
        }
    
    def _infer_physical_properties(self, concept: str, 
                                 context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Infer physical properties when not directly known"""
        properties = {
            'state': PhysicalState.UNKNOWN.value,
            'confidence': 0.5
        }
        
        concept_lower = concept.lower()
        
        # State inference
        if any(word in concept_lower for word in ['solid', 'hard', 'rigid']):
            properties['state'] = PhysicalState.SOLID.value
            properties['hardness'] = 5.0  # Medium hardness
        elif any(word in concept_lower for word in ['liquid', 'fluid', 'flow']):
            properties['state'] = PhysicalState.LIQUID.value
            properties['density'] = 1000.0  # Water-like
        elif any(word in concept_lower for word in ['gas', 'vapor', 'air']):
            properties['state'] = PhysicalState.GAS.value
            properties['density'] = 1.2  # Air-like
        
        # Mass inference
        if any(word in concept_lower for word in ['heavy', 'massive']):
            properties['mass'] = 1000.0  # 1 ton
        elif any(word in concept_lower for word in ['light', 'weightless']):
            properties['mass'] = 0.1  # 100g
        elif any(word in concept_lower for word in ['tiny', 'micro']):
            properties['mass'] = 0.001  # 1g
        
        # Temperature inference
        if any(word in concept_lower for word in ['hot', 'burning', 'fire']):
            properties['temperature'] = 1000.0  # 727°C
        elif any(word in concept_lower for word in ['cold', 'frozen', 'ice']):
            properties['temperature'] = 250.0  # -23°C
        elif any(word in concept_lower for word in ['warm']):
            properties['temperature'] = 310.0  # 37°C
        
        # Use context if available
        if context:
            if 'physical_properties' in context:
                properties.update(context['physical_properties'])
                properties['confidence'] = 0.8
        
        return properties
    
    def _identify_interactions(self, concept: str, 
                             properties: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify possible physical interactions"""
        interactions = []
        
        # Gravitational interaction (everything with mass)
        if properties.get('mass') and properties['mass'] > 0:
            interactions.append({
                'type': 'gravitational',
                'strength': 1.0,
                'range': float('inf'),
                'description': 'Attracts and is attracted by other masses'
            })
        
        # Electromagnetic interactions
        if properties.get('conductivity'):
            electrical = properties['conductivity'].get('electrical', 0)
            if electrical > 1e-10:
                interactions.append({
                    'type': 'electromagnetic',
                    'strength': min(1.0, electrical / 1e7),
                    'range': float('inf'),
                    'description': 'Can conduct electricity'
                })
        
        # Collision interactions (solid objects)
        if properties.get('state') == PhysicalState.SOLID.value:
            interactions.append({
                'type': 'collision',
                'strength': 0.8,
                'range': 0.0,  # Contact only
                'description': 'Can collide with other solid objects'
            })
            
            # Friction
            interactions.append({
                'type': 'friction',
                'strength': 0.5,
                'range': 0.0,
                'description': 'Experiences friction when in contact'
            })
        
        # Fluid interactions
        if properties.get('state') in [PhysicalState.LIQUID.value, PhysicalState.GAS.value]:
            interactions.append({
                'type': 'fluid_dynamics',
                'strength': 0.7,
                'range': 1.0,  # Local influence
                'description': 'Flows and exerts pressure'
            })
        
        # Thermal interactions
        if properties.get('temperature'):
            interactions.append({
                'type': 'thermal',
                'strength': 0.6,
                'range': 0.1,  # Short range
                'description': 'Exchanges heat with environment'
            })
        
        return interactions
    
    def _identify_constraints(self, concept: str, 
                            properties: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify physical constraints on the concept"""
        constraints = []
        
        # Conservation laws
        constraints.append({
            'type': 'conservation_of_energy',
            'description': 'Total energy must be conserved',
            'formula': 'E_total = E_kinetic + E_potential + E_internal'
        })
        
        if properties.get('mass') and properties['mass'] > 0:
            constraints.append({
                'type': 'conservation_of_momentum',
                'description': 'Momentum is conserved in closed systems',
                'formula': 'p = m * v'
            })
        
        # State-specific constraints
        state = properties.get('state')
        
        if state == PhysicalState.SOLID.value:
            constraints.append({
                'type': 'rigid_body',
                'description': 'Maintains shape under normal conditions',
                'parameters': {'deformation_threshold': properties.get('elasticity', 1e9)}
            })
        
        elif state == PhysicalState.LIQUID.value:
            constraints.append({
                'type': 'incompressible',
                'description': 'Volume remains nearly constant',
                'parameters': {'bulk_modulus': 2.2e9}  # Water
            })
            constraints.append({
                'type': 'container_required',
                'description': 'Takes shape of container'
            })
        
        elif state == PhysicalState.GAS.value:
            constraints.append({
                'type': 'ideal_gas_law',
                'description': 'Pressure, volume, and temperature are related',
                'formula': 'PV = nRT',
                'parameters': {'R': self.physical_constants['gas_constant']}
            })
        
        # Temperature constraints
        if properties.get('temperature'):
            constraints.append({
                'type': 'thermodynamic',
                'description': 'Temperature cannot go below absolute zero',
                'parameters': {'min_temperature': 0.0}  # Kelvin
            })
        
        # Speed constraint
        constraints.append({
            'type': 'relativistic',
            'description': 'Cannot exceed speed of light',
            'parameters': {'max_speed': self.physical_constants['speed_of_light']}
        })
        
        return constraints
    
    def simulate_interaction(self, concept1: str, concept2: str,
                           interaction_type: str = 'collision') -> Dict[str, Any]:
        """
        Simulate physical interaction between two concepts.
        
        Args:
            concept1: First concept
            concept2: Second concept
            interaction_type: Type of interaction to simulate
            
        Returns:
            Simulation results
        """
        logger.debug(f"Simulating {interaction_type} between {concept1} and {concept2}")
        
        # Get properties
        props1 = self.map_properties(concept1)
        props2 = self.map_properties(concept2)
        
        if interaction_type == 'collision':
            return self._simulate_collision(concept1, props1, concept2, props2)
        elif interaction_type == 'gravitational':
            return self._simulate_gravity(concept1, props1, concept2, props2)
        elif interaction_type == 'thermal':
            return self._simulate_thermal(concept1, props1, concept2, props2)
        else:
            return {'error': f'Unknown interaction type: {interaction_type}'}
    
    def _simulate_collision(self, concept1: str, props1: Dict,
                          concept2: str, props2: Dict) -> Dict[str, Any]:
        """Simulate collision between two objects"""
        result = {
            'interaction': 'collision',
            'participants': [concept1, concept2]
        }
        
        # Check if both are solid
        if (props1.get('state') != PhysicalState.SOLID.value or
            props2.get('state') != PhysicalState.SOLID.value):
            result['outcome'] = 'no_collision'
            result['reason'] = 'At least one object is not solid'
            return result
        
        # Compare masses
        mass1 = props1.get('mass') or 1.0
        mass2 = props2.get('mass') or 1.0
        
        # Compare hardness
        hard1 = props1.get('hardness', 5.0)
        hard2 = props2.get('hardness', 5.0)
        
        # Elastic collision simulation
        if mass1 > mass2 * 10:
            result['outcome'] = f'{concept1} barely affected, {concept2} bounces off'
        elif mass2 > mass1 * 10:
            result['outcome'] = f'{concept2} barely affected, {concept1} bounces off'
        else:
            result['outcome'] = 'Both objects rebound'
        
        # Damage assessment
        if hard1 < hard2 / 2:
            result['damage'] = f'{concept1} may be damaged'
        elif hard2 < hard1 / 2:
            result['damage'] = f'{concept2} may be damaged'
        
        result['energy_transfer'] = 'Kinetic energy partially converted to heat and sound'
        result['conservation'] = 'Momentum conserved'
        
        return result
    
    def _simulate_gravity(self, concept1: str, props1: Dict,
                        concept2: str, props2: Dict) -> Dict[str, Any]:
        """Simulate gravitational interaction"""
        result = {
            'interaction': 'gravitational',
            'participants': [concept1, concept2]
        }
        
        mass1 = props1.get('mass', 0)
        mass2 = props2.get('mass', 0)
        
        if mass1 == 0 or mass2 == 0:
            result['force'] = 0
            result['description'] = 'No gravitational force (massless object)'
        else:
            # Simplified calculation (assuming 1m separation)
            G = 6.67430e-11  # Gravitational constant
            force = G * mass1 * mass2  # F = G*m1*m2/r²
            
            result['force'] = force
            result['direction'] = 'attractive'
            result['description'] = f'Mutual gravitational attraction of {force:.2e} N'
            
            # Determine dominant object
            if mass1 > mass2 * 100:
                result['dominant'] = concept1
            elif mass2 > mass1 * 100:
                result['dominant'] = concept2
            else:
                result['dominant'] = 'mutual'
        
        return result
    
    def _simulate_thermal(self, concept1: str, props1: Dict,
                        concept2: str, props2: Dict) -> Dict[str, Any]:
        """Simulate thermal interaction"""
        result = {
            'interaction': 'thermal',
            'participants': [concept1, concept2]
        }
        
        temp1 = props1.get('temperature', 293.15)  # Room temp default
        temp2 = props2.get('temperature', 293.15)
        
        if abs(temp1 - temp2) < 0.1:
            result['heat_flow'] = 'negligible'
            result['description'] = 'Objects are in thermal equilibrium'
        else:
            if temp1 > temp2:
                result['heat_flow'] = f'{concept1} → {concept2}'
                result['description'] = f'Heat flows from {concept1} ({temp1:.1f}K) to {concept2} ({temp2:.1f}K)'
            else:
                result['heat_flow'] = f'{concept2} → {concept1}'
                result['description'] = f'Heat flows from {concept2} ({temp2:.1f}K) to {concept1} ({temp1:.1f}K)'
            
            # Rate depends on thermal conductivity
            cond1 = props1.get('conductivity', {}).get('thermal', 1.0)
            cond2 = props2.get('conductivity', {}).get('thermal', 1.0)
            avg_conductivity = (cond1 + cond2) / 2
            
            if avg_conductivity > 10:
                result['rate'] = 'rapid'
            elif avg_conductivity > 1:
                result['rate'] = 'moderate'
            else:
                result['rate'] = 'slow'
        
        result['equilibrium_temperature'] = (temp1 + temp2) / 2  # Simplified
        
        return result
    
    def check_physical_plausibility(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a scenario is physically plausible.
        
        Args:
            scenario: Description of the scenario to check
            
        Returns:
            Plausibility assessment
        """
        plausibility = {
            'plausible': True,
            'violations': [],
            'warnings': [],
            'confidence': 1.0
        }
        
        # Check for conservation law violations
        if 'energy_created' in scenario or 'energy_destroyed' in scenario:
            plausibility['plausible'] = False
            plausibility['violations'].append('Energy conservation violated')
            plausibility['confidence'] *= 0.1
        
        # Check for speed violations
        if 'speed' in scenario and scenario['speed'] > self.physical_constants['speed_of_light']:
            plausibility['plausible'] = False
            plausibility['violations'].append('Exceeds speed of light')
            plausibility['confidence'] *= 0.0
        
        # Check for temperature violations
        if 'temperature' in scenario and scenario['temperature'] < 0:
            plausibility['plausible'] = False
            plausibility['violations'].append('Temperature below absolute zero')
            plausibility['confidence'] *= 0.0
        
        # Check for state consistency
        if 'state' in scenario and 'temperature' in scenario:
            state = scenario['state']
            temp = scenario['temperature']
            
            if state == 'liquid' and temp < 273.15:
                plausibility['warnings'].append('Liquid water below freezing point')
                plausibility['confidence'] *= 0.5
            elif state == 'ice' and temp > 273.15:
                plausibility['warnings'].append('Ice above melting point')
                plausibility['confidence'] *= 0.5
        
        # Check for density anomalies
        if 'mass' in scenario and 'volume' in scenario:
            density = scenario['mass'] / scenario['volume']
            
            if density > 22590:  # Osmium density
                plausibility['warnings'].append('Unusually high density')
                plausibility['confidence'] *= 0.8
            elif density < 0.0899:  # Hydrogen gas
                plausibility['warnings'].append('Unusually low density')
                plausibility['confidence'] *= 0.8
        
        return plausibility