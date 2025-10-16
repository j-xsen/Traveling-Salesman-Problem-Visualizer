import random

import numpy as np
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from matplotlib import pyplot as plt
from panda3d.core import TexturePool

from src.modes.Mode import Mode, ProblemType


class GARoute:
    def __init__(self, distance, route):
        self.distance = distance
        self.route = route


POPULATION_SIZE = 10
FRAME_HEIGHT = 0.9
FRAME_WIDTH = 1.0
GRAPH_BORDER = 0

class GeneticAlgorithm(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.GENETIC_ALGORITHM, 'Random100.tsp', _map)
        self.population = []

    def build_ui(self):
        # buttons
        generate_population_button = DirectButton(text="Generate Population", scale=0.07,
                                                 pos=(.9, 0, -0.7),
                                                 command=self.generate_population)
        progress_button = DirectButton(text="Progress Generation", scale=0.07,
                                      pos=(.9, 0, -0.9),
                                      command=self.progress_generation)

        frame = DirectFrame(frameColor=(1, 1, 1, 1),
                            frameSize=(-FRAME_WIDTH / 2, FRAME_WIDTH / 2,
                                       -FRAME_HEIGHT / 2, FRAME_HEIGHT / 2),
                            pos=(-1 + FRAME_WIDTH + GRAPH_BORDER, 0,
                                 -1 + FRAME_HEIGHT + GRAPH_BORDER))
        self.ui.append(frame) # frame must be first
        self.ui.append(generate_population_button)
        self.ui.append(progress_button)

        self.regenerate_plot()

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

        # remove texture
        if self.ui[0]['frameTexture']:
            TexturePool.releaseTexture(self.ui[0]['frameTexture'])

        plt.subplots(figsize=(FRAME_WIDTH * 5, FRAME_HEIGHT * 5))

        plt.title("Genetic Algorithm Progress")
        plt.xlabel("Generation")
        plt.xticks(np.arange(0, len(self.population), 1))
        plt.ylabel("Distance")
        plt.grid(True)

        # plot each generation
        for i in range(len(self.population)):
            gen = self.population[i]
            gen_distances = [ind.distance for ind in gen]
            plt.plot([i] * len(gen), gen_distances, 'o', alpha=0.5)
        plt.savefig("progress.png")
        plt.close()
        txtr = loader.loadTexture("progress.png")
        self.ui[0]['frameTexture'] = txtr

    def activate(self, _map):
        super().activate(_map)
        self.map.disable_rendering()

    def generate_population(self):
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
        self.regenerate_plot()

    def progress_generation(self):
        if len(self.population) == 0:
            self.notify.warning("No population to progress, generate population first.")
            return
        last_gen = self.population[-1]
        last_gen.sort(key=lambda x: x.distance)
        new_gen = last_gen[:2]  # keep best two
        while len(new_gen) < POPULATION_SIZE:
            self.notify.debug("Generating new child...")
            parent1, parent2 = random.choices(last_gen[:5], k=2)  # select two from best 5

            cutpoint = random.randint(1, len(parent1.route) - 2)
            child_route = parent1.route[:cutpoint]
            # add remainder from parent2
            for city in parent2.route:
                if city not in child_route:
                    child_route.append(city)

            # get distance
            self.map.reset()
            for city_id in child_route:
                self.map.select_city(str(city_id))
            self.map.select_city(str(child_route[0]))  # return to start

            new_gen.append(GARoute(self.map.bus.distance_traveled, self.map.route[:]))
        self.population.append(new_gen)
        self.notify.debug("================================")
        self.notify.debug(f"Progressed to generation {len(self.population)}!")
        self.notify.debug("Best candidates:")
        for ind in new_gen[:3]:
            self.notify.debug(f"Distance: {ind.distance}, Route: {ind.route}")
        self.notify.debug("================================")
        self.map.reset()
        self.regenerate_plot()


    def on_mouse_click(self):
        pass
