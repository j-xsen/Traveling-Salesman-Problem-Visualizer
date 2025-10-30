import random
import statistics
import time
from collections import defaultdict
from enum import Enum

import numpy as np
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectRadioButton import DirectRadioButton
from matplotlib import pyplot as plt
from panda3d.core import TexturePool, transpose

from src.modes.Mode import Mode, ProblemType
from src.modes.GeneticAlgorithm.GARoute import GARoute


# gui
FRAME_HEIGHT = 0.9
FRAME_WIDTH = 1.3
GRAPH_BORDER = 0
# genetic algorithm parameters
RUN_TIMES = 50
GEN_TIMES = 100
POPULATION_SIZE = 100
FITTEST_TO_SELECT = 10


def mutate_child(child_route, mut_type):
    mutation_rate = 0.05
    for i in range(len(child_route)):
        if random.random() < mutation_rate:
            # mutate
            if mut_type == MutationType.SWAP:
                j = random.randint(0, len(child_route) - 1)
                # swap cities at position i and j
                child_route[i], child_route[j] = child_route[j], child_route[i]
            elif mut_type == MutationType.INVERSION:
                j = random.randint(i, len(child_route) - 1)
                # invert segment between i and j
                child_route[i:j+1] = reversed(child_route[i:j+1])
    return child_route

def update_gen_times(value):
    # verify value is int
    if not value.isdigit():
        return
    global GEN_TIMES
    print(f"Updating GEN_TIMES to {value}")
    GEN_TIMES = int(value)

def update_population_size(value):
    # verify value is int
    if not value.isdigit():
        return
    global POPULATION_SIZE
    print(f"Updating POPULATION_SIZE to {value}")
    POPULATION_SIZE = int(value)

def update_run_times(value):
    # verify value is int
    if not value.isdigit():
        return
    global RUN_TIMES
    print(f"Updating RUN_TIMES to {value}")
    RUN_TIMES = int(value)


class CrossoverType(Enum):
    ORDERED = 1
    PARTIAL_MAP = 2

class MutationType(Enum):
    SWAP = 1
    INVERSION = 2


