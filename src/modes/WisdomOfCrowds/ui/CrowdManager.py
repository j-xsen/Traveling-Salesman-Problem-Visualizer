import random
import subprocess

import numpy
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectSlider import DirectSlider
from direct.showbase.DirectObject import DirectObject
from panda3d.core import WindowProperties, ButtonHandle
from scipy.special import betaincinv

from src.modes.GeneticAlgorithm.GeneticAlgorithm import CrossoverType, MutationType, mutate_child
from src.modes.WisdomOfCrowds.People.People import People
from src.modes.WisdomOfCrowds.ui.CrowdDisplay import CrowdDisplay
from src.modes.WisdomOfCrowds.ui.PeoplePicker import PeoplePicker

bh = ButtonHandle("b")


class CrowdManager(DirectObject):
    def __init__(self, crowd_size=10, elite_percent=0.2):
        DirectObject.__init__(self)
        self.notify = directNotify.newCategory("CrowdManager")
        self.ui = []

        # crowd
        self.generations = []
        self.generation = 0
        self.crowd_size = crowd_size
        self._elite_percent = elite_percent

        self._generated_crowd = False
        self._generated_lkh = False

        self.people_picker = None
        self.crowd_display = None
        self.accept("WOCProblemChanged", self.disable_lkh_buttons)

    @property
    def elite_percent(self):
        return self._elite_percent
    @elite_percent.setter
    def elite_percent(self, val):
        if self.crowd_display:
            self.crowd_display.elite_percent = val
        self._elite_percent = val

    @property
    def generated_crowd(self):
        return self._generated_crowd

    @generated_crowd.setter
    def generated_crowd(self, val):
        if val is True:
            self.notify.debug("Generated crowd")
            # crowd generated, check if ui exists
            if len(self.ui) > 0:
                self.ui[7]["state"] = DGG.NORMAL
                self.ui[12]['state'] = DGG.NORMAL
                self.ui[13]['state'] = DGG.NORMAL
                self.ui[16]['state'] = DGG.NORMAL
            else:
                self.notify.warning("UI not built yet, cannot update LKH buttons.")
        else:
            self.ui[7]["state"] = DGG.DISABLED
            self.ui[12]['state'] = DGG.DISABLED
            self.ui[13]['state'] = DGG.DISABLED
            self.ui[16]['state'] = DGG.DISABLED
        self._generated_crowd = val

    @property
    def generated_lkh(self):
        return self._generated_lkh

    @generated_lkh.setter
    def generated_lkh(self, val):
        if val:
            self.notify.debug("Generated LKH tour")
            self.notify.debug(f"Value: {val}")
            # lkh generated, check if ui exists
            if len(self.ui) > 0:
                self.ui[6]["state"] = DGG.NORMAL
            else:
                self.notify.warning("UI not built yet, cannot update LKH buttons.")
        else:
            self.ui[6]["state"] = DGG.DISABLED
        self._generated_lkh = val

    def disable_lkh_buttons(self):
        self.notify.debug("Disabling LKH buttons...")
        if len(self.ui) == 0:
            self.notify.warning("UI not built yet, cannot disable LKH buttons.")
            return
        self.generated_lkh = False
        self.generated_crowd = False

    def destroy(self):
        self.notify.debug("Destroying Crowd Manager...")
        self.ignoreAll()
        for item in self.ui:
            item.destroy()
        self.ui.clear()
        base.userExit()

    def open(self):
        self.notify.debug("Opening Crowd Manager...")

        # resize
        wp = WindowProperties()
        wp.setSize(1600, 600)
        base.win.requestProperties(wp)

        self.build_ui()

    def adjust_crowd_size(self, text):
        if len(self.ui) == 0:
            self.notify.warning("UI not built yet, cannot adjust crowd size.")
            return
        try:
            size = int(text)
            if size < 1:
                self.notify.warning("Crowd size must be at least 1.")
                self.ui[2].enterText(str(self.crowd_size))
            else:
                self.crowd_size = size
                return
        except ValueError:
            self.notify.warning("Invalid crowd size entered.")
        self.ui[2].enterText(str(self.crowd_size))

    def set_elite_percent(self):
        if len(self.ui) == 0:
            self.notify.warning("UI not built yet, cannot set elite percent.")
            return
        slider = self.ui[14]
        label = self.ui[15]
        self.elite_percent = slider['value']
        label['text'] = "Elite Percent:\n{:.0f}%".format(self.elite_percent * 100)

    def build_ui(self):
        # base
        frame = DirectFrame(frameColor=(0, 0, 0, 1),
                            frameSize=(0, 1, 0, 1),
                            pos=(0, 0, 0),
                            parent=base.a2dBottomRight)

        # crowd
        crowd_np = frame.attachNewNode("crowd_np")
        crowd_size_label = DirectLabel(text="Crowd Size:",
                                       scale=0.07, pos=(-.5, 0, .155),
                                       text_pos=(0, 0),
                                       text_fg=(1, 1, 1, 1),
                                       frameColor=(0, 0, 0, 0),
                                       parent=crowd_np)
        crowd_size = DirectEntry(text="", scale=0.07, initialText=str(self.crowd_size),
                                 parent=crowd_np, pos=(-.3, 0, .14),
                                 text_pos=(0.15, 0.2),
                                 text_fg=(1, 1, 1, 1), frameSize=(0, 2, 0, 1),
                                 frameColor=(1, 1, 1, 0.5), width=2.5,
                                 command=self.adjust_crowd_size)
        elite_percent_slider = DirectSlider(range=(0.0, 1), value=self.elite_percent,
                                            scale=0.3, pos=(-.8, 0, .25),
                                            frameSize=(-0.15, 0.15, -0.65, 0.65),
                                            pageSize=1,
                                            command=self.set_elite_percent,
                                            thumb_frameSize=(-0.1, 0.1, -0.1, 0.1),
                                            orientation=DGG.VERTICAL,
                                            parent=crowd_np)
        elite_percent_label = DirectLabel(text="Elite Percent:\n{:.0f}%".format(self.elite_percent * 100),
                                          scale=0.05, pos=(-1, 0, .35),
                                          text_pos=(0, 0),
                                          text_fg=(1, 1, 1, 1),
                                          frameColor=(0, 0, 0, 0),
                                          parent=crowd_np)

        make_new_crowd_button = DirectButton(text="Create new Crowd", scale=0.07,
                                             pos=(-.35, 0, .05),
                                             command=self.generate_crowd, parent=frame)

        # LKH frame
        lkh_frame = DirectFrame(frameColor=(.5, .5, .5, 1),
                                relief=DGG.RAISED,
                                borderWidth=(0.01, 0.01),
                                frameSize=(-0.3, 0.3, -0.1, 0.1),
                                pos=(-1.25, 0, .15),
                                parent=frame)

        lkh_title = DirectLabel(text="LKH Tour:",
                                scale=0.07,
                                text_fg=(1, 1, 1, 1),
                                frameColor=(0, 0, 0, 0),
                                pos=(0, 0, .025),
                                parent=lkh_frame)

        show_lkh_tour_button = DirectButton(text="Show", scale=0.07,
                                            pos=(.16, 0, -.06),
                                            state=DGG.DISABLED,
                                            frameColor=(
                                                (0.8, 0.8, 0.8, 1),  # Normal
                                                (0.9, 0.9, 0.9, 1),  # Click
                                                (0.7, 0.7, 0.7, 1),  # Hover
                                                (0.5, 0.5, 0.5, 1)  # Disabled
                                            ),
                                            command=self.show_lkh_tour, parent=lkh_frame)

        generate_new_lkh_tour_button = DirectButton(text="Generate", scale=0.07,
                                                    pos=(-.11, 0, -.06),
                                                    extraArgs=["crowd"],
                                                    state=DGG.DISABLED,
                                                    frameColor=(
                                                        (0.8, 0.8, 0.8, 1),  # Normal
                                                        (0.9, 0.9, 0.9, 1),  # Click
                                                        (0.7, 0.7, 0.7, 1),  # Hover
                                                        (0.5, 0.5, 0.5, 1)  # Disabled
                                                    ),
                                                    command=self.run_lkh, parent=lkh_frame)

        # generation frame
        gen_frame = DirectFrame(frameColor=(.7, .7, .7, 1),
                                relief=DGG.RAISED,
                                 borderWidth=(0.01, 0.01),
                                 frameSize=(-0.3, 0.3, -0.1, 0.1),
                                 pos=(-1.5, 0, .4),
                                 parent=frame)
        gen_text = DirectLabel(text="Generation: 0",
                                 scale=0.07,
                                    frameColor=(0, 0, 0, 0),
                                    pos=(0, 0, 0),
                                    parent=gen_frame)
        gen_left = DirectButton(text="<", scale=0.1,
                                frameColor=(
                                    (0.8, 0.8, 0.8, 1),  # Normal
                                    (0.9, 0.9, 0.9, 1),  # Click
                                    (0.7, 0.7, 0.7, 1),  # Hover
                                    (0.5, 0.5, 0.5, 1)  # Disabled
                                ),
                                state=DGG.DISABLED,
                                pos=(-.3, 0, -.02),parent=gen_frame)
        gen_right = DirectButton(text=">", scale=0.1,
                                 frameColor=(
                                     (0.8, 0.8, 0.8, 1),  # Normal
                                     (0.9, 0.9, 0.9, 1),  # Click
                                     (0.7, 0.7, 0.7, 1),  # Hover
                                     (0.5, 0.5, 0.5, 1)  # Disabled
                                 ),
                                 state=DGG.DISABLED,
                                 pos=(.3, 0, -.02), parent=gen_frame)
        gen_new = DirectButton(text="Generate", scale=0.07,
                               frameColor=(
                                   (0.8, 0.8, 0.8, 1),  # Normal
                                   (0.9, 0.9, 0.9, 1),  # Click
                                   (0.7, 0.7, 0.7, 1),  # Hover
                                   (0.5, 0.5, 0.5, 1)  # Disabled
                               ),
                                 command=self.create_next_generation,
                                 state=DGG.DISABLED,
                               pos=(-.135, 0, -.1), parent=gen_frame)
        gen_fifty = DirectButton(text="50", scale=0.07,
                                 frameColor=(
                                     (0.8, 0.8, 0.8, 1),  # Normal
                                     (0.9, 0.9, 0.9, 1),  # Click
                                     (0.7, 0.7, 0.7, 1),  # Hover
                                     (0.5, 0.5, 0.5, 1)  # Disabled
                                 ),
                                    command=self.multiple_gens,
                                    extraArgs=[50],
                                    state=DGG.DISABLED,
                                    pos=(.085, 0, -.1), parent=gen_frame)
        gen_hundred = DirectButton(text="100", scale=0.07,
                                 frameColor=(
                                     (0.8, 0.8, 0.8, 1),  # Normal
                                     (0.9, 0.9, 0.9, 1),  # Click
                                     (0.7, 0.7, 0.7, 1),  # Hover
                                     (0.5, 0.5, 0.5, 1)  # Disabled
                                 ),
                                 command=self.multiple_gens,
                                 extraArgs=[100],
                                 state=DGG.DISABLED,
                                 pos=(.22, 0, -.1), parent=gen_frame)

        # widgets
        self.people_picker = PeoplePicker(frame)
        self.crowd_display = CrowdDisplay(frame,self.elite_percent)

        # append
        self.ui.append(frame)                           # 0
        self.ui.append(crowd_size_label)                # 1
        self.ui.append(crowd_size)                      # 2
        self.ui.append(make_new_crowd_button)           # 3
        self.ui.append(lkh_frame)                       # 4
        self.ui.append(lkh_title)                       # 5
        self.ui.append(show_lkh_tour_button)            # 6
        self.ui.append(generate_new_lkh_tour_button)    # 7
        self.ui.append(gen_frame)                       # 8
        self.ui.append(gen_text)                        # 9
        self.ui.append(gen_left)                        # 10
        self.ui.append(gen_right)                       # 11
        self.ui.append(gen_new)                         # 12
        self.ui.append(gen_fifty)                       # 13
        self.ui.append(elite_percent_slider)            # 14
        self.ui.append(elite_percent_label)             # 15
        self.ui.append(gen_hundred)                     # 16

        self.ui.append(self.crowd_display)              #
        self.ui.append(self.people_picker)              #

    def multiple_gens(self, num):
        for _ in range(num):
            self.create_next_generation()

    def read_lkh_tour(self):
        self.notify.debug("Reading LKH Tour...")
        tour_file = f"{matrix_storage_location}crowd.tour"
        self.notify.debug(f"Reading tour from {tour_file}...")
        try:
            with open(tour_file, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            self.notify.error(f"Tour file {tour_file} not found. Please generate a crowd first.")
            return []
        tour = []
        reading_tour = False
        for line in lines:
            line = line.strip()
            if line == "TOUR_SECTION":
                reading_tour = True
                continue
            if line == "EOF" or line == "-1":
                break
            if reading_tour:
                if line.isdigit():
                    city_index = int(line)
                    tour.append(city_index)
        self.notify.debug(f"Read tour: {tour}")
        return tour

    def show_lkh_tour(self):
        self.notify.debug("Showing LKH Tour...")
        tour = self.read_lkh_tour()
        self.show_route(tour)

    def run_lkh(self, name):
        create_parameter_file(name, runs=len(self.generations))
        subprocess.run(["LKH", f"{matrix_storage_location}{name}.par"], check=True)
        self.generated_lkh = True

    def show_route(self, route):
        base.map.reset()
        self.notify.debug(f"Showing route : {route}")
        first = None
        for stop in route:
            if not first:
                first = stop
            base.map.select_city(stop)
        base.map.select_city(first)

    def add_generation(self, crowd):
        self.notify.debug("Adding generation")
        self.generations.append(crowd)
        # update text
        self.ui[9]['text'] = f"Generation: {len(self.generations)}"
        # enable generate button
        self.ui[12]['state'] = DGG.NORMAL
        self.ui[13]['state'] = DGG.NORMAL
        self.ui[16]['state'] = DGG.NORMAL

    def generate_crowd(self):
        self.notify.debug("Making new crowd...")
        self.disable_lkh_buttons()
        self.generations.clear()
        crowd = []
        for _ in range(self.crowd_size):
            person = self.people_picker.pick_a_person()
            crowd.append(person)
        self.crowd_display.edit_crowd(crowd)
        self.generated_crowd = True
        self.add_generation(crowd)
        self.refresh_lkh_tour()

    def create_agreement_matrix(self):
        self.notify.debug("Creating agreement matrix...")
        route_size = len(base.map.cities)
        self.notify.debug(f"Crowd size: {self.crowd_size}, Route size: {route_size}")
        connections = 0
        matrix = numpy.array([[0 for _ in range(route_size)] for _ in range(route_size)], dtype=float)
        for i in range(self.crowd_size):
            route = self.generations[self.generation][i].route
            for j in range(route_size):
                connection_start = int(route[j].get_name()[5:]) - 1
                if j == len(route) - 1:
                    connection_end = int(route[0].get_name()[5:]) - 1
                else:
                    connection_end = int(route[j + 1].get_name()[5:]) - 1
                connections += 1
                matrix[connection_start][connection_end] += 1
                matrix[connection_end][connection_start] += 1
        # agreement
        agreement = matrix / self.crowd_size
        agreement = numpy.clip(agreement, 0.0, 1.0)

        # power transform
        b1 = b2 = 3
        eps = 1e-12
        A_clip = numpy.clip(agreement, eps, 1.0 - eps)
        C_beta = 1.0 - betaincinv(b1, b2, A_clip)
        C_int = numpy.round(C_beta * 100000).astype(int)
        return C_int

    def generate_child(self, parent_list):
        self.notify.debug("Generating new child...")
        parent1, parent2 = random.choices(parent_list, k=2)  # select two
        route_length = len(base.map.cities)
        if not parent1.route or not parent2.route:
            self.notify.error("One of the parents has an empty route.")
            return []
        # fix if loop
        if parent1.route[0] == parent1.route[-1]:
            self.notify.debug("Dropping duplicate end city from parent1 route.")
            parent1.route = parent1.route[:-1]
        if parent2.route[0] == parent2.route[-1]:
            self.notify.debug("Dropping duplicate end city from parent2 route.")
            parent2.route = parent2.route[:-1]
        if len(parent1.route) != route_length or len(parent2.route) != route_length:
            self.notify.error(f"Parent routes are of different lengths.\nParent1 {parent1.route}\nParent2 {parent2.route}")
            return []

        crossover_type = random.choice(list(CrossoverType))
        child_route = None
        if crossover_type == CrossoverType.ORDERED:
            # random crossover point
            cutpoint = random.randint(1, route_length - 2)
            child_route = parent1.route[:cutpoint]
            # add remainder from parent2
            for city in parent2.route:
                if city not in child_route:
                    child_route.append(city)
        elif crossover_type == CrossoverType.PARTIAL_MAP:
            # choose slice from parent1
            start = random.randint(0, route_length - 3)
            end = random.randint(start + 1, route_length - 1)
            self.notify.debug(f"Selected slice from {start} to {end} for crossover.")
            child_route = [None] * (route_length)  # create empty route
            # copy segment from parent1
            for i in range(start, end+1):
                child_route[i] = parent1.route[i]
            self.notify.debug(f"Child route after copying from parent1: {child_route}")
            # fill in remainder from parent2
            p2_index = 0
            used = set(child_route)
            for i in range(len(child_route)):
                if child_route[i] is None:
                    while p2_index < route_length and parent2.route[p2_index] in used:
                        p2_index += 1
                    if p2_index < route_length:
                        child_route[i] = parent2.route[p2_index]
                        used.add(parent2.route[p2_index])
                        p2_index += 1
            self.notify.debug(f"Generated child route: {child_route}")
        if len(child_route) != route_length:
            self.notify.error(f"Generated child route of incorrect length: {len(child_route)} expected {route_length}.\nRoute: {child_route}")
            return []

        mutation_type = random.choice(list(MutationType))
        mutate_child(child_route, mutation_type)

        return child_route

    def refresh_lkh_tour(self):
        agreement_matrix = self.create_agreement_matrix()
        # create files
        cost_matrix_to_tsp("crowd", agreement_matrix)
        create_par_file = create_parameter_file("crowd", runs=len(self.generations)*5)
        self.run_lkh("crowd")

    def create_next_generation(self):
        # setup
        self.notify.debug("Creating next generation...")
        current_generation = self.generations[-1]
        sorted_gen = sorted(current_generation, key=lambda person: person.distance)
        parents = sorted_gen[:max(1, int(self.crowd_size * self.elite_percent))]  # top
        # add LKH
        self.refresh_lkh_tour()
        lkh_person = People()
        lkh_person.load_route(self.read_lkh_tour())
        parents.append(lkh_person)

        # next gen
        next_generation = []
        while len(next_generation) < self.crowd_size:
            child_route = self.generate_child(parents)
            child_person = People()
            child_person.route = child_route
            child_person.calculate_distance()
            next_generation.append(child_person)
        self.generations.append(next_generation)

        # update text
        self.ui[9]['text'] = f"Generation: {len(self.generations)}"
        self.crowd_display.edit_crowd(next_generation)
        self.notify.debug("Next generation created.")


matrix_storage_location = "results/WOC/LKH/"


def cost_matrix_to_tsp(filename, cost_matrix):
    with open(f"{matrix_storage_location}{filename}.tsp", 'w') as f:
        size = cost_matrix.shape[0]
        f.write("NAME: cost_matrix_problem\n")
        f.write("TYPE: TSP\n")
        f.write(f"DIMENSION: {size}\n")
        f.write("EDGE_WEIGHT_TYPE: EXPLICIT\n")
        f.write("EDGE_WEIGHT_FORMAT: FULL_MATRIX\n")
        f.write("EDGE_WEIGHT_SECTION\n")
        for i in range(size):
            row = ' '.join(str(int(cost_matrix[i][j])) for j in range(size))
            f.write(row + '\n')
        f.write("EOF\n")


def create_parameter_file(filename,runs=1):
    with open(f"{matrix_storage_location}{filename}.par", 'w') as f:
        f.write(f"PROBLEM_FILE = {matrix_storage_location}{filename}.tsp\n")
        f.write(f"OUTPUT_TOUR_FILE = {matrix_storage_location}{filename}.tour\n")
        f.write(f"RUNS = {str(runs)}\n")
        f.write(f"KICKS = 4\n")
        f.write(f"SEED = {random.randint(1, 100000)}\n")
    return True
