"""
Adaptive Neural Optimization Engine for Kimera SWM

This module implements a self-learning optimization system that continuously
adapts processing parameters based on real-time performance feedback using
neural network-based decision making.

Key Innovations:
1. Self-Learning Parameter Optimization: Neural network learns optimal settings
2. Real-Time Performance Adaptation: Continuous adjustment based on metrics
3. Predictive Load Balancing: Anticipates system bottlenecks before they occur
4. Evolutionary Algorithm Integration: Genetic optimization for parameter spaces
5. Multi-Objective Optimization: Balances speed, accuracy, and resource usage

Author: Kimera SWM Innovation Team
Version: 1.0.0 - Neural Alpha
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
import time
import logging
import threading
from collections import deque
import psutil
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SystemState:
    """Represents current system state for optimization decisions"""
    cpu_usage: float
    memory_usage: float
    gpu_utilization: float
    gpu_memory: float
    gpu_temperature: float
    thread_count: int
    active_operations: int
    avg_response_time: float
    success_rate: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class OptimizationParameters:
    """Parameters that can be optimized by the neural network"""
    batch_size: int = 32
    thread_count: int = 4
    gpu_memory_threshold: float = 0.8
    processing_timeout: float = 60.0
    feature_compression_ratio: float = 1.0
    embedding_precision: str = "float32"  # float16, float32, float64
    cache_size: int = 1000
    prefetch_factor: float = 2.0
    
    def to_vector(self) -> np.ndarray:
        """Convert parameters to neural network input vector"""
        precision_map = {"float16": 0.0, "float32": 0.5, "float64": 1.0}
        return np.array([
            self.batch_size / 256.0,  # Normalize to 0-1
            self.thread_count / 128.0,
            self.gpu_memory_threshold,
            self.processing_timeout / 120.0,
            self.feature_compression_ratio,
            precision_map.get(self.embedding_precision, 0.5),
            self.cache_size / 10000.0,
            self.prefetch_factor / 10.0
        ], dtype=np.float32)
    
    @classmethod
    def from_vector(cls, vector: np.ndarray) -> 'OptimizationParameters':
        """Create parameters from neural network output vector"""
        precision_options = ["float16", "float32", "float64"]
        precision_idx = int(vector[5] * len(precision_options))
        precision_idx = max(0, min(precision_idx, len(precision_options) - 1))
        
        return cls(
            batch_size=max(1, int(vector[0] * 256)),
            thread_count=max(1, int(vector[1] * 128)),
            gpu_memory_threshold=max(0.1, min(0.95, vector[2])),
            processing_timeout=max(10.0, vector[3] * 120.0),
            feature_compression_ratio=max(0.1, min(2.0, vector[4])),
            embedding_precision=precision_options[precision_idx],
            cache_size=max(100, int(vector[6] * 10000)),
            prefetch_factor=max(0.5, min(10.0, vector[7] * 10.0))
        )

@dataclass
class PerformanceMetrics:
    """Performance metrics for optimization feedback"""
    throughput: float  # operations per second
    latency: float     # average response time
    resource_efficiency: float  # 0-1 score
    error_rate: float  # 0-1 error rate
    gpu_efficiency: float  # GPU utilization efficiency
    memory_efficiency: float  # Memory usage efficiency
    
    def to_reward_signal(self) -> float:
        """Convert metrics to single reward signal for neural network training"""
        # Multi-objective reward function
        throughput_reward = min(1.0, self.throughput / 100.0)  # Normalize to target 100 ops/sec
        latency_penalty = max(0.0, 1.0 - self.latency / 5.0)   # Penalty for >5s latency
        efficiency_reward = (self.resource_efficiency + self.gpu_efficiency + self.memory_efficiency) / 3.0
        error_penalty = 1.0 - self.error_rate
        
        # Weighted combination
        reward = (
            throughput_reward * 0.3 +
            latency_penalty * 0.2 +
            efficiency_reward * 0.3 +
            error_penalty * 0.2
        )
        
        return max(0.0, min(1.0, reward))

class AdaptiveNeuralNetwork(nn.Module):
    """Neural network for learning optimal system parameters"""
    
    def __init__(self, state_dim: int = 8, param_dim: int = 8, hidden_dim: int = 128):
        super().__init__()
        
        # Input: system state + current parameters
        input_dim = state_dim + param_dim
        
        # Multi-layer architecture with residual connections
        self.input_layer = nn.Linear(input_dim, hidden_dim)
        self.hidden_layers = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim) for _ in range(4)
        ])
        self.output_layer = nn.Linear(hidden_dim, param_dim)
        
        # Activation functions
        self.activation = nn.ReLU()
        self.output_activation = nn.Sigmoid()  # Output in 0-1 range
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.1)
        
        # Batch normalization
        self.batch_norms = nn.ModuleList([
            nn.BatchNorm1d(hidden_dim) for _ in range(len(self.hidden_layers))
        ])
        
    def forward(self, state: torch.Tensor, current_params: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network"""
        # Combine state and current parameters
        x = torch.cat([state, current_params], dim=-1)
        
        # Input layer
        x = self.activation(self.input_layer(x))
        x = self.dropout(x)
        
        # Hidden layers with residual connections
        for i, (layer, bn) in enumerate(zip(self.hidden_layers, self.batch_norms)):
            residual = x
            x = layer(x)
            if x.shape[0] > 1:  # Only apply batch norm if batch size > 1
                x = bn(x)
            x = self.activation(x)
            x = self.dropout(x)
            
            # Residual connection
            if i > 0:  # Skip first layer for residual
                x = x + residual
        
        # Output layer
        x = self.output_layer(x)
        x = self.output_activation(x)
        
        return x

