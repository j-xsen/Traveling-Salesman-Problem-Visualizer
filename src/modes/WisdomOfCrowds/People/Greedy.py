import random

from src.modes.WisdomOfCrowds.People.Person import Person


class Greedy(Person):
    def generate_route(self):
        # select first city
        unvisited_cities = self.cities[:]
        first_city = random.choice(self.cities)
        route = [first_city]
        unvisited_cities.remove(first_city)
        while unvisited_cities:
            last_city = route[-1]
            # find nearest unvisited city
            nearest_city = min(unvisited_cities, key=lambda city: last_city.distance_to(city))
            route.append(nearest_city)
            unvisited_cities.remove(nearest_city)
        self.notify.debug("Generated route: " + " -> ".join(str(city.name) for city in route))
        return route
