from enum import Enum
import os

from direct.gui.DirectRadioButton import DirectRadioButton

from src.TSP import read_tsp


class ProblemType(Enum):
    BRUTE_FORCE = "BF"
    FIRST_SEARCH = "FS"

class Mode:
    def __init__(self, problem_type, default_problem):
        # mode variables
        self._type = problem_type
        self._default = default_problem
        # files
        self.files = []
        self.generate_files()
        self.problem_buttons = []
        # last loaded
        self.last_loaded = None

    def activate(self, _map):
        print(f"Activating mode {self.type}")
        self.load_problem(_map, self.default, "default")
        self.generate_buttons(_map)

    def deactivate(self):
        for button in self.problem_buttons:
            button.destroy()
        self.last_loaded = None
        self.problem_buttons.clear()

    def generate_files(self):
        dir_path = f"src/tsp/{self.type.value}"
        if not os.path.exists(dir_path):
            print(f"Directory {dir_path} does not exist.")
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
        print(f"Loading problem {file} from {src}")
        if _map.get_current_loaded_file() == file or self.last_loaded == file:
            print("Problem already loaded.")
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

BRUTE_FORCE_MODE = Mode(ProblemType.BRUTE_FORCE, 'Random4.tsp')
FIRST_SEARCH_MODE = Mode(ProblemType.FIRST_SEARCH, '11PointDFSBFS.tsp')
