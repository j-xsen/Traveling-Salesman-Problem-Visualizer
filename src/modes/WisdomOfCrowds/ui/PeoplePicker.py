import os

from direct.gui.DirectCheckBox import DirectCheckBox
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.showbase.DirectObject import DirectObject
from panda3d.core import NodePath
from direct.gui import DirectGuiGlobals as DGG


class PeoplePicker(NodePath):
    def __init__(self, _parent):
        NodePath.__init__(self)
        self.notify = directNotify.newCategory("PeoplePicker")

        # base node
        self.frame = DirectFrame(frameColor=(1, 1, 1, 1),
                                 frameSize=(-.25, .4, -.1, .1),
                                    pos=(-.45, 0, .35), borderWidth=(.01, .01),
                                 relief=DGG.RAISED,
                                 parent=_parent,)

        title = DirectLabel(text="Demographics:",
                            scale=0.05,
                            frameColor=(1, 1, 1, 0),
                            pos=(-.075, 0, 0.05),
                            parent=self.frame)

        # create total list of people
        self.all_people = []
        self.gather_all_people()

    def gather_all_people(self):
        dir_path = f"src/modes/WisdomOfCrowds/People"
        if not os.path.exists(dir_path):
                self.notify.warning(f"Directory {dir_path} does not exist.")
                return
        for file in os.listdir(dir_path):
            if not file.startswith("Person"):
                self.all_people.append(file.replace('.py', ''))
        for p in self.all_people:
            self.notify.debug(f"Found person: {p} index: {self.all_people.index(p)}")
            # create button
            person_button = DirectCheckButton(frameColor=(0.8, 0.8, 0.8, 1),
                                          text=p,
                                          scale=0.05,
                                          pos=(.25 - self.all_people.index(p) * 0.15, 0, 0),
                                          relief=DGG.RAISED,
                                          borderWidth=(.005, .005),
                                          parent=self.frame)