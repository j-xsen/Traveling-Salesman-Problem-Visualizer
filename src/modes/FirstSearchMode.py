from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

from src.bus.Bus import Stop
from src.modes.Mode import Mode, ProblemType


class FirstSearchMode(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.FIRST_SEARCH, '11PointDFSBFS.tsp')
        self.map = _map
        self.stops = {}
        self.route_complete = False
        self._current_city = None
        self._final_city = None

    def activate(self, _map):
        super().activate(_map)
        self.map.bus.making_stops = False

    def reset(self):
        self.current_city = None
        self.final_city = None
        self.route_complete = False
        for stop in self.stops.values():
            stop.selected = False
        self.map.reset()

    @property
    def current_city(self):
        return self._current_city
    @current_city.setter
    def current_city(self, value):
        # check if resetting
        if value is None:
            self.ui[1].setText(f"Starting City: None")
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
            self.ui[1].setText(f"Starting City: {value}")
        # set city
        self._current_city = value
        # check if final city reached
        if self.final_city is not None and int(self.final_city) == self.current_city:
            self.notify.debug(f"Final city {self.final_city} reached!")
            self.complete_route()
        self.notify.debug(f"Current city set to {self.current_city}")

    def complete_route(self):
        self.route_complete = True
        for stop in self.stops.values():
            stop.route_complete = True
        self.map.complete_route()

    @property
    def final_city(self):
        return self._final_city
    @final_city.setter
    def final_city(self, value):
        self._final_city = value
        self.ui[2].setText(f"Final City: {self.final_city if self.final_city else 'None'}")

    def is_valid_next_city(self, city_name):
        if self.current_city is None:
            self.notify.debug("No current city, any city is valid")
            return True
        for stop in self.stops.values():
            if int(stop.from_city.name) == int(self.current_city):
                if stop.to_city.name == city_name:
                    self.notify.debug(f"Valid next city found {city_name}")
                    return True
        return False

    def deactivate(self):
        Mode.deactivate(self)
        self.stops = {}
        self._current_city = None

    def on_mouse_click(self):
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
                self.final_city = str(selected_city).split("-")[1]
                self.map.get_city(self.final_city).last_city = True
                self.notify.debug(f"Final city set to {self.final_city}")
            return
        # check if stop clicked
        obj = self.map.on_mouse_click("Stop")
        if obj is None:
            return
        stop_name = str(obj).split('/')[-1]
        self.notify.debug(f"Clicked on stop {stop_name}")

        # check if from valid
        # ensure proper from
        if int(self.stops[stop_name].from_city.name) != int(self.current_city):
            self.notify.warning(f"Stop {self.stops[stop_name].from_city.name} is not a valid stop from current city {self.current_city}")
            return
        # ensure proper to
        if not self.is_valid_next_city(self.stops[stop_name].to_city.name):
            self.notify.warning(f"Stop {stop_name} is not a valid next stop from city {self.current_city}")
            return
        # select stop
        self.map.select_city(self.stops[stop_name].to_city.name)
        self.current_city = self.stops[stop_name].to_city.name
        self.notify.debug(f"Current city updated to {self.current_city}")

        if stop_name in self.stops:
            selected_stop = self.stops[stop_name]
            selected_stop.selected = not selected_stop.selected
        else:
            self.notify.warning(f"Clicked stop not found in stops: {stop_name}")

    def build_ui(self):
        # reset button
        reset_button = DirectButton(text="Reset", scale=0.07,
                                    pos=(1, 0, -0.8),
                                    command=self.reset)
        self.ui.append(reset_button)

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
