import sys
from time import sleep

import numpy
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, NodePath, FrameBufferProperties, ButtonThrower, GraphicsWindow, ButtonHandle
from panda3d_tools import text_stats
from scipy.special import betaincinv

from src.modes.WisdomOfCrowds.ui.CrowdDisplay import CrowdDisplay
from src.modes.WisdomOfCrowds.ui.PeoplePicker import PeoplePicker

bh = ButtonHandle("b")


class CrowdManager(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.notify = directNotify.newCategory("CrowdManager")
        self.ui = []

        # crowd
        self.crowd = []
        self.crowd_size = 10

        self.people_picker = None
        self.crowd_display = None
        self.accept("close-crowd-manager-window", self.destroy)

    def destroy(self):
        self.notify.debug("Destroying Crowd Manager...")
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

    def adjust_crowd_size(self, text):
        try:
            size = int(text)
            if size < 1:
                self.notify.warning("Crowd size must be at least 1.")
                self.ui[2].enterText(str(self.crowd_size))
            else:
                self.crowd_size = size
                return
        except ValueError:
            self.notify.warning("Invalid crowd size entered.")
        self.ui[2].enterText(str(self.crowd_size))

    def build_ui(self):
        frame = DirectFrame(frameColor=(0, 0, 0, 1),
                            frameSize=(0, 1, 0, 1),
                            pos=(0, 0, 0),
                            parent=base.a2dBottomRight)
        self.ui.append(frame)

        crowd_np = frame.attachNewNode("crowd_np")
        crowd_size_label = DirectLabel(text="Crowd Size:",
                                       scale=0.07, pos=(-.5,0,.155),
                                       text_pos=(0,0),
                                       text_fg=(1,1,1,1),
                                       frameColor=(0,0,0,0),
                                       parent=crowd_np)
        self.ui.append(crowd_size_label)
        crowd_size = DirectEntry(text="", scale=0.07, initialText=str(self.crowd_size),
                                 parent=crowd_np, pos=(-.3, 0, .14),
                                 text_pos=(0.15,0.2),
                                 text_fg=(1,1,1,1), frameSize=(0, 2, 0, 1),
                                 frameColor=(1, 1, 1, 0.5), width=2.5,
                                 command=self.adjust_crowd_size)
        self.ui.append(crowd_size)

        make_new_crowd_button = DirectButton(text="Create new Crowd", scale=0.07,
                                             pos=(-.35, 0, .05),
                                             command=self.generate_crowd,
                                             frameColor=(
                                                 (0.8, 0.8, 0.8, 1),  # Normal
                                                 (0.9, 0.9, 0.9, 1),  # Click
                                                 (0.7, 0.7, 0.7, 1),  # Hover
                                                 (0.5, 0.5, 0.5, 1)  # Disabled
                                             ), parent=frame)
        self.ui.append(make_new_crowd_button)
        self.people_picker = PeoplePicker(frame)
        self.crowd_display = CrowdDisplay(self.crowd, frame)
        self.ui.append(self.crowd_display)
        self.ui.append(self.people_picker)

    def generate_crowd(self):
        self.notify.debug("Making new crowd...")
        self.crowd = []
        for _ in range(self.crowd_size):
            person = self.people_picker.pick_a_person()
            self.crowd.append(person)
        self.crowd_display.update_display(self.crowd)
        self.create_agreement_matrix()

    def create_agreement_matrix(self):
        self.notify.debug("Creating agreement matrix...")
        size = len(self.crowd)
        route_size = len(base.map.cities)
        self.notify.debug(f"Crowd size: {size}, Route size: {route_size}")
        connections = 0
        matrix = numpy.array([[0 for _ in range(route_size)] for _ in range(route_size)], dtype=float)
        for i in range(size):
            route = self.crowd[i].route
            for j in range(size):
                connection_start = int(route[j].get_name()[5:])-1
                if j == len(route) - 1:
                    connection_end = int(route[0].get_name()[5:])-1
                else:
                    connection_end = int(route[j+1].get_name()[5:])-1
                connections+=1
                # matrix[min(connection_start, connection_end)][max(connection_start, connection_end)] += 1
                matrix[connection_start][connection_end] += 1
                matrix[connection_end][connection_start] += 1
        # agreement
        agreement = matrix / size
        agreement = numpy.clip(agreement, 0.0, 1.0)
        self.notify.debug("Agreement matrix created:")
        for row in matrix:
            self.notify.debug(row)
        self.notify.debug(f"Agreement value: {agreement}")

        # power transform
        b1 = b2 = 3
        eps = 1e-12
        A_clip = numpy.clip(agreement, eps, 1.0-eps)
        C_beta = 1.0 - betaincinv(b1, b2, A_clip)
        self.notify.debug(f"Beta transformed agreement value: {C_beta}")
        return matrix
