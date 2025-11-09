import sys

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectRadioButton import DirectRadioButton
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, VirtualFileSystem, Filename

from src.Map import Map
from src.modes.BruteForceMode import BruteForceMode
from src.modes.ClosestEdgeInsertionMode import ClosestEdgeInsertionMode
from src.modes.FirstSearchMode import FirstSearchMode
from src.modes.GeneticAlgorithm.GeneticAlgorithm import GeneticAlgorithm
from src.modes.WisdomOfCrowds.WisdomOfCrowds import WisdomOfCrowds

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
        self.accept("escape", self.userExit)

        # modes
        BFMode = BruteForceMode(self.map)
        FSMode = FirstSearchMode(self.map)
        CEMode = ClosestEdgeInsertionMode(self.map)
        GAMode = GeneticAlgorithm(self.map)
        WOCMode = WisdomOfCrowds(self)
        self._mode = WOCMode

        # modes radio buttons
        radio_button_node = base.a2dTopRight.attachNewNode("radio_buttons")
        radio_button_node.setPos(-.5,0,0)
        radio_button_node.setScale(0.9)
        buttons = [
            DirectRadioButton(text="Brute Force", scale=0.07, pos=(0, 0, -.1), variable=[self.mode], value=[BFMode],
                              command=self.set_mode, extraArgs=[BFMode],
                              parent=radio_button_node),
            DirectRadioButton(text="Breadth/Depth First Search", scale=0.07, pos=(0, 0, -.2), variable=[self.mode],
                              value=[FSMode], command=self.set_mode, extraArgs=[FSMode],
                              parent=radio_button_node),
            DirectRadioButton(text="Closest Edge Insertion", scale=0.07, pos=(0, 0, -.3), variable=[self.mode],
                              value=[CEMode], command=self.set_mode, extraArgs=[CEMode],
                              parent=radio_button_node),
            DirectRadioButton(text="Genetic Algorithm", scale=0.07, pos=(0, 0, -.4),
                            variable=[self.mode],
                            value=[GAMode], command=self.set_mode, extraArgs=[GAMode],
                              parent=radio_button_node),
            DirectRadioButton(text="Wisdom of Crowds", scale=0.07, pos=(0, 0, -.5), variable=[self.mode],
                              value=[WOCMode], command=self.set_mode, extraArgs=[WOCMode],
                              parent=radio_button_node),
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
