from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from src.bus.distance import distance


class People(DirectObject):
    def __init__(self, name="People"):
        DirectObject.__init__(self)
        self.notify = directNotify.newCategory(name)
        self.name = name
        self.route = []
        self.distance = 0
        self.generate_route()
        self.calculate_distance()

    def __str__(self):
        return self.name

    def generate_route(self):
        pass

    def load_route(self, rte):
        self.notify.debug(f"Loading rte: {rte}")
        city_copy = base.map.cities[:]
        self.route = []
        for stop in rte:
            self.route.append(city_copy[stop-1])
        self.calculate_distance()

    def calculate_distance(self):
        total_distance = 0
        for i in range(len(self.route) - 1):
            total_distance += distance(self.route[i].coords, self.route[i + 1].coords)
        self.distance = total_distance
        return self.distance
