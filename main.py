import sys

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectRadioButton import DirectRadioButton
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, VirtualFileSystem, Filename

from src.Map import Map
from src.Mode import BruteForceMode, FirstSearchMode

loadPrcFile("./config.prc")


class TravelingSalesmanProblem(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        ShowBase.set_background_color(self, 0, 0, 0.2, 1)

        # load models
        vfs = VirtualFileSystem.getGlobalPtr()
        vfs.mount(Filename("models.mf"), ".", VirtualFileSystem.MFReadOnly)

        self.notify = directNotify.newCategory("TSPApp")

        # map
        self.map = Map()

        # disable mouse
        self.disableMouse()

        # accept close program
        self.accept("escape", sys.exit)

        # modes
        BFMode = BruteForceMode(self.map)
        FSMode = FirstSearchMode(self.map)
        self._mode = BFMode

        # mode radio buttons
        buttons = [
            DirectRadioButton(text="Brute Force", scale=0.07, pos=(0.9, 0, 0.9), variable=[self.mode], value=[BFMode],
                              command=self.set_mode, extraArgs=[BFMode]),
            DirectRadioButton(text="Breadth/Depth First Search", scale=0.07, pos=(0.7, 0, 0.8), variable=[self.mode],
                              value=[FSMode], command=self.set_mode, extraArgs=[FSMode])
        ]
        for button in buttons:
            button.setOthers(buttons)

        # accept mouse
        self.accept("mouse1-up", self.map.on_mouse_click)

        # start mode
        self.mode.activate(self.map)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if self._mode:
            self.notify.debug(f"Switching mode to {value.type}")
        if self._mode != value:
            self.mode.deactivate()
            self._mode = value
            self.mode.activate(self.map)

    def set_mode(self, mode):
        if self.mode != mode:
            self.mode = mode


app = TravelingSalesmanProblem()
app.run()
