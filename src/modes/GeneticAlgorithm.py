import random

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel

from src.modes.Mode import Mode, ProblemType


class GARoute:
    def __init__(self, distance, route):
        self.distance = distance
        self.route = route


POPULATION_SIZE = 10
FRAME_HEIGHT = 0.8
FRAME_WIDTH = 1.0
GRAPH_BORDER = 0.05

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
                                      command=self.generate_population)
        # frame
        graph_frame = DirectFrame(frameColor=(1, 1, 1, 1),
                            frameSize=((-FRAME_WIDTH/2)-(GRAPH_BORDER/2), FRAME_WIDTH/2+GRAPH_BORDER/2, (-FRAME_HEIGHT/2)-(GRAPH_BORDER*2),FRAME_HEIGHT/2+GRAPH_BORDER),
                            pos=(0, 0, 0))
        # graph essentials
        graph_label = DirectLabel(text='Genetic Algorithm',
                                  scale=0.05,
                                  pos=(0, 0, FRAME_HEIGHT/2+GRAPH_BORDER),
                                  parent=graph_frame)
        y_line = DirectFrame(frameColor=(0, 0, 1, 1),
                            frameSize=(-0.01, 0.01, -FRAME_HEIGHT/2, FRAME_HEIGHT/2),
                            pos=(-FRAME_WIDTH/2+GRAPH_BORDER, 0, -GRAPH_BORDER),
                            parent=graph_frame)
        self.ui.append(graph_frame)
        self.ui.append(graph_label)
        self.ui.append(generate_population_button)
        self.ui.append(progress_button)
        self.ui.append(y_line)

    def activate(self, _map):
        super().activate(_map)
        self.map.disable_rendering()

    def generate_population(self):
        new_population = []
        for _ in range(POPULATION_SIZE):
            temp_cities = self.map.cities[:]
            self.map.reset()
            while len(temp_cities) > 0:
                city = random.choice(temp_cities)
                self.map.select_city(city.name)
                temp_cities.remove(city)
            self.map.select_city(self.map.route[0])  # return to start
            new_population.append(GARoute(self.map.bus.distance_traveled, self.map.route[:]))
        self.notify.debug(f"Generated initial population of size {len(new_population)}")
        for individual in new_population:
            self.notify.debug(f"Distance {individual.distance}, Route {individual.route}")
        self.map.reset()

