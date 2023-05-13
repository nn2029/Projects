import copy
import numpy as np
from numpy.random import randint
import matplotlib.pyplot as plt
from optproblems import cec2005
from optproblems import Individual
np.random.seed(32)

# PSO Algorithm
class Particles:
    # Class for particle generation
    def __init__(self, dimensions, population, bounds, obj_func):
        self.dims = dimensions  # Number of Dimensions
        self.pop = population  # Population size
        self.bounds = bounds  # Upper and Lower thresholds
        self.obj_func = obj_func  # Objective function

    def candidate_solutions(self):
        # Generating a population of candidate solutions/ particles
        solutions = [Individual([np.random.uniform(self.bounds[0], self.bounds[1]) for _ in range(self.dims)])
                     for _ in range(self.pop)]
        self.obj_func.batch_evaluate(solutions)
        return solutions


# Function to handle boundary violations in a dimension
def bound_dims_reflect(value, minimum_bound, maximum_bound):
    # Bounded Mirror Method
    # Prosposed by Helwig et. al in Experimental Analysis of Bound Handling Techniques in Particle Swarm Optimization [4]
    bounded_mirror_range = 2 * (maximum_bound - minimum_bound)
    if abs(value - minimum_bound) > bounded_mirror_range:
        value = minimum_bound + np.fmod(abs(value - minimum_bound), bounded_mirror_range)
    max_boundary_violated = value > maximum_bound  # Max Boundary violation
    min_boundary_violated = value < minimum_bound  # Min Boundary violation
    # Reflection Method
    # Prosposed by Helwig et. al in Experimental Analysis of Bound Handling Techniques in Particle Swarm Optimization [4]
    while min_boundary_violated or max_boundary_violated:
        if max_boundary_violated:
            value = maximum_bound - (value - maximum_bound)
        elif min_boundary_violated:
            value = minimum_bound + (minimum_bound - value)
        max_boundary_violated = value > maximum_bound
        min_boundary_violated = value < minimum_bound
    return value


# Creating a class to handle bounds

class BoundsHandling:
    def __init__(self, particle, minimum_bound, maximum_bound):
        self.particle = particle
        self.minimum = minimum_bound
        self.maximum = maximum_bound

    # Method to handle bounds in particles
    def bound_particles_reflect(self):
        # Creating a copy of the particle to be reflected through bounded mirror
        self.particle = copy.deepcopy(self.particle)
        for i, _ in enumerate(self.particle):
            self.particle[i] = bound_dims_reflect(self.particle[i], self.minimum, self.maximum)
        return self.particle


