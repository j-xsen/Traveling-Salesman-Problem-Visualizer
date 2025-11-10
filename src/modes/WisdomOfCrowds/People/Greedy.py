import random

from src.bus.distance import distance
from src.modes.WisdomOfCrowds.People.People import People


class Greedy(People):
    def __init__(self):
        super().__init__("Greedy")
    def generate_route(self):
        # select first city
        unvisited_cities = base.map.cities[:]
        if not unvisited_cities:
            self.notify.error("No cities available to generate route.")
            self.route = []
            return self.route
        first_city = random.choice(unvisited_cities)
        route = [first_city]
        unvisited_cities.remove(first_city)
        while unvisited_cities:
            last_city = route[-1]
            # find nearest unvisited city
            nearest_city = min(unvisited_cities, key=lambda city: distance(last_city.coords, city.coords))
            route.append(nearest_city)
            unvisited_cities.remove(nearest_city)
        route.append(first_city)
        self.notify.debug("Generated route: " + " -> ".join(str(city.name) for city in route))
        self.route = route
        return self.route
