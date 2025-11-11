import random

from src.modes.WisdomOfCrowds.People.People import People


class Random(People):
    def __init__(self):
        super().__init__("Random")

    def generate_route(self):
        # select first city
        unvisited_cities = base.map.cities[:]
        if not unvisited_cities:
            self.notify.error("No cities available to generate route.")
            self.route = []
            return self.route
        route = []
        while unvisited_cities:
            next_city = random.choice(unvisited_cities)
            route.append(next_city)
            unvisited_cities.remove(next_city)
        route.append(route[0])
        self.notify.debug("Generated route: " + " -> ".join(str(city.name) for city in route))
        self.route = route
        return self.route
