import os
import time
from itertools import permutations

from direct.gui.DirectButton import DirectButton

from src.modes.Mode import Mode, ProblemType


class BruteForceMode(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.BRUTE_FORCE, 'Random4.tsp', _map)

    def build_ui(self):
        generate_routes_button = DirectButton(text="Generate Routes", scale=0.07,
                                              pos=(1, 0, -0.9),
                                              command=self.generate_routes)
        reset_button = DirectButton(text="Reset", scale=0.07,
                                    pos=(1, 0, -0.8),
                                    command=self.map.reset)
        self.ui.append(generate_routes_button)
        self.ui.append(reset_button)

    def on_mouse_click(self):
        # accept mouse
        selected_city = self.map.on_mouse_click("ClickableCity")
        if selected_city is None:
            return
        if self.map.route_complete:
            self.map.reset()
        self.map.select_city(str(selected_city).split("-")[1])

    def generate_routes(self):
        self.map.disable_rendering()
        start_time = time.perf_counter()
        results = []
        for p in permutations(range(len(self.map.cities))):
            self.map.reset()
            for city_index in p:
                self.map.select_city(str(city_index + 1))
            self.map.select_city(str(p[0] + 1))  # return to start
            results.append((self.map.bus.distance_traveled, self.map.route))
        results.sort(key=lambda x: x[0])
        with open(f"results/{self.map.tsp.name}.txt", "w") as f:
            f.write("----- Results -----\n")
            for distance, route in results:
                f.write(f"Distance: {distance}, Route: {', '.join(route)}\n")
            f.write("-------------------")
            f.flush()
            os.fsync(f.fileno())
        elapsed = time.perf_counter() - start_time
        with open(f"results/{self.map.tsp.name}_time.txt", "w") as f:
            f.write(f"Time taken: {elapsed} seconds\n")
            f.flush()
            os.fsync(f.fileno())
        self.map.enable_rendering()
