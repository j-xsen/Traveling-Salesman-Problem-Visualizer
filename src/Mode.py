import os
import time
from enum import Enum
from itertools import permutations

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectRadioButton import DirectRadioButton
from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger
from direct.task.TaskManagerGlobal import taskMgr

from src.Bus import Stop
from src.TSP import read_tsp


class ProblemType(Enum):
    BRUTE_FORCE = "BF"
    FIRST_SEARCH = "FS"


class Mode(DirectObject):
    def __init__(self, problem_type, default_problem):
        DirectObject.__init__(self)
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
        self.accept("TSPChanged", self.update_last_loaded)

    def on_mouse_click(self):
        self.notify.warning("Mouse click not handled in base Mode class")
        pass

    def destroy(self):
        self.ignoreAll()
        self.ui.clear()
        self.files.clear()
        self.problem_buttons.clear()

    def update_last_loaded(self, file):
        self.notify.debug(f"Updating last loaded to {file}")
        self.last_loaded = file

    def build_ui(self):
        pass

    def destroy_ui(self):
        for button in self.problem_buttons:
            button.destroy()
        self.problem_buttons.clear()

    def activate(self, _map):
        self.notify.debug(f"Activating mode {self.type}")
        self.accept("mouse1-up", self.on_mouse_click)
        self.load_problem(_map, self.default, "default")
        self.generate_buttons(_map)
        self.build_ui()

    def deactivate(self):
        for button in self.problem_buttons:
            button.destroy()
        self.last_loaded = None
        self.destroy()
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
        self.notify.debug(f"Generating buttons for {len(self.files)} files.")
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
                extraArgs=[_map, file, f"drb{file}"]
            )
            if file == _map.get_current_loaded_file():
                button.set_state(True)
            self.problem_buttons.append(button)
        for button in self.problem_buttons:
            button.setOthers(self.problem_buttons)
            button['command'] = self.load_problem
            button['extraArgs'] = [_map, button['value'][0], f"drb{button['value'][0]}"]

    def load_problem(self, _map, file, src=""):
        self.notify.debug(f"Loading problem {file} from {src}")
        if _map.get_current_loaded_file() == file or self.last_loaded == file:
            self.notify.warning("Problem already loaded.")
            return
        imported_tsp = read_tsp(self.type, file)
        _map.TSP = imported_tsp
        self.last_loaded = file

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

    def on_mouse_click(self):
        self.notify.debug("BruteForceMode mouse click")
        # accept mouse
        self.map.on_mouse_click("ClickableCity")

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
