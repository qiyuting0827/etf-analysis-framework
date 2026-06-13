"""
Genetic algorithm optimization
"""

import numpy as np
from typing import Dict, List, Any, Callable, Tuple, Optional
from etf_framework.optimization.base import Optimizer, OptimizationResult
import logging

logger = logging.getLogger(__name__)


class GeneticAlgorithm(Optimizer):
    """
    Genetic Algorithm for strategy optimization
    """
    
    def __init__(
        self,
        population_size: int = 50,
        generations: int = 20,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        **kwargs
    ):
        """
        Initialize Genetic Algorithm
        
        Args:
            population_size: Population size
            generations: Number of generations
            mutation_rate: Mutation rate
            crossover_rate: Crossover rate
            **kwargs: Additional config
        """
        super().__init__(name='GeneticAlgorithm', **kwargs)
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
    
    def optimize(
        self,
        objective_func: Callable,
        param_space: Dict[str, Tuple[float, float]],
        maximize: bool = True,
    ) -> OptimizationResult:
        """
        Run genetic algorithm optimization
        
        Args:
            objective_func: Objective function
            param_space: Parameter space with bounds
            maximize: Maximize or minimize
            
        Returns:
            OptimizationResult
        """
        logger.info("Starting Genetic Algorithm optimization")
        
        param_names = list(param_space.keys())
        param_bounds = [param_space[name] for name in param_names]
        
        all_results = []
        best_score = float('-inf') if maximize else float('inf')
        best_params = None
        
        # Initialize population
        population = self._initialize_population(param_bounds)
        fitness_scores = []
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                params = dict(zip(param_names, individual))
                score = self._evaluate_objective(objective_func, params)
                fitness_scores.append(score)
                all_results.append({'params': params, 'score': score})
                self.history.append((params.copy(), score))
                
                # Update best
                if maximize:
                    if score > best_score:
                        best_score = score
                        best_params = params.copy()
                else:
                    if score < best_score:
                        best_score = score
                        best_params = params.copy()
            
            logger.info(f"Generation {generation + 1}/{self.generations} - Best Score: {best_score:.4f}")
            
            # Selection and breeding
            population = self._evolve_population(
                population, fitness_scores, param_bounds, maximize
            )
        
        logger.info(f"Genetic algorithm completed. Best score: {best_score:.4f}")
        
        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            all_results=all_results,
            history=self.history,
        )
    
    def _initialize_population(
        self,
        param_bounds: List[Tuple[float, float]],
    ) -> List[List[float]]:
        """
        Initialize random population
        """
        population = []
        for _ in range(self.population_size):
            individual = []
            for min_val, max_val in param_bounds:
                if isinstance(min_val, int):
                    individual.append(float(np.random.randint(min_val, max_val + 1)))
                else:
                    individual.append(np.random.uniform(min_val, max_val))
            population.append(individual)
        return population
    
    def _evolve_population(
        self,
        population: List[List[float]],
        fitness_scores: List[float],
        param_bounds: List[Tuple[float, float]],
        maximize: bool = True,
    ) -> List[List[float]]:
        """
        Evolve population through selection, crossover, and mutation
        """
        # Normalize fitness scores
        fitness_array = np.array(fitness_scores)
        if not maximize:
            fitness_array = -fitness_array
        
        fitness_array = fitness_array - np.min(fitness_array) + 1e-6
        probabilities = fitness_array / np.sum(fitness_array)
        
        # Selection
        new_population = []
        for _ in range(self.population_size // 2):
            parent1_idx = np.random.choice(len(population), p=probabilities)
            parent2_idx = np.random.choice(len(population), p=probabilities)
            
            parent1 = population[parent1_idx]
            parent2 = population[parent2_idx]
            
            # Crossover
            if np.random.random() < self.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1[:], parent2[:]
            
            # Mutation
            child1 = self._mutate(child1, param_bounds)
            child2 = self._mutate(child2, param_bounds)
            
            new_population.extend([child1, child2])
        
        return new_population[:self.population_size]
    
    def _crossover(
        self,
        parent1: List[float],
        parent2: List[float],
    ) -> Tuple[List[float], List[float]]:
        """
        Single-point crossover
        """
        crossover_point = np.random.randint(1, len(parent1))
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2
    
    def _mutate(
        self,
        individual: List[float],
        param_bounds: List[Tuple[float, float]],
    ) -> List[float]:
        """
        Mutation operation
        """
        mutated = individual[:]
        for i in range(len(mutated)):
            if np.random.random() < self.mutation_rate:
                min_val, max_val = param_bounds[i]
                if isinstance(min_val, int):
                    mutated[i] = float(np.random.randint(min_val, max_val + 1))
                else:
                    mutated[i] = np.random.uniform(min_val, max_val)
        return mutated
