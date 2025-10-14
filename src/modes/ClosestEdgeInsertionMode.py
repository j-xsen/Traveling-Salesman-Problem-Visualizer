import os
import time

from direct.gui.DirectButton import DirectButton

from src.modes.Mode import Mode, ProblemType
from src.bus.distance import distance, edge_distance

class ClosestEdgeInsertionMode(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.CLOSEST_EDGE, 'Random30.tsp', _map)

    def activate(self, _map):
        self.map.bus.making_stops = True
        self.map.calc_route_complete = False
        Mode.activate(self, _map)

    def deactivate(self):
        self.map.calc_route_complete = True
        Mode.deactivate(self)

    def find_nearest_city(self, param_city=None):
        self.notify.debug("Finding nearest city...")
        last_city = int(param_city) if param_city is not None else int(self.map.route[-1])
        nearest_city = None
        nearest_distance = float('inf')
        for city in self.map.cities:
            # self.notify.debug(f"Route: {self.map.route}, Last city: {last_city}, Checking city: {city.name}")
            if city.name in self.map.route or city.name == last_city or str(city.name) in self.map.route:
                continue
            calc_dist = distance(self.map.cities[last_city-1].coords, city.coords)
            if type(calc_dist) is not float:
                self.notify.error(f"Calculated distance is not a float: {calc_dist}")
                continue
            # self.notify.debug(f"Calculated distance: {calc_dist} to city {city.name}")
            if calc_dist < nearest_distance:
                nearest_distance = calc_dist
                nearest_city = city
        return nearest_city

    def expand_tour(self):
        # check if complete
        if self.map.route_complete:
            self.notify.warning("Route already complete, cannot expand tour")
            return
        self.notify.debug("Expanding tour...")

        # initialize route if empty
        if len(self.map.route) == 0:
            self.notify.debug("Route empty, selecting city 1 & nearest city")
            # select city 1 to start
            self.map.select_city(1)
            # find next closest city
            nearest_city = self.find_nearest_city()
            self.map.select_city(nearest_city.name)
            # loop to beginning
            self.map.select_city(1)
            return
        elif len(self.map.route) == 1:
            self.notify.debug("Route has one city, selecting nearest city")
            nearest_city = self.find_nearest_city()
            self.map.select_city(nearest_city.name)
            # loop to beginning
            self.map.select_city(self.map.route[0])
            return

        self.notify.debug(f"Current route: {self.map.route}")

        lowest_cost = float('inf')
        nearest_city = None
        stop_number = None
        for city in self.map.cities:
            # skip visited
            if city.name in self.map.route or str(city.name) in self.map.route:
                continue

            # visit each edge
            i = 1  # (starts at 1 to place after from_city)
            for stop in self.map.bus.stop_nodes.getChildren():
                # get stop object
                stop_obj = stop.getPythonTag("stopobj")
                if stop_obj is None:
                    self.notify.error(f"Stop object not found for stop {stop}")
                    continue

                # compute edge cost
                edge_cost = edge_distance(city.coords, stop_obj.from_city, stop_obj.to_city)
                # self.notify.debug(f"Edge cost to insert city {city.name} between {stop_obj.from_city.name}-{stop_obj.to_city.name} is {edge_cost}")

                if edge_cost < lowest_cost:
                    lowest_cost = edge_cost
                    nearest_city = city
                    stop_number = i
                i += 1
        # insert
        if nearest_city is None or stop_number is None:
            self.notify.warning("No nearest city or cheapest edge found, cannot expand tour")
            self.map.complete_route()
            return
        self.map.route.insert(stop_number, nearest_city.name)

        # redraw route
        self.redraw_route()

    def redraw_route(self):
        self.notify.debug("Redrawing route...")
        saved_route = self.map.route.copy()
        self.map.reset()
        for city_id in saved_route:
            self.map.select_city(city_id)
        self.notify.debug("Redrew route.")

    def generate_full_tour(self):
        self.notify.debug("Generating full tour...")
        start_time = time.perf_counter()
        self.map.reset()
        while not self.map.route_complete:
            self.expand_tour()
        elapsed = time.perf_counter() - start_time
        with open(f"results/CEI-{self.map.tsp.name}.txt", "w") as f:
            f.write(f"Route found: {', '.join(map(str, self.map.route))}\n")
            f.write(f"Distance: {self.map.bus.distance_traveled}\n")
            f.write(f"Time taken: {elapsed} seconds\n")
            f.flush()
            os.fsync(f.fileno())
        self.notify.debug("Generated full tour.")

    def recreate_files_buttons(self, new_type):
        self.notify.debug(f"Recreating files and buttons for type {new_type}...")

        if new_type is None:
            self.notify.error("New problem type is None, cannot recreate files and buttons.")
            return

        self.clear_problem_buttons()
        self.generate_files(new_type)
        self.generate_buttons(self.map)

    def build_ui(self):
        reset_button = DirectButton(text="Reset", scale=0.07,
                                    pos=(1, 0, -0.7),
                                    command=self.map.reset)
        expand_tour = DirectButton(text="Expand Tour", scale=0.07,
                                   pos=(1, 0, -0.8),
                                   command=self.expand_tour)
        generate_tour_button = DirectButton(text="Generate Full Tour", scale=0.07,
                                              pos=(1, 0, -.92),
                                              command=self.generate_full_tour)
        view_bfs_button = DirectButton(text="Brute Files", scale=0.07,
                                       command=self.recreate_files_buttons,
                                       pos=(-1, 0, 0.6), extraArgs=[ProblemType.BRUTE_FORCE])
        view_cei_button = DirectButton(text="CEI Files", scale=0.07,
                                       command=self.recreate_files_buttons,
                                        pos=(-1, 0, 0.5), extraArgs=[ProblemType.CLOSEST_EDGE])
        view_dfs_button = DirectButton(text="DFS Files", scale=0.07,
                                       command=self.recreate_files_buttons,
                                       pos=(-1, 0, 0.4), extraArgs=[ProblemType.FIRST_SEARCH])
        self.ui.append(reset_button)
        self.ui.append(expand_tour)
        self.ui.append(generate_tour_button)
        self.ui.append(view_bfs_button)
        self.ui.append(view_cei_button)
        self.ui.append(view_dfs_button)

    def on_mouse_click(self):
        # accept mouse
        selected_city = self.map.on_mouse_click("ClickableCity")
        if selected_city is None:
            return
        self.map.select_city(int(str(selected_city).split("-")[1]))
