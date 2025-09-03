from src.Bus import Stop
from src.modes.Mode import Mode, ProblemType


class FirstSearchMode(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.FIRST_SEARCH, '11PointDFSBFS.tsp')
        self.map = _map

    def on_mouse_click(self):
        self.notify.debug("FirstSearchMode mouse click")
        self.map.on_mouse_click("Stop")

    def build_ui(self):
        pass

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
        for stop in stops_to_make:
            city_from = self.map.cities[stop[0]-1]
            city_to = self.map.cities[stop[1]-1]
            new_stop = Stop(city_from.coords, city_to.coords)
            new_stop.reparentTo(self.map.bus.stops)
