import os
import time
from collections import deque
from queue import LifoQueue

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectRadioButton import DirectRadioButton
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

from src.bus.Bus import Stop
from src.modes.Mode import Mode, ProblemType


class FirstSearchMode(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.FIRST_SEARCH, '11PointDFSBFS.tsp', _map)
        self.stops = {}
        self.route_complete = False
        self._current_city = None
        self._final_city = None
        self._first_city = None

        self._search_type = "BFS"

        # search algorithm stuff
        self.searched_nodes = {}
        self.queue = deque()

    @property
    def search_type(self):
        return self._search_type
    @search_type.setter
    def search_type(self, value):
        if value in ["BFS", "DFS"]:
            self._search_type = value
            self.notify.debug(f"Search type set to {self._search_type}")
        else:
            self.notify.warning(f"Invalid search type: {value}")

    def find_stop_from_cities(self, from_city, to_city):
        for stop in self.stops.values():
            if int(stop.from_city.name) == int(from_city) and int(stop.to_city.name) == int(to_city):
                return stop
        return None

    def build_route_from_list(self, qd_city, parent_list):
        # build route
        self.notify.debug("Setting current city to first city")
        self._current_city=self.first_city
        route_list = []
        parent_loop = qd_city
        while parent_loop is not None:
            route_list.append(parent_loop)
            if parent_loop not in parent_list:
                self.notify.warning(f"Parent loop {parent_loop} not in parent list")
                break
            parent_loop = parent_list[parent_loop]
        route_list.reverse()
        # self.current_city = route_list[0]
        for i in range(1, len(route_list)):
            from_city = route_list[i - 1]
            to_city = route_list[i]
            stop = self.find_stop_from_cities(from_city, to_city)
            if stop is not None:
                self.select_stop(stop.name)
        self.complete_route()

    def do_breadth_first_search(self):
        self.queue = deque()
        self.notify.debug("Generating routes using BFS")

        # clear data
        self.searched_nodes.clear()

        # initial values
        self.searched_nodes[int(self.first_city)] = None
        self.queue.append(int(self.first_city))
        while self.queue:
            self.notify.debug(f"Begin Queue Loop: {self.queue}")
            qd_city = self.queue.popleft()

            # success case
            if self.final_city is not None and qd_city == int(self.final_city):
                self.build_route_from_list(qd_city, self.searched_nodes)
                return

            # add valid next cities to queue
            for city in self.list_valid_next_cities_of(qd_city):
                if city not in self.searched_nodes:
                    self.searched_nodes[city] = int(qd_city)
                    self.queue.append(city)

    def do_depth_first_search(self):
        self.notify.debug("Generating routes using DFS")

        self.queue = LifoQueue()

        # clear data
        self.searched_nodes.clear()
        parents = {}

        # initial values
        self.queue.put(int(self.first_city))
        while not self.queue.empty():
            qd_city = self.queue.get()
            self.notify.debug(f"Begin Stack Loop: {qd_city}")

            # success case
            if self.final_city is not None and qd_city == int(self.final_city):
                self.build_route_from_list(qd_city, parents)
                return

            if qd_city not in self.searched_nodes:
                self.notify.debug(f"Visiting city {qd_city}")
                self.searched_nodes[qd_city] = True
                for city in self.list_valid_next_cities_of(qd_city):
                    self.notify.debug(f"Checking city {city}")
                    if city not in self.searched_nodes:
                        parents[city] = qd_city
                        self.queue.put(city)
        self.notify.debug("No route found")

    def generate_routes(self):
        self.current_city = self.first_city
        self.map.reset()
        for stop in self.stops.values():
            stop.selected = False
            stop.route_complete = False
        start_time = time.perf_counter()
        if self.search_type == "BFS":
            self.do_breadth_first_search()
        else:
            self.do_depth_first_search()
        elapsed_time = time.perf_counter() - start_time
        self.notify.debug(f"Time elapsed: {elapsed_time}")
        with open(f"results/{self.search_type}_time.txt", "w") as f:
            f.write(str(elapsed_time))
            f.flush()
            os.fsync(f.fileno())

    def activate(self, _map):
        super().activate(_map)
        self.disable_generate_routes_button()
        self.map.bus.making_stops = False

    def reset(self):
        self.current_city = None
        self.final_city = None
        self.first_city = None
        self.route_complete = False
        self.searched_nodes = {}
        for stop in self.stops.values():
            stop.selected = False
            stop.route_complete = False
        self.map.reset()

    @property
    def first_city(self):
        return self._first_city
    @first_city.setter
    def first_city(self, value):
        self.notify.debug(f"Setting first city to {value}")
        self._first_city = value

    @property
    def current_city(self):
        return self._current_city
    @current_city.setter
    def current_city(self, value):
        # check if resetting
        if value is None:
            self.ui[2].setText(f"Starting City: None")
            self._current_city = None
            return
        # check if the route is started
        if self._current_city is not None:
            # route started; check if valid next city
            self.notify.debug("Checking if next city is valid")
            if not self.is_valid_next_city(value):
                self.notify.warning(f"City {value} is not a valid next city from {self.current_city}")
                return
        else:
            self.notify.debug("Setting starting city")
            self.ui[2].setText(f"Starting City: {value}")
            self.first_city = value
        # set city
        self._current_city = value
        self.notify.debug(f"Current city set to {self.current_city}")
        # check if final city reached
        if self.final_city is not None and int(self.final_city) == self.current_city:
            self.notify.debug(f"Final city {self.final_city} reached!")
            self.complete_route()

    def disable_generate_routes_button(self):
        self.ui[1]['state'] = "disabled"

    def enable_generate_routes_button(self):
        self.ui[1]['state'] = "normal"

    def complete_route(self):
        self.route_complete = True
        self.disable_generate_routes_button()
        for stop in self.stops.values():
            stop.route_complete = True
        self.map.complete_route()

    @property
    def final_city(self):
        return self._final_city
    @final_city.setter
    def final_city(self, value):
        if value is not None and value == self.current_city:
            self.notify.warning("Final city cannot be the same as starting city")
            return
        self._final_city = value
        self.ui[3].setText(f"Final City: {self.final_city if self.final_city else 'None'}")
        self.enable_generate_routes_button()

    def list_valid_next_cities(self):
        return self.list_valid_next_cities_of(int(self.current_city))

    def list_valid_next_cities_of(self, city_name):
        valid_cities = []
        if city_name is None:
            return valid_cities
        for stop in self.stops.values():
            if int(stop.from_city.name) == int(city_name):
                valid_cities.append(int(stop.to_city.name))
        return valid_cities

    def is_valid_next_city(self, city_name):
        if self.current_city is None:
            self.notify.debug("No current city, any city is valid")
            return True
        return int(city_name) in self.list_valid_next_cities()

    def deactivate(self):
        Mode.deactivate(self)
        self.stops = {}
        self._current_city = None
        self._final_city = None
        self.route_complete = False

    def select_stop(self, stop_name):
        # check if from valid
        # ensure proper from
        if int(self.stops[stop_name].from_city.name) != int(self.current_city):
            self.notify.warning(
                f"{stop_name} from {self.stops[stop_name].from_city.name} to {self.stops[stop_name].to_city.name} is not a valid stop from current city {self.current_city}")
            return
        # ensure proper to
        if not self.is_valid_next_city(self.stops[stop_name].to_city.name):
            self.notify.warning(f"Stop {stop_name} is not a valid next stop from city {self.current_city}")
            return
        # select stop
        self.map.select_city(self.stops[stop_name].to_city.name)
        self.current_city = self.stops[stop_name].to_city.name

        if stop_name in self.stops:
            selected_stop = self.stops[stop_name]
            selected_stop.selected = not selected_stop.selected
        else:
            self.notify.warning(f"Clicked stop not found in stops: {stop_name}")

    def on_mouse_click(self):
        if not self.route_complete:
            # is first city?
            if self.current_city is None or self.final_city is None:
                selected_city = self.map.on_mouse_click("ClickableCity")
                if selected_city is None:
                    return
                if self.current_city is None:
                    self.current_city = str(selected_city).split("-")[1]
                    self.notify.debug(f"Starting city set to {self.current_city}")
                    self.map.select_city(self.current_city)
                elif self.final_city is None:
                    city_id = str(selected_city).split("-")[1]
                    if city_id and str(city_id) != str(self.current_city):
                        self.final_city = city_id
                        if self.final_city:
                            self.map.get_city(self.final_city).last_city = True
                            self.notify.debug(f"Final city set to {self.final_city}")
                    else:
                        self.notify.warning("Final city selection failed")
                return
            # check if stop clicked
            obj = self.map.on_mouse_click("Stop")
            if obj is None:
                return
            stop_name = str(obj).split('/')[-1]
            self.notify.debug(f"Clicked on stop {stop_name}")

            self.select_stop(stop_name)

    def build_ui(self):
        # reset button
        reset_button = DirectButton(text="Reset", scale=0.07,
                                    pos=(1, 0, -0.8),
                                    command=self.reset)
        self.ui.append(reset_button)

        # generate routes button (disabled)
        generate_routes_button = DirectButton(text="Generate Routes", scale=0.07,
                                              pos=(1, 0, -0.9),
                                              state="disabled",
                                              frameColor=(
                                                  (0.8, 0.8, 0.8, 1),  # Normal
                                                  (0.9, 0.9, 0.9, 1),  # Click
                                                  (0.7, 0.7, 0.7, 1),  # Hover
                                                  (0.5, 0.5, 0.5, 1)  # Disabled
                                              ),
                                              command=self.generate_routes)
        self.ui.append(generate_routes_button)

        # starting city text
        starting_city_text = OnscreenText(text=f"Starting City: {self.current_city if self.current_city else 'None'}",
                                          fg=(1, 1, 1, 1),align=TextNode.ALeft,scale=0.07,pos=(-1.3,0.65),
                                          mayChange=True,)

        self.ui.append(starting_city_text)

        # final city text
        final_city_text_node = OnscreenText(text=f"Final City: {self.final_city if self.final_city else 'None'}",
                                            fg=(1, 1, 1, 1), align=TextNode.ALeft, scale=0.07, pos=(-1.3, 0.55),
                                            mayChange=True, )
        self.ui.append(final_city_text_node)

        # radio button group for search type
        buttons=[DirectRadioButton(text="BFS", scale=0.07, pos=(-1.1, 0, -0.8),
                                             variable=[self.search_type], value=["BFS"],
                                   command=self.set_search_type, extraArgs=["BFS"]),
        DirectRadioButton(text="DFS", scale=0.07, pos=(-.8, 0, -0.8),
                                      variable=[self.search_type], value=["DFS"],
                          command=self.set_search_type, extraArgs=["DFS"])]
        for button in buttons:
            button.setOthers(buttons)
            self.ui.append(button)

    def set_search_type(self, search_type):
        if search_type in ["BFS", "DFS"]:
            self.search_type = search_type
            if self.final_city is not None:
                self.enable_generate_routes_button()
            self.notify.debug(f"Search type set to {self.search_type}")
        else:
            self.notify.warning(f"Invalid search type: {search_type}")

    def load_problem(self, _map, file, src=""):
        super().load_problem(_map, file, src)
        # create stops
        # hard coding each file
        stops_to_make = []
        match file:
            case "11PointDFSBFS.tsp":
                stops_to_make = [[1,2],[1,3],[1,4],
                         [2,3],[3,4],[3,5],
                         [4,5],[4,6],[4,7],
                         [5,7],[5,8],
                         [6,8],
                         [7,9],[7,10],
                         [8,9],[8,10],[8,11],
                         [9,11],
                         [10,11]]

        if stops_to_make==[]:
            self.notify.warning(f"No stops defined for {file}")
            return
        i = 0
        for stop in stops_to_make:
            city_from = self.map.cities[stop[0]-1]
            city_to = self.map.cities[stop[1]-1]
            new_stop = Stop(city_from.coords, city_to.coords, name=f"Stop-{i}")
            self.stops[f"Stop-{i}"] = new_stop
            new_stop.reparentTo(self.map.bus.stop_nodes)
            i+=1
