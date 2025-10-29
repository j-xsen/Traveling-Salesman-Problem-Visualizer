import os
from enum import Enum

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectRadioButton import DirectRadioButton
from direct.showbase.DirectObject import DirectObject

from src.TSP import read_tsp


class ProblemType(Enum):
    BRUTE_FORCE = "BF"
    FIRST_SEARCH = "FS"
    CLOSEST_EDGE = "CE"
    GENETIC_ALGORITHM = "GA"
    WISDOM_OF_CROWDS = "WOC"


class Mode(DirectObject):
    def __init__(self, problem_type, default_problem, _map, name="Mode"):
        DirectObject.__init__(self)
        # notifier
        self.notify = directNotify.newCategory(name)
        # modes variables
        self._type = problem_type
        self._default = default_problem
        self.ui = []
        self.open_type = problem_type
        # files
        self.files = []
        self.generate_files()
        self.problem_buttons = []
        # last loaded
        self.last_loaded = None
        self.accept("TSPChanged", self.update_last_loaded)
        # map
        self.map = _map

    def on_mouse_click(self):
        self.notify.warning("Mouse click not handled in base Mode class")
        pass

    def destroy(self):
        self.destroy_ui()
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
        for element in self.ui:
            if type(element) is list:
                for sub_element in element:
                    if sub_element:
                        sub_element.destroy()
                continue
            element.destroy()
        self.ui.clear()

    def activate(self, _map):
        self.notify.debug(f"Activating modes {self.type}")
        self.accept("mouse1-up", self.on_mouse_click)
        self.load_problem(_map, self.default, "default")
        if not self.files:
            self.generate_files()
        self.generate_buttons(_map)
        self.build_ui()

    def deactivate(self):
        for button in self.problem_buttons:
            button.destroy()
        self.last_loaded = None
        self.destroy()
        self.problem_buttons.clear()

    def generate_files(self, open_type=None):
        if open_type is None:
            open_type = self.type
        self.open_type = open_type
        if type(open_type) is not ProblemType:
            self.notify.error(f"Invalid problem type: {type(open_type)}")
            return
        dir_path = f"src/tsp/{open_type.value}"
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
                pos=(-1 + col * 0.5, 0, -row * 0.15 - 0.6),
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

    def clear_problem_buttons(self):
        for button in self.problem_buttons:
            button.destroy()
        self.problem_buttons.clear()
        self.files.clear()

    def load_problem(self, _map, file, src=""):
        self.notify.debug(f"Loading problem {file} from {src}")
        if _map.get_current_loaded_file() == file or self.last_loaded == file:
            self.notify.warning("Problem already loaded.")
            return
        imported_tsp = read_tsp(self.open_type, file)
        _map.tsp = imported_tsp
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
