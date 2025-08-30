import os
import time
from enum import Enum
from itertools import permutations

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectRadioButton import DirectRadioButton

from src.TSP import read_tsp


class ProblemType(Enum):
    BRUTE_FORCE = "BF"
    FIRST_SEARCH = "FS"


class Mode:
    def __init__(self, problem_type, default_problem):
        # notifier
        self.notify = directNotify.newCategory("Mode")
        # mode variables
        self._type = problem_type
        self._default = default_problem
        self.ui = []
        # files
        self.files = []
        self.generate_files()
        self.problem_buttons = []
        # last loaded
        self.last_loaded = None

    def build_ui(self):
        pass

    def destroy_ui(self):
        for element in self.ui:
            element.destroy()
        self.ui.clear()

    def activate(self, _map):
        self.notify.debug(f"Activating mode {self.type}")
        self.load_problem(_map, self.default, "default")
        self.build_ui()
        self.generate_buttons(_map)

    def deactivate(self):
        for button in self.problem_buttons:
            button.destroy()
        self.last_loaded = None
        self.destroy_ui()
        self.problem_buttons.clear()

    def generate_files(self):
        dir_path = f"src/tsp/{self.type.value}"
        if not os.path.exists(dir_path):
            self.notify.warning(f"Directory {dir_path} does not exist.")
            return
        for file in os.listdir(dir_path):
            if file.endswith(".tsp"):
                self.files.append(file)

    def generate_buttons(self, _map):
        self.problem_buttons.clear()
        for index, file in enumerate(self.files):
            col = index % 3
            row = index // 3
            button = DirectRadioButton(
                text=file.replace('.tsp', ''),
                scale=0.07,
                frameColor=(0.8, 0.8, 0.8, 1),
                pos=(-1 + col * 0.4, 0, -row * 0.15 - 0.6),
                variable=[self.last_loaded],
                value=[file],
                command=self.load_problem,
                extraArgs=[_map, file, f"drb{file}"]
            )
            self.problem_buttons.append(button)
        for button in self.problem_buttons:
            button.setOthers(self.problem_buttons)

    def load_problem(self, _map, file, src=""):
        self.notify.debug(f"Loading problem {file} from {src}")
        if _map.get_current_loaded_file() == file or self.last_loaded == file:
            self.notify.warning("Problem already loaded.")
            return
        imported_tsp = read_tsp(self.type, file)
        self.last_loaded = file
        _map.TSP = imported_tsp

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        self._default = value


class FirstSearchMode(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.FIRST_SEARCH, '11PointDFSBFS.tsp')
        self.map = _map

    def build_ui(self):
        pass


class BruteForceMode(Mode):
    def __init__(self, _map):
        super().__init__(ProblemType.BRUTE_FORCE, 'Random4.tsp')
        self.map = _map

    def build_ui(self):
        generate_routes_button = DirectButton(text="Generate Routes", scale=0.07,
                                              pos=(1, 0, -0.9),
                                              command=self.generate_routes)
        reset_button = DirectButton(text="Reset", scale=0.07,
                                    pos=(1, 0, -0.8),
                                    command=self.map.reset)
        self.ui.append(generate_routes_button)
        self.ui.append(reset_button)

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
        with open(f"results/{self.map.TSP.name}.txt", "w") as f:
            f.write("----- Results -----\n")
            for distance, route in results:
                f.write(f"Distance: {distance}, Route: {', '.join(route)}\n")
            f.write("-------------------")
            f.flush()
            os.fsync(f.fileno())
        elapsed = time.perf_counter() - start_time
        with open(f"results/{self.map.TSP.name}_time.txt", "w") as f:
            f.write(f"Time taken: {elapsed} seconds\n")
            f.flush()
            os.fsync(f.fileno())
        self.map.enable_rendering()
