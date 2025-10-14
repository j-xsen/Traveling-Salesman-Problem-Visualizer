import sys

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectRadioButton import DirectRadioButton
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, VirtualFileSystem, Filename

from src.Map import Map
from src.modes.BruteForceMode import BruteForceMode
from src.modes.ClosestEdgeInsertionMode import ClosestEdgeInsertionMode
from src.modes.FirstSearchMode import FirstSearchMode
from src.modes.GeneticAlgorithm import GeneticAlgorithm

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
        CEMode = ClosestEdgeInsertionMode(self.map)
        GAMode = GeneticAlgorithm(self.map)
        self._mode = GAMode

        # modes radio buttons
        buttons = [
            DirectRadioButton(text="Brute Force", scale=0.07, pos=(1, 0, 0.9), variable=[self.mode], value=[BFMode],
                              command=self.set_mode, extraArgs=[BFMode]),
            DirectRadioButton(text="Breadth/Depth First Search", scale=0.07, pos=(0.8, 0, 0.75), variable=[self.mode],
                              value=[FSMode], command=self.set_mode, extraArgs=[FSMode]),
            DirectRadioButton(text="Closest Edge Insertion", scale=0.07, pos=(0.9, 0, 0.6), variable=[self.mode],
                              value=[CEMode], command=self.set_mode, extraArgs=[CEMode]),
            DirectRadioButton(text="Genetic Algorithm", scale=0.07, pos=(0.9, 0, 0.45),
                            variable=[self.mode],
                            value=[GAMode], command=self.set_mode, extraArgs=[GAMode])
        ]
        for button in buttons:
            button.setOthers(buttons)

        # start modes
        self.mode.activate(self.map)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if self._mode:
            self.notify.debug(f"Switching mode to {value.type}")
        if self._mode != value:
            self.notify.debug(f"Changing mode from {self._mode.type} to {value.type}")
            self.mode.deactivate()
            self._mode = value
            self.mode.activate(self.map)

    def set_mode(self, mode):
        if self.mode != mode:
            self.mode = mode


app = TravelingSalesmanProblem()
app.run()
