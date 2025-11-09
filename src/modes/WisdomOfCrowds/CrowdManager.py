import sys
from time import sleep

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, NodePath, FrameBufferProperties, ButtonThrower, GraphicsWindow, ButtonHandle

bh = ButtonHandle("b")


class CrowdManager(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.notify = directNotify.newCategory("CrowdManager")
        self.ui = []

        # crowd
        self.crowd = []

        # window stuff
        self.crowd_manager_cam = None
        self.crowd_manager_win = None
        self.accept("close-crowd-manager-window", self.destroy)

    def destroy(self):
        self.notify.debug("Destroying Crowd Manager...")
        if self.crowd_manager_cam:
            self.crowd_manager_cam.removeNode()
        if self.crowd_manager_win:
            base.closeWindow(self.crowd_manager_win)
        self.ignoreAll()
        for item in self.ui:
            item.destroy()
        self.ui.clear()
        base.userExit()

    def open(self):
        self.notify.debug("Opening Crowd Manager...")

        # resize
        wp = WindowProperties()
        wp.setSize(1600, 600)
        base.win.requestProperties(wp)

        self.build_ui()

    def build_ui(self):
        frame = DirectFrame(frameColor=(0, 0, 0, 1),
                            frameSize=(0, 2.66, 0, 2),
                            pos=(-1.33, 0, -3),
                            parent=base.aspect2d)
        self.ui.append(frame)

        title = DirectLabel(text="Crowd Manager",
                            scale=0.1, pos=(1.25, 0, 1.9),
                            parent=frame)
        self.ui.append(title)

        crowd_size_label = DirectLabel(text="Crowd Size:",
                                       scale=0.07, pos=(1,0,1.7),
                                       text_pos=(0,0),
                                       text_fg=(1,1,1,1),
                                       frameColor=(1,1,1,1),
                                       parent=frame)
        self.ui.append(crowd_size_label)
        crowd_size = DirectEntry(text="", scale=0.07, initialText="10",
                                 parent=frame, pos=(1.25, 0, 1.7),
                                 text_fg=(1,1,1,1),
                                 frameColor=(1, 1, 1, 1),focus=1)
        self.ui.append(crowd_size)

        make_new_crowd_button = DirectButton(text="Create new Crowd", scale=0.07,
                                             pos=(1.25, 0, 1.5),
                                             command=self.make_new_crowd,
                                             frameColor=(
                                                 (0.8, 0.8, 0.8, 1),  # Normal
                                                 (0.9, 0.9, 0.9, 1),  # Click
                                                 (0.7, 0.7, 0.7, 1),  # Hover
                                                 (0.5, 0.5, 0.5, 1)  # Disabled
                                             ), parent=frame)
        self.ui.append(make_new_crowd_button)

    def make_new_crowd(self):
        self.notify.debug("Making new crowd...")
        self.crowd = []
