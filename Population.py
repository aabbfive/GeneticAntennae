import matplotlib.pyplot as plt
import numpy as np


class Population():
    """population of sets of antennae"""

    def __init__(self, grid, n_pop=25, n_antennae=5, default_power=0.2, p_cross=0.5, p_mutation=1, std_mutation=0.1,
                 n_generations=50):
        self.grid = grid
        self.NPOPULATION = n_pop
        self.NANTENNAE = n_antennae
        self.DEFAULT_POWER = default_power

        self.P_CROSSOVER = p_cross
        self.P_MUTATION = p_mutation
        self.MUTATION_STD = std_mutation

        self.r_antennae_population = np.ones((self.NPOPULATION, self.NANTENNAE, 2)) * \
                                     np.array([[[grid.xmax, grid.ymax]]]) / 2

        self.TEMP_ARRAY = np.zeros_like(self.r_antennae_population)

        self.n_generations = n_generations
        self.max_fitness_history = np.zeros(self.n_generations)
        self.mean_fitness_history = np.zeros(self.n_generations)
        self.std_fitness_history = np.zeros(self.n_generations)
        self.crossovers_history = np.zeros(self.n_generations)
        self.position_history = np.zeros(((self.n_generations, self.NPOPULATION, self.NANTENNAE, 2)))
        self.iteration = 0

    """ genetic operators """

    def selection(self):
        coverage_population = self.grid.antenna_coverage_population(self)

        utility_function_values = self.grid.utility_function(coverage_population)
        utility_function_total = utility_function_values.sum()

        utility_function_normalized = utility_function_values / utility_function_total
        dystrybuanta = utility_function_normalized.cumsum()
        random_x = np.random.random(self.NPOPULATION).reshape(1, self.NPOPULATION)

        new_r_antennae_population = self.TEMP_ARRAY
        # for i, x in enumerate(random_x.T):
        #     indeks = (x > dystrybuanta).sum()
        #     print(indeks)
        #     new_r_antennae_population[i] = r_antennae_population[indeks]
        selected_targets = (random_x > dystrybuanta.reshape(self.NPOPULATION, 1)).sum(axis=0)
        # print(selected_targets, utility_function_values, sep='\n')
        # print(utility_function_values.max(), utility_function_values.mean(), utility_function_values.std())

        new_r_antennae_population[...] = self.r_antennae_population[selected_targets]
        self.r_antennae_population[...] = new_r_antennae_population[...]
        self.max_fitness_history[self.iteration] = utility_function_values.max()
        self.mean_fitness_history[self.iteration] = utility_function_values.mean()
        self.std_fitness_history[self.iteration] = utility_function_values.std()

    def crossover_cutoff(self, ):
        self.TEMP_ARRAY[...] = self.r_antennae_population[...]
        number_crossovers_occurred = 0
        for i in range(0, self.NPOPULATION, 2):
            if i + 1 < self.NPOPULATION and np.random.random() < self.P_CROSSOVER:
                number_crossovers_occurred += 1
                cutoff = np.random.randint(0, self.NANTENNAE)
                a = self.r_antennae_population[i + 1]
                b = self.r_antennae_population[i]
                self.TEMP_ARRAY[i, cutoff:] = a[cutoff:]
                self.TEMP_ARRAY[i + 1, cutoff:] = b[cutoff:]
        self.r_antennae_population[...] = self.TEMP_ARRAY[...]
        self.crossovers_history[self.iteration] = number_crossovers_occurred

    def mutation(self):
        # TODO: implement 1/5 success rule or some other way
        which_to_move = (np.random.random((self.NPOPULATION, self.NANTENNAE)) < self.P_MUTATION)
        how_much_to_move = np.random.normal(scale=self.MUTATION_STD,
                                            size=(self.NPOPULATION, self.NANTENNAE, 2))
        self.r_antennae_population += which_to_move[..., np.newaxis] * how_much_to_move

        # TODO: swap PBC to punishing for underperforming
        self.r_antennae_population[:, :, 0] %= self.grid.xmax
        self.r_antennae_population[:, :, 1] %= self.grid.ymax

    def generation_cycle(self):
        self.position_history[self.iteration] = self.r_antennae_population
        self.selection()
        self.crossover_cutoff()
        self.mutation()
        self.iteration += 1

    """ plotting routines"""

    def plot_fitness(self, filename=False, show=True,
                     save=True):
        if show or save:
            fig, ax = plt.subplots()
            ax.plot(self.mean_fitness_history, "o-", label="Average fitness")
            ax.plot(self.max_fitness_history, "o-", label="Max fitness")
            ax.fill_between(np.arange(self.n_generations),
                            self.mean_fitness_history + self.std_fitness_history,
                            self.mean_fitness_history - self.std_fitness_history,
                            alpha=0.5,
                            facecolor='orange',
                            label="1 std")
            ax.set_xlabel("Generation #")
            ax.set_ylabel("Fitness")
            ax.set_ylim(0, 1)
            ax.legend()
            ax.grid()
            if filename and save:
                fig.savefig(filename)
            if show:
                return fig
            else:
                plt.close(fig)

    def plot_population(self, generation_number, only_winner=False, savefilename=None, show=True):
        """
        plot grid values (coverage (weighted optionally) and antenna locations)
        """

        coverage_population_values = self.grid.antenna_coverage_population(self)
        utility_function_values = self.grid.utility_function(coverage_population_values)
        best_candidate = np.argmax(utility_function_values)

        fig, axis = plt.subplots()
        for i, antenna_locations in enumerate(self.position_history[generation_number]):
            x_a, y_a = antenna_locations.T
            marker_size = 10
            alpha = 0.6
            if i == best_candidate:
                marker_size *= 2
                alpha = 1
            axis.plot(x_a, y_a, "*", label="#{}".format(i), ms=marker_size, alpha=alpha)

        axis.contourf(self.grid.x, self.grid.y, self.grid.weights, 100, cmap='viridis', label="Coverage")
        configurations = axis.contourf(self.grid.x, self.grid.y, coverage_population_values.sum(axis=0), 100,
                                       cmap='viridis', alpha=0.5)
        fig.colorbar(configurations)

        axis.set_title(r"Generation {}, $<f>$ {:.2f} $\pm$ {:.2f}, max {:.2f}".format(
            generation_number,
            utility_function_values.mean(),
            utility_function_values.std(),
            utility_function_values.max(),
        ))
        axis.set_xlabel("x")
        axis.set_ylabel("y")
        axis.set_xlim(0, 1)
        axis.set_ylim(0, 1)
        # axis.legend(loc='best')
        if savefilename:
            fig.savefig(savefilename)
        if show:
            return fig
        plt.close(fig)