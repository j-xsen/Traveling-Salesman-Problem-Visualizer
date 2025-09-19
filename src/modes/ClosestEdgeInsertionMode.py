from direct.gui.DirectButton import DirectButton

from src.modes.Mode import Mode, ProblemType
from src.bus.distance import distance


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

    def find_nearest_city(self):
        self.notify.debug("Finding nearest city...")
        last_city = int(self.map.route[-1])
        nearest_city = None
        nearest_distance = float('inf')
        for city in self.map.cities:
            self.notify.debug(f"Route: {self.map.route}, Last city: {last_city}, Checking city: {city.name}")
            if city.name in self.map.route or city.name == last_city or str(city.name) in self.map.route:
                continue
            calc_dist = distance(self.map.cities[last_city-1].coords, city.coords)
            if type(calc_dist) is not float:
                self.notify.error(f"Calculated distance is not a float: {calc_dist}")
                continue
            self.notify.debug(f"Calculated distance: {calc_dist} to city {city.name}")
            if calc_dist < nearest_distance:
                nearest_distance = calc_dist
                nearest_city = city
        return nearest_city

    def expand_tour(self):
        if len(self.map.route) == 0:
            # select city 1 to start
            self.map.select_city("1")
            # find next closest city
            nearest_city = self.find_nearest_city()
            self.map.select_city(nearest_city.name)
        else:
            # unselect last city to allow re-selection
            self.map.unselect_last_city()


        # loop through every edge in the current route
        for i in range(len(self.map.route)):
            city_a = int(self.map.route[i])
            city_b = int(self.map.route[(i + 1) % len(self.map.route)])
            self.notify.debug(f"Checking edge from {city_a} to {city_b}")

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