class GeneticAlgorithm(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.GENETIC_ALGORITHM, 'Random100.tsp', _map, name="GeneticAlgorithm")
        self.map.hide_sliders()
        self.population = []
        self.crossover_type = CrossoverType.PARTIAL_MAP
        self.mutation_type = MutationType.INVERSION

    def build_ui(self):
        # buttons
        generate_population_button = DirectButton(text="Generate Population", scale=0.07,
                                                 pos=(.9, 0, -0.7),
                                                 command=self.generate_population)
        progress_button = DirectButton(text="Progress Generation", scale=0.07,
                                      pos=(.9, 0, -0.9),
                                      command=self.progress_generation)

        # prog 50 button
        prog_fifty_button = DirectButton(text="Prog 50", scale=0.05,
                                       pos=(.6, 0, -0.8),
                                       command=self.nGenerations, extraArgs=[50],)

        # find avg
        avg_button = DirectButton(text="Find Avg Best Distance", scale=0.05,
                                  pos=(-.8, 0, .5),
                                  command=self.find_avg_best_distance)

        # entry for variables
        generations_entry = DirectEntry(scale=0.05, initialText=str(GEN_TIMES),
                                        pos=(-.75, 0, 0.6), frameColor=(1, 1, 1, 1),
                                        command=update_gen_times)
        generations_label = DirectLabel(text="Generations to run:", scale=0.05,
                                        pos=(-1, 0, 0.6), text_fg=(0, 0, 0, 1),)
        run_times_entry = DirectEntry(scale=0.05, initialText=str(RUN_TIMES),
                                      pos=(-.75, 0, 0.75), frameColor=(1, 1, 1, 1),
                                      command=update_run_times)
        run_times_label = DirectLabel(text="Run times:", scale=0.05,
                                      pos=(-1, 0, 0.75), text_fg=(0, 0, 0, 1),)
        population_entry = DirectEntry(scale=0.05, initialText=str(POPULATION_SIZE),
                                       pos=(-.75, 0, 0.9), frameColor=(1,1,1,1),
                                       command=update_population_size)
        population_label = DirectLabel(text="Population Size:", scale=0.05,
                                       pos=(-1, 0, 0.9), text_fg=(0,0,0,1),)

        # radio buttons

        #   crossover
        crossover_buttons = [
            DirectRadioButton(text="Ordered Crossover", scale=0.05, pos=(-1, 0, 0.3),
                              variable=[self.crossover_type], value=[CrossoverType.ORDERED],
                              command=self.set_crossover_type, extraArgs=[CrossoverType.ORDERED],),
            DirectRadioButton(text="Partial Map Crossover", scale=0.05, pos=(-1, 0, .1),
                              variable=[self.crossover_type], value=[CrossoverType.PARTIAL_MAP],
                              command=self.set_crossover_type, extraArgs=[CrossoverType.PARTIAL_MAP],)
        ]
        for button in crossover_buttons:
            button.setOthers(crossover_buttons)

        #   mutation
        mutation_buttons = [
            DirectRadioButton(text="Swap Mutation", scale=0.05, pos=(-1, 0, -0.1),
                              variable=[self.mutation_type], value=[MutationType.SWAP],
                              command=self.set_mutation_type, extraArgs=[MutationType.SWAP], ),
            DirectRadioButton(text="Inversion Mutation", scale=0.05, pos=(-1, 0, -0.3),
                              variable=[self.mutation_type], value=[MutationType.INVERSION],
                              command=self.set_mutation_type, extraArgs=[MutationType.INVERSION], )
        ]
        for button in mutation_buttons:
            button.setOthers(mutation_buttons)

        frame = DirectFrame(frameColor=(1, 1, 1, 1),
                            frameSize=(-FRAME_WIDTH / 2, FRAME_WIDTH / 2,
                                       -FRAME_HEIGHT / 2, FRAME_HEIGHT / 2),
                            pos=(GRAPH_BORDER, 0,
                                 -1 + FRAME_HEIGHT + GRAPH_BORDER))
        self.ui.append(frame) # frame must be first
        self.ui.append(generate_population_button)
        self.ui.append(progress_button)
        self.ui.append(mutation_buttons)
        self.ui.append(crossover_buttons)
        self.ui.append(prog_fifty_button)
        self.ui.append(avg_button)
        self.ui.append(generations_entry)
        self.ui.append(generations_label)
        self.ui.append(run_times_entry)
        self.ui.append(run_times_label)
        self.ui.append(population_entry)
        self.ui.append(population_label)

        self.regenerate_plot()

    def nGenerations(self, n):
        for _ in range(n):
            self.progress_generation(regen=False)
        self.regenerate_plot()

    def find_avg_best_distance(self):
        for child in self.ui[0].getChildren():
            child.removeNode()
        # clear texture
        self.remove_texture()

        # totals
        min_total = 0
        max_total = 0
        avg_distance_total = 0
        start_time = time.perf_counter()
        run_times_list = []
        distance_list = []
        min_list = []
        max_list = []
        best_route = []
        best_distance = float('inf')

        for _ in range(RUN_TIMES):
            self.generate_population(regen=False)
            cur_min = float('inf')
            cur_max = 0
            total_distance = 0
            total_individuals = 0
            run_start_time = time.perf_counter()

            cur_dist_list = []

            # 50 generations
            for _ in range(GEN_TIMES):

                self.progress_generation(regen=False)
                last_gen = self.population[-1]
                last_gen.sort(key=lambda x: x.distance)

                cur_dist_list.append(sum(map(lambda g: g.distance, last_gen)) / len(last_gen))

                total_distance += sum(map(lambda g: g.distance, last_gen))
                total_individuals += len(last_gen)

                if last_gen[0].distance < cur_min:
                    cur_min = last_gen[0].distance
                    best_route = last_gen[0].route[:]
                    if last_gen[0].distance < best_distance:
                        best_distance = last_gen[0].distance
                if last_gen[-1].distance > cur_max:
                    cur_max = last_gen[-1].distance

            distance_list.append(sum(cur_dist_list))
            min_list.append(cur_min)
            max_list.append(cur_max)
            min_total += cur_min
            max_total += cur_max
            avg_distance = total_distance / total_individuals
            avg_distance_total += avg_distance
            run_elapsed = time.perf_counter() - run_start_time
            run_times_list.append(run_elapsed)
        avg_min = min_total / RUN_TIMES
        avg_max = max_total / RUN_TIMES
        avg_distance_overall = avg_distance_total / RUN_TIMES
        time_elapsed = time.perf_counter() - start_time
        time_averaged = sum(run_times_list) / RUN_TIMES

        # std dev
        yerrs = [statistics.stdev(min_list), statistics.stdev(max_list), statistics.stdev(distance_list)]

        # plt
        labels = ['Avg Min', 'Avg Max', 'Avg Distance']
        values = [avg_min, avg_max, avg_distance_overall]
        colors = ['green', 'red', 'blue']

        # create figure
        plt.figure(figsize=(FRAME_WIDTH * 5, FRAME_HEIGHT * 5))
        bars = plt.bar(labels, values, color=colors)

        # create errorbars
        for i in range(len(bars)):
            plt.errorbar(bars[i].get_x() + bars[i].get_width() / 5, values[i],
                         yerr=yerrs[i], fmt='none', ecolor='black', capsize=10)
            y_top = values[i] + yerrs[i]
            plt.text(bars[i].get_x() + bars[i].get_width() / 5, y_top+200, f'±{yerrs[i]:.2f}', ha='center', va='center', fontsize=10)

        # title
        plt.title(f'Genetic Algorithm {self.mutation_type.name} {self.crossover_type.name}', fontweight='bold',
                  fontsize=14, x=0.5, y=1.07)
        # text
        plt.text(0.5, 1.04, f'Over {RUN_TIMES} runs of {GEN_TIMES} generations each / Population: {POPULATION_SIZE}', transform=plt.gca().transAxes,
                 ha='center', va='center',fontsize=12)
        plt.text(1.1, -.1175, f'Avg Time/Run: {time_averaged:.2f} secs', transform=plt.gca().transAxes,
                 ha='right', va='center',)
        plt.text(-.12, -.1175, f'Total Time: {time_elapsed:.2f} sec', transform=plt.gca().transAxes,
                 ha='left', va='center')
        plt.text(-.12, -.2, f'Best: {min(min_list):.2f} / Worst: {max(max_list):.2f}', transform=plt.gca().transAxes,)

        # plt.subplots_adjust(bottom=0.2)
        plt.margins(y=0.1)

        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}', va='bottom', fontweight="bold")

        title = f"results/GA/{self.mutation_type.name}-{self.crossover_type.name}-G{GEN_TIMES}-R{RUN_TIMES}.png"
        with open(f"{title[:-4]}.txt", 'w') as f:
            f.write(f"Best Route:\n{best_route}\n\n")
            f.write(f"Distance:\t{best_distance:.5f}\n")
            f.write(f"Overall Min:\t{min(min_list):.5f}\n")
            f.write(f"Overall Max:\t{max(max_list):.5f}\n")
            f.write(f"Avg Min:\t{avg_min:.5f}\n")
            f.write(f"Avg Max:\t{avg_max:.5f}\n")
            f.write(f"Avg Distance:\t{avg_distance_overall:.5f}\n")
            f.write(f"Total Distance:\t{sum(distance_list):.5f}\n")
            f.write(f"Time Elapsed:\t{time_elapsed:.5f}\n")
            f.write(f"Avg Time/Run:\t{time_averaged:.5f}\n")
        plt.savefig(title)
        plt.close()
        self.load_texture(texture_path=title)

    def set_mutation_type(self, mutation_type):
        self.mutation_type = mutation_type

    def set_crossover_type(self, crossover_type):
        self.crossover_type = crossover_type

    def regenerate_plot(self):
        self.notify.debug("Regenerating plot...")
        if len(self.population) == 0:
            label = DirectLabel(text="No population generated yet.",
                                scale=0.07,
                                pos=(0, 0, 0),
                                text_fg=(0, 0, 0, 1),
                                parent=self.ui[0])
            return
        for child in self.ui[0].getChildren():
            child.removeNode()

        self.remove_texture()

        fig, ax = plt.subplots(figsize=(FRAME_WIDTH * 5, FRAME_HEIGHT * 5))

        plt.title(f"Genetic Algorithm - {self.mutation_type.name.title()} & {self.crossover_type.name.title()}")
        plt.xlabel("Generation")
        step = max(1, len(self.population)//10)
        plt.xticks(np.arange(0, len(self.population)+1, step))
        plt.ylabel("Distance")
        plt.grid(True)

        # plot each generation
        min_distance, min_gen = float('inf'), 0
        best_route = []
        for gen_idx, gen in enumerate(self.population, start=1):
            for ind in gen:
                if ind.distance < min_distance:
                    min_distance = ind.distance
                    min_gen = gen_idx
                    best_route = ind.route[:]
                ax.plot(gen_idx, ind.distance, 'o', alpha=0.5)

        # text info
        plt.text(.7, -.175, f"Generations: {len(self.population)}\n", transform=plt.gca().transAxes,)
        plt.text(-.15, -.175, f"Best distance: {min_distance:.3f} from gen {min_gen}\n",
                 transform=plt.gca().transAxes,)

        # take picture
        title = f"results/GA/{self.mutation_type.name}-{self.crossover_type.name}-ProgGen.png"
        plt.savefig(title)

        with open(f"{title[:-4]}-info.txt", 'w') as f:
            f.write(f"Best Route:\n{best_route}\n\n")
            f.write(f"Best Distance:\t{min_distance:.5f} from Generation {min_gen}\n")
            f.write(f"Total Generations:\t{len(self.population)}\n")
            f.write(f"Population Size:\t{POPULATION_SIZE}\n")

        # close plot
        plt.close()

        self.load_texture(texture_path=title)

    def remove_texture(self):
        if self.ui and self.ui[0]['frameTexture']:
            TexturePool.releaseTexture(self.ui[0]['frameTexture'])
            self.ui[0]['frameTexture'] = None

    def load_texture(self, texture_path="progress.png"):
        txtr = loader.loadTexture(texture_path)
        self.ui[0]['frameTexture'] = txtr

    def activate(self, _map):
        super().activate(_map)
        self.map.disable_rendering()
        self.map.disable_text()

    def deactivate(self):
        super().deactivate()
        self.map.enable_rendering()
        self.map.enable_text()

    def generate_population(self, regen=True):
        new_population = []
        for _ in range(POPULATION_SIZE):
            temp_cities = self.map.cities[:] # create temp copy
            self.map.reset()
            while len(temp_cities) > 0:
                city = random.choice(temp_cities)
                self.map.select_city(city.name)
                temp_cities.remove(city)
            self.map.select_city(self.map.route[0])  # return to start
            new_population.append(GARoute(self.map.bus.distance_traveled, self.map.route[:]))
        self.notify.debug(f"Generated initial population of size {len(new_population)}")
        self.map.reset()
        self.population = [new_population]
        if regen:
            self.regenerate_plot()

    def generate_child(self, parent_list):
        self.notify.debug("Generating new child...")
        parent1, parent2 = random.choices(parent_list, k=2)  # select two

        if self.crossover_type == CrossoverType.ORDERED:
            # random crossover point
            cutpoint = random.randint(1, len(parent1.route) - 2)
            child_route = parent1.route[:cutpoint]
            # add remainder from parent2
            for city in parent2.route:
                if city not in child_route:
                    child_route.append(city)

            # mutate child
            mutate_child(child_route, self.mutation_type)
        elif self.crossover_type == CrossoverType.PARTIAL_MAP:
            # choose slice from parent1
            start = random.randint(0, len(parent1.route) - 3)
            end = random.randint(start + 1, len(parent1.route) - 1)
            self.notify.debug(f"Selected slice from {start} to {end} for crossover.")
            child_route = [None]*(len(parent2.route)-1)  # create empty route
            # copy segment from parent1
            for i in range(start, end):
                child_route[i] = parent1.route[i]
            self.notify.debug(f"Child route after copying from parent1: {child_route}")
            # fill in remainder from parent2
            p2_index = 0
            used = set(child_route)
            for i in range(len(child_route)):
                if child_route[i] is None:
                    while p2_index < len(parent2.route) and parent2.route[p2_index] in used:
                        p2_index += 1
                    if p2_index < len(parent2.route):
                        child_route[i] = parent2.route[p2_index]
                        used.add(parent2.route[p2_index])
                        p2_index += 1

            # mutate child
            mutate_child(child_route, self.mutation_type)
            self.notify.debug(f"Generated child route: {child_route}")

        return child_route

    def progress_generation(self, regen=True):
        if len(self.population) == 0:
            self.notify.warning("No population to progress, generate population first.")
            return
        last_gen = self.population[-1]
        last_gen.sort(key=lambda x: x.distance)
        new_gen = []
        while len(new_gen) < POPULATION_SIZE:
            child_route = self.generate_child(last_gen[:FITTEST_TO_SELECT])
            # get distance
            self.map.reset()
            for city_id in child_route:
                self.map.select_city(str(city_id))
            self.map.select_city(str(child_route[0]))  # return to start

            new_gen.append(GARoute(self.map.bus.distance_traveled, self.map.route[:]))
        self.population.append(new_gen)
        self.notify.debug("================================")
        self.notify.debug(f"Progressed to generation {len(self.population)}!")
        self.notify.debug(f"Mutation type: {self.mutation_type}, Crossover type: {self.crossover_type}")
        self.notify.debug("Best candidates:")
        for ind in new_gen[:3]:
            self.notify.debug(f"Distance: {ind.distance}")
        self.notify.debug("================================")
        self.map.reset()
        if regen:
            self.regenerate_plot()


    def on_mouse_click(self):
        pass
