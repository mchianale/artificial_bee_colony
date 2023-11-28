# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 16:40:17 2023

@author: Matteo
"""

import random
import pandas as pd
import matplotlib.pyplot as plt
from Goal import *
import Goal

def fit(eval):
  if eval >= 0:
    return 1/(1+eval)
  else:
    return 1 + abs(eval)

class FoodSource(object):
    def __init__(self,goal_fun):
        self.source = np.array([random.uniform(goal_fun.min, goal_fun.max) for _ in range(goal_fun.dim)])
        self.goal_fun = goal_fun
        self.eval = goal_fun.evaluate(self.source)
        self.fitness = fit(self.eval)
        self.trial = 0

    def updateLocationRandom(self):
        """used for scout phase """
        self.source = np.array([random.uniform(self.goal_fun.min, self.goal_fun.max) for _ in range(self.goal_fun.dim)])
        self.eval = self.goal_fun.evaluate(self.source)
        self.fitness = fit(self.eval)
        self.trial = 0
        
    def updateLocation(self, partner):
        """ from a partner FoodSource input, we update the FoodSource if the new one gets a better fitness,
        """
        #select the random variable to change
        index = random.randint(0, len(self.source)-1)
        r = random.random()
        while r == 0:
            r = random.uniform(-1, 1)
        new_xi = self.source[index] + r*(self.source[index] + partner.source[index])
        if new_xi < self.goal_fun.min: 
            #we cheat and give to new_xi a new value based of its range
            new_xi = r*self.goal_fun.min
        elif new_xi > self.goal_fun.max: 
            #we cheat and give to new_xi a new value based of its range
            new_xi = r*self.goal_fun.max

        #new location
        new_source = self.source.copy()
        new_source[index] = new_xi
        new_eval = self.goal_fun.evaluate(new_source)
        new_fitness = fit(new_eval)
        #greedy selection
        if new_fitness < self.fitness:
            #update
            self.source = new_source
            self.eval = new_eval
            self.fitness = new_fitness
            self.trial = 0
        else:
            self.trial += 1
    
class ABC(object):
    def __init__(self, goal_fun, colony_size, max_iter, limit):
        self.goal_fun = goal_fun
        self.colony_size = colony_size
        self.max_iter = max_iter
        self.limit = limit
        self.sources = [FoodSource(goal_fun) for i in range(colony_size)]
        self.best_solution = None
        self.best_answer = None

    def display(self):
        """ create a dataframe of our abc problem"""
        data = {}
        for i in range(self.goal_fun.dim):
            label = 'x' + str(i+1)
            data[label] = [source.source[i] for source in self.sources]
            
        data['f(x)'] =  [source.eval for source in self.sources]
        data['fitness'] =  [source.fitness for source in self.sources]
        data['trial'] = [source.trial for source in self.sources]
        display(pd.DataFrame(data))

    def displayAnswer(self):
        """ display the solution and answer to the solution"""
        print('best answer :')
        ans = ''
        for i, a in enumerate(self.best_answer):
            ans += 'x' + str(i) + ' : ' + str(a) + ' , '
        print(ans[:len(ans)-3])
        print('best solution f(x) = ', self.best_solution)
        print('\n')
      
    def updateBest(self):
        """ catch the actual best solution and its answer, don't update if the previous is better"""
        total_eval = np.array([source.eval for source in self.sources])
        if not self.best_solution:
            #first solution
            self.best_solution =  total_eval.max()
            self.best_answer = self.sources[np.where(total_eval == self.best_solution)[0][0]].source
            
        if total_eval.max() > self.best_solution:
            #update the current solution else we keep the previous
            self.best_solution =  total_eval.max()
            self.best_answer = self.sources[np.where(total_eval == self.best_solution)[0][0]].source

    def employed_phase(self):
        """create a new solution for each food location"""
        for i in range(self.colony_size):
            #select random partner, need to be different that the current food source explore 
            index = random.randint(0, len(self.sources)-1)
            while index == i:
                index = random.randint(0, len(self.sources)-1)
            
            self.sources[i].updateLocation(self.sources[index])

    def onlooker_phase(self):
        """create a new solution for each food location if the condition is valid,
          cond : r (random number between 0 and 1) < prob = fitness of source i / sum of all fitness"""
        total_fit = np.array([source.fitness for source in self.sources]).sum()
        prob = [source.fitness  / total_fit  for source in self.sources]
        i = 0
        n_update = 0
        #we have to update n times, n = size of the colony
        while n_update < self.colony_size:
            r = random.random()
            if r < prob[i]:
                #select random partner, need to be different that the current food source explore 
                index = random.randint(0, len(self.sources)-1)
                while index == i:
                  index = random.randint(0, len(self.sources)-1)
                self.sources[i].updateLocation(self.sources[index])
                #we count like update even if the source didn't change
                n_update += 1
                
            i = (i+1) % self.colony_size

    def scout_phase(self):
        """ forced to update food source with a trial > limit"""
        for i in range(self.colony_size):
            if self.sources[i].trial >= self.limit:    
                 self.sources[i].updateLocationRandom()

    def optimize(self, displayAll=False,displayAns=True, convergence=None):
        """ run all the algo, if displayAll is set to True, 
        each iteration will be display
        If displayAns is set to False, the answer will not be display
        """
        if displayAll:
            print('iteration {} :'.format(0))
            self.display()
            print('\n')
            
        if convergence:
            mean_fitness_iter = np.array([source.fitness for source in self.sources]).mean()
            fitness_iter = [mean_fitness_iter]
            convergence_point = None
                
        for i in range(self.max_iter):
            self.employed_phase()
            self.onlooker_phase()
            self.updateBest()
            self.scout_phase()
              
            if convergence:
                mean_fitness_iter = np.array([source.fitness for source in self.sources]).mean()
                fitness_iter.append(mean_fitness_iter)
                if abs(fitness_iter[i] - fitness_iter[i - 1]) < convergence:
                    if not convergence_point:
                        convergence_point = [mean_fitness_iter, i]
              
            if displayAll:
                print('iteration {} :'.format(i+1))
                self.display()
                print('\n')
        
        if convergence:
            iterations = np.arange(0, self.max_iter+1)
            plt.plot(iterations, fitness_iter, marker='.', linestyle='-')
            plt.xlabel('Iterations')
            plt.ylabel('Mean of fitness values')
            plt.title('Output Mean Of Fitness Values Over Iterations')
            if convergence_point:
                label = 'Convergence Point at iteration : ' + str(convergence_point[1]) + ', value : ' + str(convergence_point[0])
                plt.scatter(convergence_point[1], convergence_point[0], color='red', label=label)
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            plt.show()
            
        if displayAns:
            self.displayAnswer()
            
        return self.best_answer, self.best_solution



    def optimize_displayALL(self, convergence=1e-6):
        """ Display each step, answer and convergence plot"""
        size_ = 100
        print(''.join(['' + '-' for i in range(size_)]))
        print('ITERATION {} :'.format(0))
        self.display()
        print('\n')
            
        mean_fitness_iter = np.array([source.fitness for source in self.sources]).mean()
        fitness_iter = [mean_fitness_iter]
        convergence_point = None
                
        for i in range(self.max_iter):
            print(''.join(['' + '-' for i in range(size_)]))
            print('ITERATION {} :'.format(i+1))
              
            print('EMPLOYED PHASE :')
            self.employed_phase()
            self.display()
            print('\n')
              
            print('ONLOOKER Phase :')
            self.onlooker_phase()
            self.display()
            print('\n')
              
            self.updateBest()
              
            print('SCOUT Phase :')
            self.scout_phase()
            self.display()
            print('\n')
              
              
            mean_fitness_iter = np.array([source.fitness for source in self.sources]).mean()
            fitness_iter.append(mean_fitness_iter)
            if abs(fitness_iter[i] - fitness_iter[i - 1]) < convergence:
                if not convergence_point:
                    convergence_point = [mean_fitness_iter, i]
              
            print('FINAL :')
            self.display()
            print('\n')
            
        iterations = np.arange(0, self.max_iter+1)
        plt.plot(iterations, fitness_iter, marker='.', linestyle='-')
        plt.xlabel('Iterations')
        plt.ylabel('Mean of fitness values')
        plt.title('Output Mean Of Fitness Values Over Iterations')
        if convergence_point:
            label = 'Convergence Point at iteration : ' + str(convergence_point[1]) + ', value : ' + str(convergence_point[0])
            plt.scatter(convergence_point[1], convergence_point[0], color='red', label=label)
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()

        self.displayAnswer()
        return self.best_answer, self.best_solution

