from src.modes.Mode import Mode, ProblemType


class ClosestEdgeInsertionMode(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.CLOSEST_EDGE, 'Random30.tsp')
        self.map = _map

    def activate(self, _map):
        self.map.bus.making_stops = True
        Mode.activate(self, _map)
