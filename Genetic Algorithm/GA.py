"""" Genetic Algorithm Implementation Based on a tutorial on Simple Genetic Algorithm from
     https://machinelearningmastery.com/simple-genetic-algorithm-from-scratch-in-python/"""
import numpy as np
from numpy.random import randint , rand
from optproblems import cec2005 ,Individual
import matplotlib.pyplot as plt


# perform tournament selection
def tournament(pop, scores, k):
    #random selection
    rand_selection = randint(len(pop))
    for t in randint(0, len(pop), k-1):
        #check tournament winner
        if scores[t] < scores[rand_selection]:
            rand_selection = t
    return pop[rand_selection]

#function to perform one_point crossover operation
def crossover(p1, p2, cross_rate):
    c1 = Individual(phenome=p1.phenome)
    c2 = Individual(phenome=p2.phenome)

    if np.random.randint(1, 100) < cross_rate:
        # selecting crossover at midpoint
        pt = int(len(p1.phenome)/2)
        # perform crossover
        c1 = Individual(phenome= np.append(p1.phenome[:pt] , p2.phenome[pt:]))
        c2 = Individual(phenome= np.append(p2.phenome[:pt] , p1.phenome[pt:]))
    return [c1, c2]


# function to perform mutation
def mutation(p, mut_rate, varmin, varmax):
    for i in range(len(p.phenome)):
        if np.random.randint(1, 100) < mut_rate:
            phenome = p.phenome
            # replace an existing value with a random value within specified bounds
            phenome[i] = round(np.random.uniform(varmin, varmax), 4)
            p.phenome = phenome


# function to perform genetic algorithm
def ga(func, bounds, num_dims, iters, pop_size, cross_rate, mut_rate , k):
    #defining the minimum and maximum bounds
    min = bounds[0]
    max = bounds[1]
    gen = 0
    num_iters = []
    best_list = []

    # initial population
    pop = [Individual(phenome=[round(np.random.uniform(min, max), 4) for _ in range(num_dims)]) for i in range(pop_size)]

    #store the best solutions
    best, best_eval = 0, func(pop[0].phenome)
    #number of generations to iterate
    for gen in range (iters):
        scores = [func(p.phenome) for p in pop]
        # check for new best solution in the population
        for i in range(pop_size):
            for i in range(len(scores)):
                if scores[i] < best_eval:
                    best, best_eval = pop[i], scores[i]
                    print(">%d, new best f(%s) = %f" % (gen + 1, pop[i].phenome, scores[i]))

        num_iters.append(gen)
        best_list.append(best_eval)
        # select parents for generation the new population
        selected = [tournament(pop, scores, k) for _ in range(pop_size)]
        # reproduction
        children = list()
        for i in range(0, pop_size, 2):
            # get selected parents in pairs
            p1, p2 = selected[i], selected[i + 1]
            # perform crossover and mutation
            for c in crossover(p1, p2, cross_rate): #crossover
                mutation(c, mut_rate, min, max) # mutation
                # store for next generation
                children.append(c)
        pop = children  # replace population with children
    return best ,best_eval


# define genetic algorithm parameters
num_dims = 10  # number of dimensions
bounds = [-100 , 100] #bounds
iters = 1000 #total iterations
pop_size = 100 #population size
k = 5 # number of individuals for tournament selection
cross_rate = 90 #crossover rate
mut_rate = 5 #mutation rate
func = cec2005.F1(10) #function to optimise 


# perform the genetic algorithm
best , score = ga(func, bounds, num_dims, iters, pop_size, cross_rate, mut_rate ,k = 5 )
print('\n Genetic Algorithm Search Completed \n Found Best Solution at: \n' 'f(%s) = %f' % (best.phenome , score))


