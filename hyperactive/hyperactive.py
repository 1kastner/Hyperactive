# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import time
import warnings

from .main_args import MainArgs
from .opt_args import Arguments

from . import (
    HillClimbingOptimizer,
    StochasticHillClimbingOptimizer,
    TabuOptimizer,
    RandomSearchOptimizer,
    RandomRestartHillClimbingOptimizer,
    RandomAnnealingOptimizer,
    SimulatedAnnealingOptimizer,
    StochasticTunnelingOptimizer,
    ParallelTemperingOptimizer,
    ParticleSwarmOptimizer,
    EvolutionStrategyOptimizer,
    BayesianOptimizer,
)


def stop_warnings():
    # because sklearn warnings are annoying when they appear 100 times
    def warn(*args, **kwargs):
        pass

    import warnings

    warnings.warn = warn


class Hyperactive:
    """
    Optimization main class.
    """

    def __init__(self, X, y, memory=True, random_state=1, verbosity=3, warnings=False):
        """

        Parameters
        ----------
            X: array-like or None
                Training input samples used during the optimization process.
                The training data is passed to the ``X`` argument in the objective function during the optimization process.
                You can also pass ``None`` if you want to optimize an objective function that does not contain a machine learning model.

            y: array-like or None
                Training target values used during the optimization process.
                The target values are passed to the ``y`` argument in the objective function during the optimization process.
                You can also pass ``None`` if you want to optimize an objective function that does not contain a machine learning model.

            memory: bool, optional (default: True)
                Collects and reuses evaluation information during optimization.

            random_state: **int, optional (default: 1)**

                The seed of the pseudo random number generator.

            verbosity: **int, optional (default: 3)**
                How much information Hyperactive provides during the optimization process

                - 0 -> No information from Hyperactive.
                - 1 -> Prints scores and positions of best evaluation after optimization.
                - 2 -> Adds progress bar(s) with minimal information.
                - 3 -> Adds current best score and iteration number of current best score to progress bar information.

            warnings: **bool, optional (default: False)**
                Disables warnings (like deprecation warnings) during optimization:
                Warnings can be very intrusive, since they are often printed during each model evaluation.
        """
        self.X = X
        self._main_args_ = MainArgs(X, y, memory, random_state, verbosity)

        if not warnings:
            stop_warnings()

        self.optimizer_dict = {
            "HillClimbing": HillClimbingOptimizer,
            "StochasticHillClimbing": StochasticHillClimbingOptimizer,
            "TabuSearch": TabuOptimizer,
            "RandomSearch": RandomSearchOptimizer,
            "RandomRestartHillClimbing": RandomRestartHillClimbingOptimizer,
            "RandomAnnealing": RandomAnnealingOptimizer,
            "SimulatedAnnealing": SimulatedAnnealingOptimizer,
            "StochasticTunneling": StochasticTunnelingOptimizer,
            "ParallelTempering": ParallelTemperingOptimizer,
            "ParticleSwarm": ParticleSwarmOptimizer,
            "EvolutionStrategy": EvolutionStrategyOptimizer,
            "Bayesian": BayesianOptimizer,
        }

    def search(
        self,
        search_config,
        n_iter=10,
        max_time=None,
        optimizer="RandomSearch",
        n_jobs=1,
        warm_start=False,
        scatter_init=False,
    ):
        """
        Starts the optimization run.

        Parameters
        ----------
        search_config: dictionary
            Defines the search space and links it to the objective function.
            The objective function is the key of the dictionary, while the search space (which is also a dictionary) is the value.
            You can define multiple modeles/search-spaces in the search_config.
            The values within the search space (not search_config) must be lists or numpy arrays.

        n_iter: int, optional (default: 10)
            Number of iterations.

        max_time: float, optional (default: None)
            Maximum time in hours to run the optimization.

        optimizer: string or dict, optional (default: "RandomSearch")
            Optimization strategy used during the run.

        n_jobs: int, optional (default: 1)
            Number of jobs to run.

        """

        start_time = time.time()

        self._main_args_.search_args(
            search_config, max_time, n_iter, optimizer, n_jobs, warm_start, scatter_init
        )
        self._opt_args_ = Arguments(self._main_args_.opt_para)
        optimizer_class = self.optimizer_dict[self._main_args_.optimizer]

        try:
            import ray

            if ray.is_initialized():
                ray_ = True
            else:
                ray_ = False
        except ImportError:
            warnings.warn("failed to import ray", ImportWarning)
            ray_ = False

        if ray_:
            optimizer_class = ray.remote(optimizer_class)
            opts = [
                optimizer_class.remote(self._main_args_, self._opt_args_)
                for job in range(self._main_args_.n_jobs)
            ]
            searches = [
                opt.search.remote(job, ray_=ray_) for job, opt in enumerate(opts)
            ]
            ray.get(searches)
        else:
            self._optimizer_ = optimizer_class(self._main_args_, self._opt_args_)
            self._optimizer_.search()

        self.results_params = self._optimizer_.results_params
        self.results_models = self._optimizer_.results_models

        self.pos_list = self._optimizer_.pos_list
        self.score_list = self._optimizer_.score_list

        self.total_time = time.time() - start_time

    def get_total_time(self):
        return self.total_time

    def get_eval_time(self):
        return self._optimizer_.eval_time

    def save_report(self):
        pass
