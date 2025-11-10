import random
import subprocess
import sys
from time import sleep

import numpy
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, NodePath, FrameBufferProperties, ButtonThrower, GraphicsWindow, ButtonHandle
from panda3d_tools import text_stats
from scipy.special import betaincinv
from direct.gui import DirectGuiGlobals as DGG

from src.modes.GeneticAlgorithm.GeneticAlgorithm import CrossoverType
from src.modes.WisdomOfCrowds.ui.CrowdDisplay import CrowdDisplay
from src.modes.WisdomOfCrowds.ui.PeoplePicker import PeoplePicker

bh = ButtonHandle("b")


class CrowdManager(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.notify = directNotify.newCategory("CrowdManager")
        self.ui = []

        # crowd
        self.crowd = []
        self.crowd_size = 10

        self.people_picker = None
        self.crowd_display = None
        self.accept("close-crowd-manager-window", self.destroy)

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

    def build_ui(self):
        frame = DirectFrame(frameColor=(0, 0, 0, 1),
                            frameSize=(0, 1, 0, 1),
                            pos=(0, 0, 0),
                            parent=base.a2dBottomRight)
        self.ui.append(frame)

        crowd_np = frame.attachNewNode("crowd_np")
        crowd_size_label = DirectLabel(text="Crowd Size:",
                                       scale=0.07, pos=(-.5,0,.155),
                                       text_pos=(0,0),
                                       text_fg=(1,1,1,1),
                                       frameColor=(0,0,0,0),
                                       parent=crowd_np)
        self.ui.append(crowd_size_label)
        crowd_size = DirectEntry(text="", scale=0.07, initialText=str(self.crowd_size),
                                 parent=crowd_np, pos=(-.3, 0, .14),
                                 text_pos=(0.15,0.2),
                                 text_fg=(1,1,1,1), frameSize=(0, 2, 0, 1),
                                 frameColor=(1, 1, 1, 0.5), width=2.5,
                                 command=self.adjust_crowd_size)
        self.ui.append(crowd_size)

        make_new_crowd_button = DirectButton(text="Create new Crowd", scale=0.07,
                                             pos=(-.35, 0, .05),
                                             command=self.generate_crowd,
                                             frameColor=(
                                                 (0.8, 0.8, 0.8, 1),  # Normal
                                                 (0.9, 0.9, 0.9, 1),  # Click
                                                 (0.7, 0.7, 0.7, 1),  # Hover
                                                 (0.5, 0.5, 0.5, 1)  # Disabled
                                             ), parent=frame)
        self.ui.append(make_new_crowd_button)

        # show LKH tour button
        lkh_frame = DirectFrame(frameColor=(.5, .5, .5, 1),
                                relief=DGG.RAISED,
                                borderWidth=(0.01, 0.01),
                                frameSize=(-0.3, 0.3, -0.1, 0.1),
                                pos=(-1.25, 0, .15),
                                parent=frame)
        self.ui.append(lkh_frame)
        lkh_title = DirectLabel(text="LKH Tour:",
                                scale=0.07,
                                text_fg=(1, 1, 1, 1),
                                frameColor=(0, 0, 0, 0),
                                pos=(0, 0, .025),
                                parent=lkh_frame)
        self.ui.append(lkh_title)
        show_lkh_tour_button = DirectButton(text="Show", scale=0.07,
                                             pos=(.16, 0, -.06),
                                             command=self.show_lkh_tour, parent=lkh_frame)
        self.ui.append(show_lkh_tour_button)
        generate_new_lkh_tour_button = DirectButton(text="Generate", scale=0.07,
                                             pos=(-.11, 0, -.06),
                                                    extraArgs=["crowd"],
                                             command=self.run_hlk, parent=lkh_frame)
        self.ui.append(generate_new_lkh_tour_button)

        self.people_picker = PeoplePicker(frame)
        self.crowd_display = CrowdDisplay(self.crowd, frame)
        self.ui.append(self.crowd_display)
        self.ui.append(self.people_picker)

    def show_lkh_tour(self):
        self.notify.debug("Showing LKH Tour...")
        tour_file = f"{matrix_storage_location}crowd.tour"
        self.notify.debug(f"Reading tour from {tour_file}...")
        try:
            with open(tour_file, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            self.notify.error(f"Tour file {tour_file} not found. Please generate a crowd first.")
            return
        tour = []
        reading_tour = False
        for line in lines:
            line = line.strip()
            if line == "TOUR_SECTION":
                reading_tour = True
                continue
            if line == "EOF":
                break
            if reading_tour:
                if line.isdigit():
                    city_index = int(line) - 1
                    tour.append(city_index)
        self.notify.debug(f"Read tour: {tour}")
        tour.append(tour[0])
        self.show_route(tour)

    def run_hlk(self, name):
        subprocess.run(["LKH", f"{matrix_storage_location}{name}.par"], check=True)

    def show_route(self, route):
        base.map.reset()
        self.notify.debug(f"Showing route : {route}")
        for stop in route:
            base.map.select_city(stop)

    def generate_crowd(self):
        self.notify.debug("Making new crowd...")
        self.crowd = []
        for _ in range(self.crowd_size):
            person = self.people_picker.pick_a_person()
            self.crowd.append(person)
        self.crowd_display.update_display(self.crowd)
        agreement_matrix = self.create_agreement_matrix()
        # create files
        cost_matrix_to_tsp("crowd", agreement_matrix)
        create_parameter_file("crowd")
        self.run_hlk("crowd")

    def create_agreement_matrix(self):
        self.notify.debug("Creating agreement matrix...")
        size = len(self.crowd)
        route_size = len(base.map.cities)
        self.notify.debug(f"Crowd size: {size}, Route size: {route_size}")
        connections = 0
        matrix = numpy.array([[0 for _ in range(route_size)] for _ in range(route_size)], dtype=float)
        for i in range(size):
            route = self.crowd[i].route
            for j in range(size):
                connection_start = int(route[j].get_name()[5:])-1
                if j == len(route) - 1:
                    connection_end = int(route[0].get_name()[5:])-1
                else:
                    connection_end = int(route[j+1].get_name()[5:])-1
                connections+=1
                # matrix[min(connection_start, connection_end)][max(connection_start, connection_end)] += 1
                matrix[connection_start][connection_end] += 1
                matrix[connection_end][connection_start] += 1
        # agreement
        agreement = matrix / size
        agreement = numpy.clip(agreement, 0.0, 1.0)

        # power transform
        b1 = b2 = 3
        eps = 1e-12
        A_clip = numpy.clip(agreement, eps, 1.0-eps)
        C_beta = 1.0 - betaincinv(b1, b2, A_clip)
        C_int = numpy.round(C_beta*100000).astype(int)
        return C_int

    def generate_child(self, parent_list):
        self.notify.debug("Generating new child...")
        parent1, parent2 = random.choices(parent_list, k=2)  # select two

        crossover_type = random.choice(list(CrossoverType))
        child_route = None
        if crossover_type == CrossoverType.ORDERED:
            # random crossover point
            cutpoint = random.randint(1, len(parent1.route) - 2)
            child_route = parent1.route[:cutpoint]
            # add remainder from parent2
            for city in parent2.route:
                if city not in child_route:
                    child_route.append(city)
        elif crossover_type == CrossoverType.PARTIAL_MAP:
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
            self.notify.debug(f"Generated child route: {child_route}")

        return child_route

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

def create_parameter_file(filename):
    with open(f"{matrix_storage_location}{filename}.par", 'w') as f:
        f.write(f"PROBLEM_FILE = {matrix_storage_location}{filename}.tsp\n")
        f.write(f"OUTPUT_TOUR_FILE = {matrix_storage_location}{filename}.tour\n")
        f.write("RUNS = 1\n")
