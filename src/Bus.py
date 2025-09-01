import math

from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import NodePath, TextNode, PandaNode


def distance(point1, point2):
    """Calculate the Euclidean distance between two points in 2D space."""
    if point1 is None or point2 is None:
        return 0
    return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5


# class for each bus stop
# mostly visual
class Stop(NodePath):
    def __init__(self, from_city, to_city):
        NodePath.__init__(self, "Stop")
        self.setTag("Stop", f"{from_city.name}-{to_city.name}")
        self.notify = directNotify.newCategory("Stop")
        self.notify.debug(f"Creating stop from {from_city} to {to_city}")
        self.from_city = from_city
        self.to_city = to_city

        # # ARROW BODY
        self.model = loader.loadModel("arrow_body.bam")
        self.model.setColor((1, 1, 1, 1))

        # compute roll
        dx = to_city.x - from_city.x
        dz = to_city.y - from_city.y
        theta = math.degrees(math.atan2(dz, dx))
        roll = (90 - theta) % 360

        # position and scale
        self.model.setHpr(0, 0, roll)
        self.model.setPos(from_city.x - 50 + (to_city.x - from_city.x) / 2,
                          0,
                          from_city.y - 50 + (to_city.y - from_city.y) / 2)
        self.model.setScale(2, 5, 4*distance(from_city, to_city)/10)

        # # ARROW HEAD
        head_x = from_city.x - 50 + (to_city.x - from_city.x) * 0.9
        head_z = from_city.y - 50 + (to_city.y - from_city.y) * 0.9
        arrow_head = loader.loadModel("arrow_head.bam")
        arrow_head.setColor((1, 1, 1, 1))
        arrow_head.setHpr(0, 0, roll)
        arrow_head.setPos(head_x, 0, head_z)
        arrow_head.setScale(3, 3, 3)
        arrow_head.reparentTo(self)

        # reparent
        self.model.reparentTo(self)


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
        self.stops = NodePath("Stops")
        self.stops.reparentTo(self)

    def add_stop(self, to_city_coords):
        if self.making_stops:
            self.notify.debug(f"Adding stop to {to_city_coords}")
            if self.current_coords is not None:
                new_stop = Stop(self.current_coords, to_city_coords)
                new_stop.reparentTo(self.stops)
        self.current_coords = to_city_coords

    def reset(self):
        self.current_coords = None
        self.distance_traveled = 0
        self.stops.removeNode()
        self.stops = NodePath("Stops")
        self.stops.reparentTo(self)

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
