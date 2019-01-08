import json
import datetime
import random

from collections import namedtuple

import numpy as np

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

__MAGIC__ = 142

Ingredient = namedtuple("Ingredient", ('name', 'quantity', 'unit', 'calories', 'proteins', 'carbohydrates', 'fats'))
Target = namedtuple('Target', ['proteins', 'carbohydrates', 'fats', 'calories'])

def mutation_operator(ind, indpb=0.05):
    for idx, bit in enumerate(ind):
        if np.random.random() <= indpb:
            ind[idx] = np.random.random()
    return (ind,)

def crossover(ind1, ind2):
  
    size = len(ind1)
    cxpoint1 = random.randint(1, size)
    cxpoint2 = random.randint(1, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else: # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1

    ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] \
        = ind2[cxpoint1:cxpoint2].copy(), ind1[cxpoint1:cxpoint2].copy()
        
    return (ind1, ind2)


def score(ingredient_list, target, lockers, genome):
    n_ingredients = len(ingredient_list)
    proteins_sum = 0
    carbohydrates_sum = 0
    fats_sum = 0
    calories_sum = 0
    error = 0.0

    ## Replace the alleles that are locked in the the genome
    if lockers:
        for idx in range(len(genome)):
            if lockers[idx]:
                genome[idx] = lockers[idx] / ingredient_list[idx].quantity 
    
    #print(genome, ingredient_list, target)
    for idx, ingredient in enumerate(ingredient_list):
        proteins_sum += genome[idx] * ingredient.proteins
        carbohydrates_sum += genome[idx] * ingredient.carbohydrates
        fats_sum += genome[idx] * ingredient.fats
        calories_sum += genome[idx] * ingredient.calories

    error += target.proteins*(proteins_sum - target.proteins)**2 
    error += target.carbohydrates * (carbohydrates_sum - target.carbohydrates)**2
    error += target.fats*(fats_sum - target.fats)**2
    error += (calories_sum - target.calories)**2

    error -= proteins_sum
    
    
    return (error,)
    
    ## @todo: use required argument




class ThisIsMadness():
    def __init__(self, ingredients, target, lockers=None):

        n_ingredients = len(ingredients)
        self.ingredients = ingredients
        self.lockers = lockers
        creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()
        self.toolbox.register("generate_random_bit", lambda : __MAGIC__*random.random())
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.generate_random_bit, n=n_ingredients)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("mate", crossover)
        self.toolbox.register("mutate", mutation_operator, indpb=0.05)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("evaluate", score, self.ingredients, target, self.lockers)

        self.pop = self.toolbox.population(n=500)

    def solve(self):
        random.seed(64)

        # Numpy equality function (operators.eq) between two arrays returns the
        # equality element wise, which raises an exception in the if similar()
        # check of the hall of fame. Using a different equality function like
        # numpy.array_equal or numpy.allclose solve this issue.
        self.hof = tools.HallOfFame(1, similar=np.array_equal)

        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", np.mean)
        self.stats.register("std", np.std)
        self.stats.register("min", np.min)
        self.stats.register("max", np.max)

        algorithms.eaSimple(self.pop, self.toolbox, cxpb=0.5, mutpb=0.2, ngen=100, stats=self.stats,
                            halloffame=self.hof)

        self.quantities = list()
        for idx, ingredient in enumerate(self.ingredients):
            if self.lockers and self.lockers[idx]:
                self.quantities.append(self.lockers[idx])
            else:
                self.quantities.append(self.hof.items[0][idx])
                self.quantities[idx] *= ingredient.quantity 

        
        self.macros = list(
            map(
                lambda x: int(x), 
                np.dot( 
                    self.hof.items[0], 
                    list(
                        map(
                            lambda x: [x.proteins, x.carbohydrates, x.fats, x.calories, ]
                            , self.ingredients
                        )
                    )
                )
            )
        )

        
        self.quantities = dict(zip(list(map(lambda x: x.name, self.ingredients)), self.quantities))
        self.macros = dict(zip(['proteins', 'carbohydrates', 'fats', 'calories'], self.macros))


def main(event, context):

    data = json.loads(event['body'])
    target_data = data['target']
    ingredients_data = data['ingredients']
    
    ingredients_all = list()

    for ingredient in ingredients_data:
        ingredients_all.append(Ingredient(**ingredient))

    target = Target(**target_data)
    
    p = ThisIsMadness(ingredients_all, target)
    p.solve()
    print(p.quantities)
    print(p.macros)

    
    body = {
        "target": target,
        "quantities": p.quantities,
        "macros": p.macros
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
