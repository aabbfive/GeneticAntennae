import numpy as np

from GeoData import GeoGrid
from Population import Population

if __name__ == '__main__':
    np.random.seed(0)
    grid = GeoGrid()

    pop = Population(grid,
                     n_pop=4,
                     n_trial=7 * 4,
                     n_antennae=30,
                     default_power=0.3,
                     p_cross=0.8,
                     p_mutation=1,
                     std_mutation=0.15,
                     n_generations=200,
                     )
    print(f"Running {pop.NPOPULATION} populations of {pop.NANTENNAE} antennae each for {pop.n_generations} generations")
    for n in range(pop.n_generations):
        pop.generation_cycle()
    pop.plot_fitness(savefilename="fitness", show=False)
    pop.plot_std(savefilename="std", show=False)
    for i in np.linspace(0, pop.n_generations, 5, endpoint=False, dtype=int):
        print(f"Plotted generation {i}")
        pop.plot_population(i, savefilename="snapshot", show=False)
    pop.plot_population(savefilename="snapshot_final", show=False)
    # print(pop.mean_fitness_history)
