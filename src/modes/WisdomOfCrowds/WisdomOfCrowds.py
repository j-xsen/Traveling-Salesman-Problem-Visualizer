from direct.directnotify.DirectNotifyGlobal import directNotify

from src.modes.Mode import Mode, ProblemType
from src.modes.WisdomOfCrowds.ui.CrowdManager import CrowdManager


class WisdomOfCrowds(Mode):
    def __init__(self, _show_base):
        super().__init__(ProblemType.WISDOM_OF_CROWDS, 'Random11.tsp', _show_base.map, name="WisdomOfCrowds")
        self.crowd_manager = CrowdManager()

    def load_problem(self, _map, file, src=""):
        hold=False
        if self.last_loaded:
            hold = True
        super().load_problem(_map,file,src)
        if hold:
            messenger.send("WOCProblemChanged")

    def build_ui(self):
        self.notify.debug("Building Wisdom of Crowds UI.")
        self.open_crowd_manager()

    def open_crowd_manager(self):
        self.crowd_manager.open()

    def on_mouse_click(self):
        pass
