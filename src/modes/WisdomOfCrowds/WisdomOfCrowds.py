from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectButton import DirectButton
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, NodePath

from src.modes.Mode import Mode, ProblemType
from src.modes.WisdomOfCrowds.CrowdManager import CrowdManager


class WisdomOfCrowds(Mode):
    def __init__(self, _show_base):
        super().__init__(ProblemType.WISDOM_OF_CROWDS, 'Random11.tsp', _show_base.map)
        self.notify = directNotify.newCategory("WisdomOfCrowds")
        self.crowd_manager = CrowdManager(_show_base)

    def build_ui(self):
        self.notify.debug("Building Wisdom of Crowds UI.")
        open_crowd_window_button = DirectButton(text="Open Crowd Manager", scale=0.07,
                                    pos=(.85, 0, -0.8),
                                    command=self.open_crowd_manager,
                                                frameColor=(
                                                    (0.8, 0.8, 0.8, 1),  # Normal
                                                    (0.9, 0.9, 0.9, 1),  # Click
                                                    (0.7, 0.7, 0.7, 1),  # Hover
                                                    (0.5, 0.5, 0.5, 1)  # Disabled
                                                ),)
        self.ui.append(open_crowd_window_button)

    def open_crowd_manager(self):
        self.crowd_manager.open()
        self.ui[0]['state'] = "disabled"

    def build_crowd(self):
        self.notify.debug("Building crowd...")
