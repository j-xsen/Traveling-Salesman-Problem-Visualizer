import math

from direct.gui.DirectButton import DirectButton

from src.modes.Mode import Mode, ProblemType
from src.bus.distance import distance


def point_to_edge_dist(p, a, b):
    px = p.x
    py = p.y
    ax = a.x
    ay = a.y
    bx = b.x
    by = b.y
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

class ClosestEdgeInsertionMode(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.CLOSEST_EDGE, 'Random30.tsp')
        self.map = _map

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

    def find_nearest_city_to_stop(self, stop):
        self.notify.debug(f"Finding nearest city to stop {stop.from_city.name}-{stop.to_city.name}...")
        stop_point_one = stop.from_city
        stop_point_two = stop.to_city
        nearest_city = None
        nearest_distance = float('inf')
        for city in self.map.cities:
            if city.name in self.map.route or city.name == stop.from_city.name or city.name == stop.to_city.name or str(city.name) in self.map.route:
                continue
            # Calculate distance from city to the line segment defined by stop_point_one and stop_point_two
            calc_dist = point_to_edge_dist(city.coords, stop_point_one, stop_point_two)
            if type(calc_dist) is not float:
                self.notify.error(f"Calculated distance is not a float: {calc_dist}")
                continue
            # self.notify.debug(f"Calculated distance: {calc_dist} to city {city.name}")
            if calc_dist < nearest_distance:
                nearest_distance = calc_dist
                nearest_city = city
        if nearest_city is not None:
            self.notify.debug(f"Nearest city to stop {stop.from_city.name}-{stop.to_city.name} is {nearest_city.name}"
                              f" at distance {nearest_distance}")
        return nearest_city, nearest_distance

    def expand_tour(self):
        self.notify.debug("Expanding tour...")
        if len(self.map.route) == 0:
            self.notify.debug("Route empty, selecting city 1 & nearest city")
            # select city 1 to start
            self.map.select_city("1")
            # find next closest city
            nearest_city = self.find_nearest_city()
            self.map.select_city(nearest_city.name)
            # loop to beginning
            self.map.select_city("1")
            return
        else:
            # unselect last city to allow for re-selection
            self.map.unselect_last_city()

        # loop through every edge in the current route
        nearest_city = None
        nearest_distance = float('inf')
        nearest_stop = None
        for i in range(len(self.map.route)-1):
            city_a = int(self.map.route[i])
            city_b = int(self.map.route[(i + 1) % len(self.map.route)])
            self.notify.debug(f"Checking edge from {city_a} to {city_b}")
            # get stop
            stop_path = self.map.bus.stop_nodes.find(f"**/{city_a}-{city_b}")
            if stop_path.isEmpty():
                self.notify.error(f"Stop {city_a}-{city_b} not found")
                continue
            stop = stop_path.getPythonTag("stopobj")
            # find nearest city to this stop
            cur_nearest_city, cur_nearest_distance = self.find_nearest_city_to_stop(stop)
            if cur_nearest_city is not None:
                if cur_nearest_distance < nearest_distance:
                    nearest_distance = cur_nearest_distance
                    nearest_city = cur_nearest_city
                    nearest_stop = stop
        self.notify.debug(f"Nearest city to current route is {nearest_city.name} at distance {nearest_distance}"
                          f" via stop {nearest_stop.from_city.name}-{nearest_stop.to_city.name}")

        # loop back to beginning
        self.map.select_city(self.map.route[0])

    def build_ui(self):
        reset_button = DirectButton(text="Reset", scale=0.07,
                                    pos=(1, 0, -0.8),
                                    command=self.map.reset)
        expand_tour = DirectButton(text="Expand Tour", scale=0.07,
                                   pos=(1, 0, -0.9),
                                   command=self.expand_tour)
        self.ui.append(reset_button)
        self.ui.append(expand_tour)

    def on_mouse_click(self):
        # accept mouse
        selected_city = self.map.on_mouse_click("ClickableCity")
        if selected_city is None:
            return
        self.map.select_city(str(selected_city).split("-")[1])