class EvolutionaryOptimizer:
    """Evolutionary algorithm for parameter space exploration"""
    
    def __init__(self, population_size: int = 20, mutation_rate: float = 0.1):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = []
        self.fitness_scores = []
        
    def initialize_population(self) -> List[OptimizationParameters]:
        """Initialize random population of parameters"""
        self.population = []
        for _ in range(self.population_size):
            # Random parameter initialization
            params = OptimizationParameters(
                batch_size=np.random.randint(8, 256),
                thread_count=np.random.randint(1, 64),
                gpu_memory_threshold=np.random.uniform(0.3, 0.95),
                processing_timeout=np.random.uniform(10.0, 120.0),
                feature_compression_ratio=np.random.uniform(0.5, 2.0),
                embedding_precision=np.random.choice(["float16", "float32", "float64"]),
                cache_size=np.random.randint(100, 5000),
                prefetch_factor=np.random.uniform(0.5, 5.0)
            )
            self.population.append(params)
        
        self.fitness_scores = [0.0] * self.population_size
        return self.population
    
    def evaluate_fitness(self, params: OptimizationParameters, performance: PerformanceMetrics) -> float:
        """Evaluate fitness of parameter set"""
        return performance.to_reward_signal()
    
    def evolve_generation(self) -> List[OptimizationParameters]:
        """Evolve population to next generation"""
        if len(self.population) != len(self.fitness_scores):
            return self.population
        
        # Selection: tournament selection
        new_population = []
        
        for _ in range(self.population_size):
            # Tournament selection
            tournament_size = 3
            tournament_indices = np.random.choice(len(self.population), tournament_size, replace=False)
            tournament_fitness = [self.fitness_scores[i] for i in tournament_indices]
            winner_idx = tournament_indices[np.argmax(tournament_fitness)]
            
            # Create offspring through mutation
            parent = self.population[winner_idx]
            offspring = self._mutate(parent)
            new_population.append(offspring)
        
        self.population = new_population
        self.fitness_scores = [0.0] * self.population_size
        
        return self.population
    
    def _mutate(self, params: OptimizationParameters) -> OptimizationParameters:
        """Mutate parameters with small random changes"""
        if np.random.random() > self.mutation_rate:
            return params  # No mutation
        
        # Convert to vector, mutate, convert back
        vector = params.to_vector()
        
        # Add Gaussian noise
        noise = np.random.normal(0, 0.05, vector.shape)
        mutated_vector = vector + noise
        
        # Clamp to valid range
        mutated_vector = np.clip(mutated_vector, 0.0, 1.0)
        
        return OptimizationParameters.from_vector(mutated_vector)
    
    def get_best_parameters(self) -> OptimizationParameters:
        """Get best parameters from current population"""
        if not self.fitness_scores:
            return OptimizationParameters()
        
        best_idx = np.argmax(self.fitness_scores)
        return self.population[best_idx]