class PSO:
    # Class for Particle Swarm Optimization
    def __init__(self, iters, pop_size, dimensions, informant_size, bounds, func):
        self.max_iters = iters  # Max iterations allowed to reach global minima
        self.pop_size = pop_size  # Population of objective function particles
        self.dims = dimensions  # Dimensions in objective function
        self.obj_func = func  # Objective Function for fitness evaluation
        if informant_size > self.pop_size:  # Ensuring informant's do not exceed population
            self.informants_size = self.pop_size
        elif informant_size < 0:  # Ensuring there is at least one informant for population
            self.informants_size = 1
        else:
            self.informants_size = informant_size
        self.bounds = bounds  # Objective Function bounds
        # Particles are initially set to none until initialization
        self.particles = None
        self.velocities = None
        self.p_best_position = None
        self.p_best = None
        self.l_best_position = []
        self.l_best = []
        self.g_best_position = None
        self.g_best = None

    # PSO initialization method
    def initialize(self):
        particle_sols = Particles(self.dims, self.pop_size, self.bounds, self.obj_func)  # Initialize particles class
        solutions = particle_sols.candidate_solutions()  # Initialize candidate solutions
        self.particles = [particle.phenome for particle in solutions]     # Initialize particles
        self.velocities = np.zeros((self.pop_size, self.dims)).tolist()   # Initialize velocities
        self.p_best_position = [particle.phenome for particle in solutions]  # Initial particle's best positions
        self.p_best = [particle.objective_values for particle in solutions]  # Initial particle's best fitness values
        # Informants will be a subset of particles
        self.l_best = [particle.objective_values for particle in solutions]
        self.l_best_position = [particle.phenome for particle in solutions]
        # Assessing initial global best fitness and particle position
        for i in range(len(self.p_best)):
            if (self.g_best is None) or (self.p_best[i] <= self.g_best):
                self.g_best = self.p_best[i]
                self.g_best_position = self.p_best_position[i]

    def optimize(self, alpha, beta, gamma, delta, epsilon_decay=False, verbose=True):
        # Method to carry out optimization with Inertia weight, Cognitive Weight, Social Weight and Global Weight
        iterations = 0
        iterations_list = []
        g_best_list = []
        #  step size for informants as a subset of the particles
        informant_index_step_size = self.pop_size // self.informants_size
        # Position update step size
        epsilon = 0.9
        # Calculating global optimum value for the specified function
        global_optima = self.obj_func.get_optimal_solutions()
        for opt in global_optima:
            opt.objective_values
        self.obj_func.batch_evaluate(global_optima)
        # Iterative optimization
        while iterations < self.max_iters:
            informant_index = 0
            # Particle loop
            for p in range(self.pop_size):
                # Dimension Loop
                for d in range(self.dims):
                    # Random Numbers for velocity control
                    c1 = np.random.uniform(0, 1)
                    c2 = np.random.uniform(0, 1)
                    c3 = np.random.uniform(0, 1)
                    # A constant to limit the minimum and maximum velocity in a dimension
                    velocity_limiter = 1
                    # Velocity update
                    self.velocities[p][d] = self.velocities[p][d] = (alpha * self.velocities[p][d]) + \
                    (beta * c1 * (self.p_best_position[p][d] - self.particles[p][d])) + \
                    (gamma * c2 * (self.l_best_position[informant_index][d] - self.particles[p][d])) + \
                    (delta * c3 * (self.g_best_position[d] - self.particles[p][d]))
                    # Particle update
                    self.particles[p][d] = self.particles[p][d] + (epsilon * self.velocities[p][d])
                    # Boundary violation handling
                    if (self.particles[p][d] < self.bounds[0]) or (self.particles[p][d] > self.bounds[1]):
                        bh = BoundsHandling(self.particles[p], self.bounds[0], self.bounds[1])
                        self.particles[p] = bh.bound_particles_reflect()
                    # Maximum and Minimum velocity handling
                    if self.velocities[p][d] > velocity_limiter * (abs(self.bounds[1] - self.bounds[0])):
                        self.velocities[p][d] = velocity_limiter * (abs(self.bounds[1] - self.bounds[0]))
                    if self.velocities[p][d] < -velocity_limiter * (abs(self.bounds[1] - self.bounds[0])):
                        self.velocities[p][d] = -velocity_limiter * (abs(self.bounds[1] - self.bounds[0]))
                # Informants are a subset of particles that are the specified step size away from each other
                if ((p + 1) % informant_index_step_size == 0) and (informant_index != len(self.l_best_position)):
                    informant_index += informant_index_step_size
            # Fitness evaluation of new particle positions
            for particle, i in zip(self.particles, range(self.pop_size)):
                particle = Individual(particle)
                self.obj_func.evaluate(particle)
                if particle.objective_values <= self.g_best:
                    self.g_best = particle.objective_values
                    self.g_best_position = particle.phenome
                if particle.objective_values <= self.p_best[i]:
                    self.p_best[i] = particle.objective_values
                    self.p_best_position[i] = particle.phenome
            # Fitness evaluation of informants
            for i in range(0, self.pop_size, (self.pop_size // self.informants_size)):
                informant_sol = Individual(self.particles[i])
                self.obj_func.evaluate(informant_sol)
                if informant_sol.objective_values <= self.l_best[i]:
                    self.l_best[i] = informant_sol.objective_values
                    self.l_best_position[i] = informant_sol.phenome
            # Particle step size decrease
            if epsilon_decay:
                epsilon -= 0.005
                if epsilon < 0.4:
                    epsilon = 0.4
            # Break operation if 1 away from global optimum of the function
            if self.g_best - opt.objective_values <= 1:
                break
            # Global best discovered over each iteration
            if verbose:
                print(f"{iterations + 1}/{self.max_iters} = {self.g_best}")
            iterations_list.append(iterations)
            g_best_list.append(self.g_best)
            iterations += 1
        # Summary of PSO with best fitness and particle position
        if verbose:
            print("\nThe best fitness evaluated was", self.g_best,'\n')
            print("The best particle location was :", '\n')
            print(self.g_best_position, '\n')
            print('Iterations :', iterations, '\n')
        return iterations_list, g_best_list, self.g_best

# F1 Benchmark Function
f1_best_list_pso100 = []
optimizer1_pso = None
for i in range(10):
    f1 = cec2005.F1(10)
    pso = PSO(iters=1000, pop_size=100, dimensions=10, informant_size=50, bounds=(-100, 100), func=f1)
    pso.initialize()
    optimizer = pso.optimize(alpha=0.9, beta=0.1, gamma=0.2, delta=0.7, verbose=False)
    f1_best_list_pso100.append(optimizer[2])
    optimizer1_pso = optimizer
f1_mean_pso100 = np.mean(f1_best_list_pso100)
print('Average Global Optima for F1 with PSO after a 1000 iterations with population 100 over 10 runs for PSO :', f1_mean_pso100, '\n')

