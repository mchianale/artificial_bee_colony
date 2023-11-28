# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 16:35:06 2023

@author: Matteo
"""

from abc import abstractmethod
import numpy as np
from deap.benchmarks import schwefel

class Goal(object):
  def __init__(self,name,dim, min, max):
    self.name = name
    self.dim = dim
    self.min = min
    self.max = max

  @abstractmethod
  def evaluate(self, x):
        pass
    
    
"""
if you ton implement your own objectif function
class NameClass(Goal):
    def __init__(self, dim):
        super(NameClass, self).__init__('name', dim, min, max)

    def evaluate(self, x):
        return your_function(x)
"""
    
class Rastrigin(Goal):

    def __init__(self, dim):
        super(Rastrigin, self).__init__('Rastrigin', dim, -5.12, 5.12)

    def evaluate(self, x):
        return 10 * len(x)\
        + np.sum(np.power(x, 2) - 10 * np.cos(2 * np.pi * np.array(x)))
        
class Sum(Goal):
    def __init__(self, dim):
        super(Sum, self).__init__('Sum', dim, -10, 10)

    def evaluate(self, x):
        return np.sum(x)
    
class Schwefel(Goal):

    def __init__(self, dim):
        super(Schwefel, self).__init__('Schwefel', dim, -500.0, 500.0)

    def evaluate(self, x):
        return schwefel(x)[0]


class MyFunction(Goal):

    def __init__(self):
        super(MyFunction, self).__init__('My Function', 2, -5, 5)
        
    def evaluate(self, x):
        return x[0]**2 - x[0]*x[1] + x[1]**2 + 2*x[0] + 4*x[1] + 3
    

    
    