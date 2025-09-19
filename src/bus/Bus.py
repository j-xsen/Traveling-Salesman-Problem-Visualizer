from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import NodePath, TextNode

from src.bus.Stop import Stop
from src.bus.distance import distance


class Bus(NodePath):
    def __init__(self):
        NodePath.__init__(self, "Bus")
        self.notify = directNotify.newCategory("Bus")
        self._distance_traveled = 0
        self._current_coords = None

        self.making_stops = True

        # gui
        distance_text = TextNode("distance")
        distance_text.setText(f"Distance traveled: {self._distance_traveled}")
        distance_text.setAlign(TextNode.ALeft)
        self.distance_text_path = aspect2d.attachNewNode(distance_text)
        self.distance_text_path.setScale(0.07)
        self.distance_text_path.setPos(-1.3, 0, 0.9)
        self.stop_nodes = NodePath("Stops")
        self.stop_nodes.reparentTo(self)

    def complete_route(self):
        for child in self.stop_nodes.getChildren():
            child.selected = False
            child.route_complete = True

    # Brute force
    def add_stop(self, to_city_coords):
        if self.making_stops:
            self.notify.debug(f"Adding stop to {to_city_coords}")
            if self.current_coords is not None:
                new_stop = Stop(self.current_coords, to_city_coords)
                new_stop.reparentTo(self.stop_nodes)
        self.current_coords = to_city_coords

    def reset(self):
        self.reset_to(None)
        self.distance_traveled = 0
        if self.making_stops:
            self.stop_nodes.removeNode()
            self.stop_nodes = NodePath("Stops")
            self.stop_nodes.reparentTo(self)

    def reset_to(self, to_city_coords):
        # remove distance
        self.notify.debug(f"Resetting bus to {to_city_coords}")
        dist = self.distance(to_city_coords)
        self.current_coords = to_city_coords
        self.distance_traveled -= dist*2 # remove distance to city and back

    def remove_stop(self, stop_name):
        self.notify.debug(f"Removing stop {stop_name}")
        if self.making_stops:
            stop = self.stop_nodes.find(f"**/{stop_name}")
            if not stop.isEmpty():
                stop.removeNode()
            else:
                self.notify.warning(f"Stop {stop_name} not found")

    @property
    def distance_traveled(self):
        return self._distance_traveled

    @distance_traveled.setter
    def distance_traveled(self, value):
        self._distance_traveled = value
        self.distance_text_path.node().setText(f"Distance traveled: {self._distance_traveled}")

    @property
    def current_coords(self):
        return self._current_coords

    @current_coords.setter
    def current_coords(self, value):
        self.distance_traveled += self.distance(value)
        self._current_coords = value

    def distance(self, point2):
        if self._current_coords is None or point2 is None:
            return 0
        return distance(self._current_coords, point2)

    def render(self):
        pass
