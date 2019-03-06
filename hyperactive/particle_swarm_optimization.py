'''
MIT License
Copyright (c) [2018] [Simon Franz Albert Blanke]
Email: simonblanke528481@gmail.com
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import os
import sys
import time
import random as rnd
import numpy as np
import pandas as pd


from .base import BaseOptimizer


class ParticleSwarm_Optimizer(BaseOptimizer):

	def __init__(self, ml_search_dict, n_searches, scoring, n_particles=1, n_jobs=1, cv=5, verbosity=0):
		super().__init__(ml_search_dict, n_searches, scoring, n_jobs, cv, verbosity)
		self._search = self._start_particle_swarm_optimization

		self.ml_search_dict = ml_search_dict
		self.n_searches = n_searches
		self.scoring = scoring
		
		self.n_particles = n_particles

		self.best_model = None
		self.best_score = 0
		self.best_pos = None
		self.best_hyperpara_dict = None
		self.best_train_time = None

	def _find_best_particle(self):
		for p in self.p_list:
			if p.best_score > self.best_score:
				self.best_score = p.best_score
				self.best_pos = p.best_pos


	def _init_particles(self):
		self.p_list = [Particle() for _ in range(self.n_particles)]
		for p in self.p_list:
			p.pos = self._pos_dict2np_array(self._get_random_position())
			p.best_pos = self._pos_dict2np_array(self._get_random_position())
			p.velo = np.zeros(self._get_dim_SearchSpace())


	def _move_particles(self):
		W = 0.5
		c1 = 0.8
		c2 = 0.9
		for p in self.p_list:
			A = W * p.velo
			B = c1 * rnd.random() * np.subtract(p.best_pos, p.pos)
			C = c2 * rnd.random() * np.subtract(self.best_pos, p.pos)
			new_velocity = A + B + C
			p.velo = new_velocity
			p.move()


	def _eval_particles(self):
		for p in self.p_list:
			print('\n---------------p.pos;', p.pos)

			pos = self._limit_pos(p.pos)

			hyperpara_dict = self._pos_np2values_dict(pos)
			p.best_score, p.train_time, p.sklearn_model = self._train_model(hyperpara_dict)


	def _start_particle_swarm_optimization(self, n_searches):
		n_steps = int(self.n_searches/self.n_jobs)

		self._init_particles()
		for i in range(n_steps):
			print('\nstep:', i, '\n')
			self._eval_particles()
			self._find_best_particle()
			self._move_particles()

		hyperpara_dict_best = self._pos_np2values_dict(self.best_pos)
		score_best, train_time, sklearn_model = self._train_model(hyperpara_dict_best)

		return sklearn_model, score_best, hyperpara_dict_best, train_time



class Particle():
	def __init__(self):
		self.pos = None
		self.velo = None
		self.best_pos = None

		self.best_score = None
		self.train_time = None
		self.sklearn_model = None


	def move(self):
		self.pos = (self.pos + self.velo).astype(int)