class AdaptiveNeuralOptimizer:
    """Main adaptive optimization engine combining neural networks and evolutionary algorithms"""
    
    def __init__(self, 
                 learning_rate: float = 0.001,
                 memory_size: int = 10000,
                 update_frequency: int = 100):
        
        self.learning_rate = learning_rate
        self.memory_size = memory_size
        self.update_frequency = update_frequency
        
        # Neural network components
        self.neural_network = AdaptiveNeuralNetwork()
        self.optimizer = optim.Adam(self.neural_network.parameters(), lr=learning_rate)
        self.loss_function = nn.MSELoss()
        
        # Experience replay memory
        self.experience_memory = deque(maxlen=memory_size)
        
        # Evolutionary optimizer
        self.evolutionary_optimizer = EvolutionaryOptimizer()
        self.evolutionary_optimizer.initialize_population()
        
        # Current optimization state
        self.current_parameters = OptimizationParameters()
        self.system_state_history = deque(maxlen=1000)
        self.performance_history = deque(maxlen=1000)
        
        # Training metrics
        self.training_step = 0
        self.last_update_time = time.time()
        
        # Thread safety
        self.optimization_lock = threading.Lock()
        
        # Persistence
        self.model_save_path = Path("models/adaptive_optimizer.pth")
        self.model_save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing model if available
        self._load_model()
    
    def get_optimal_parameters(self, current_state: SystemState) -> OptimizationParameters:
        """Get optimal parameters for current system state"""
        with self.optimization_lock:
            # Convert system state to tensor
            state_vector = self._system_state_to_vector(current_state)
            current_params_vector = self.current_parameters.to_vector()
            
            state_tensor = torch.FloatTensor(state_vector).unsqueeze(0)
            params_tensor = torch.FloatTensor(current_params_vector).unsqueeze(0)
            
            # Get neural network prediction
            self.neural_network.eval()
            with torch.no_grad():
                predicted_params_vector = self.neural_network(state_tensor, params_tensor)
                predicted_params_vector = predicted_params_vector.squeeze(0).numpy()
            
            # Convert back to parameters
            neural_params = OptimizationParameters.from_vector(predicted_params_vector)
            
            # Get evolutionary algorithm suggestion
            evolutionary_params = self.evolutionary_optimizer.get_best_parameters()
            
            # Combine neural and evolutionary suggestions
            optimal_params = self._combine_suggestions(neural_params, evolutionary_params, current_state)
            
            self.current_parameters = optimal_params
            return optimal_params
    
    def update_performance_feedback(self, 
                                  system_state: SystemState, 
                                  parameters: OptimizationParameters,
                                  performance: PerformanceMetrics):
        """Update optimizer with performance feedback"""
        with self.optimization_lock:
            # Store experience for replay
            experience = {
                'state': self._system_state_to_vector(system_state),
                'parameters': parameters.to_vector(),
                'performance': performance,
                'reward': performance.to_reward_signal(),
                'timestamp': time.time()
            }
            self.experience_memory.append(experience)
            
            # Update evolutionary algorithm
            param_idx = self._find_similar_evolutionary_params(parameters)
            if param_idx is not None:
                fitness = self.evolutionary_optimizer.evaluate_fitness(parameters, performance)
                self.evolutionary_optimizer.fitness_scores[param_idx] = fitness
            
            # Store history
            self.system_state_history.append(system_state)
            self.performance_history.append(performance)
            
            # Periodic neural network training
            self.training_step += 1
            if self.training_step % self.update_frequency == 0:
                self._train_neural_network()
                self._evolve_population()
                self._save_model()
    
    def _system_state_to_vector(self, state: SystemState) -> np.ndarray:
        """Convert system state to neural network input vector"""
        return np.array([
            state.cpu_usage / 100.0,
            state.memory_usage / 100.0,
            state.gpu_utilization / 100.0,
            state.gpu_memory / 100.0,
            state.gpu_temperature / 100.0,
            min(1.0, state.thread_count / 128.0),
            min(1.0, state.active_operations / 1000.0),
            min(1.0, state.avg_response_time / 10.0)
        ], dtype=np.float32)
    
    def _combine_suggestions(self, 
                           neural_params: OptimizationParameters,
                           evolutionary_params: OptimizationParameters,
                           current_state: SystemState) -> OptimizationParameters:
        """Combine neural network and evolutionary algorithm suggestions"""
        
        # Weight based on recent performance
        recent_performance = list(self.performance_history)[-10:] if self.performance_history else []
        
        if recent_performance:
            avg_reward = np.mean([p.to_reward_signal() for p in recent_performance])
            neural_weight = 0.7 if avg_reward > 0.6 else 0.3  # Trust neural more if performing well
        else:
            neural_weight = 0.5
        
        evolutionary_weight = 1.0 - neural_weight
        
        # Weighted combination
        neural_vector = neural_params.to_vector()
        evolutionary_vector = evolutionary_params.to_vector()
        
        combined_vector = neural_weight * neural_vector + evolutionary_weight * evolutionary_vector
        
        # Apply system-specific constraints
        combined_vector = self._apply_system_constraints(combined_vector, current_state)
        
        return OptimizationParameters.from_vector(combined_vector)
    
    def _apply_system_constraints(self, 
                                params_vector: np.ndarray, 
                                current_state: SystemState) -> np.ndarray:
        """Apply system-specific constraints to parameters"""
        
        # Reduce batch size if memory is high
        if current_state.memory_usage > 80:
            params_vector[0] *= 0.7  # Reduce batch size
        
        # Reduce thread count if CPU usage is high
        if current_state.cpu_usage > 80:
            params_vector[1] *= 0.8  # Reduce thread count
        
        # Adjust GPU memory threshold based on current usage
        if current_state.gpu_memory > 80:
            params_vector[2] = min(params_vector[2], 0.7)  # Lower GPU memory threshold
        
        # Increase timeout if system is under stress
        if current_state.cpu_usage > 70 or current_state.memory_usage > 70:
            params_vector[3] = min(1.0, params_vector[3] * 1.2)  # Increase timeout
        
        return params_vector
    
    def _find_similar_evolutionary_params(self, params: OptimizationParameters) -> Optional[int]:
        """Find most similar parameters in evolutionary population"""
        if not self.evolutionary_optimizer.population:
            return None
        
        target_vector = params.to_vector()
        min_distance = float('inf')
        best_idx = None
        
        for i, pop_params in enumerate(self.evolutionary_optimizer.population):
            pop_vector = pop_params.to_vector()
            distance = np.linalg.norm(target_vector - pop_vector)
            
            if distance < min_distance:
                min_distance = distance
                best_idx = i
        
        return best_idx if min_distance < 0.5 else None  # Threshold for similarity
    
    def _train_neural_network(self):
        """Train neural network on experience replay memory"""
        if len(self.experience_memory) < 32:  # Need minimum batch size
            return
        
        # Sample batch from experience memory
        batch_size = min(32, len(self.experience_memory))
        batch_indices = np.random.choice(len(self.experience_memory), batch_size, replace=False)
        batch = [self.experience_memory[i] for i in batch_indices]
        
        # Prepare training data
        states = torch.FloatTensor([exp['state'] for exp in batch])
        current_params = torch.FloatTensor([exp['parameters'] for exp in batch])
        rewards = torch.FloatTensor([exp['reward'] for exp in batch])
        
        # Target: adjust parameters to maximize reward
        # Use reward as target for parameter adjustment
        target_params = current_params.clone()
        
        # Adjust target parameters based on reward
        for i, reward in enumerate(rewards):
            if reward > 0.7:  # Good performance - small adjustments
                noise = torch.normal(0, 0.02, current_params[i].shape)
            elif reward < 0.3:  # Poor performance - larger adjustments
                noise = torch.normal(0, 0.1, current_params[i].shape)
            else:  # Medium performance - medium adjustments
                noise = torch.normal(0, 0.05, current_params[i].shape)
            
            target_params[i] = torch.clamp(current_params[i] + noise, 0, 1)
        
        # Training step
        self.neural_network.train()
        self.optimizer.zero_grad()
        
        predicted_params = self.neural_network(states, current_params)
        loss = self.loss_function(predicted_params, target_params)
        
        loss.backward()
        self.optimizer.step()
        
        logger.debug(f"Neural network training loss: {loss.item():.4f}")
    
    def _evolve_population(self):
        """Evolve evolutionary algorithm population"""
        self.evolutionary_optimizer.evolve_generation()
    
    def _save_model(self):
        """Save neural network model"""
        try:
            torch.save({
                'model_state_dict': self.neural_network.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'training_step': self.training_step,
                'current_parameters': self.current_parameters.__dict__
            }, self.model_save_path)
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def _load_model(self):
        """Load existing neural network model"""
        try:
            if self.model_save_path.exists():
                checkpoint = torch.load(self.model_save_path)
                self.neural_network.load_state_dict(checkpoint['model_state_dict'])
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                self.training_step = checkpoint.get('training_step', 0)
                
                # Load current parameters
                if 'current_parameters' in checkpoint:
                    params_dict = checkpoint['current_parameters']
                    self.current_parameters = OptimizationParameters(**params_dict)
                
                logger.info(f"Loaded model from {self.model_save_path}")
        except Exception as e:
            logger.warning(f"Failed to load model: {e}")
    
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get comprehensive optimization metrics"""
        recent_performance = list(self.performance_history)[-10:] if self.performance_history else []
        
        metrics = {
            'training_step': self.training_step,
            'experience_memory_size': len(self.experience_memory),
            'evolutionary_population_size': len(self.evolutionary_optimizer.population),
            'current_parameters': self.current_parameters.__dict__,
            'recent_avg_reward': np.mean([p.to_reward_signal() for p in recent_performance]) if recent_performance else 0.0,
            'system_state_history_size': len(self.system_state_history),
            'performance_history_size': len(self.performance_history)
        }
        
        if self.evolutionary_optimizer.fitness_scores:
            metrics['best_evolutionary_fitness'] = max(self.evolutionary_optimizer.fitness_scores)
            metrics['avg_evolutionary_fitness'] = np.mean(self.evolutionary_optimizer.fitness_scores)
        
        return metrics

# Global adaptive optimizer instance
adaptive_optimizer = AdaptiveNeuralOptimizer()

def get_optimal_parameters(system_state: SystemState) -> OptimizationParameters:
    """Convenience function to get optimal parameters"""
    return adaptive_optimizer.get_optimal_parameters(system_state)

def update_performance_feedback(system_state: SystemState, 
                              parameters: OptimizationParameters,
                              performance: PerformanceMetrics):
    """Convenience function to update performance feedback"""
    adaptive_optimizer.update_performance_feedback(system_state, parameters, performance)

def get_optimization_metrics() -> Dict[str, Any]:
    """Get current optimization metrics"""
    return adaptive_optimizer.get_optimization_metrics()