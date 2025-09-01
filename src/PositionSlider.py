from enum import Enum

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectSlider import DirectSlider
from panda3d.core import NodePath, TextNode


class PositionSlider(NodePath):
    def __init__(self, position, command=lambda *_: None, range=(-500, 500), default=0):
        NodePath.__init__(self, f"Slider{position}")

        self.notify = directNotify.newCategory(f"PositionSlider")
        self.notify.debug(f"range {range}, default {default}")

        self.slider = None
        self._value = 0

        self.range = range

        self.setPos(-.95, 0, -.4-(float(position) * -0.3))
        self.reparentTo(aspect2d)

        dir_str = "X"
        match position:
            case 0:
                dir_str = "X (Left/Right)"
            case 1:
                dir_str = "Z (Back/Forward)"
            case 2:
                dir_str = "Y (Up/Down)"
            case _:
                self.notify.warning(f"Unknown position {position}, defaulting to X")

        # text
        slider_text = TextNode(f"Slider{position}Text")
        slider_text.setText(f"{dir_str}")
        slider_text.setAlign(TextNode.ACenter)
        slider_node_path = self.attachNewNode(slider_text)
        slider_node_path.setScale(0.07)
        slider_node_path.setPos(0, 0, 0.1)

        # slider
        slider_thumb_scale = 0.15
        self.slider = DirectSlider(range=self.range, value=default, scale=0.3,
                                     command=self.update_value,
                                   thumb_frameSize=(-slider_thumb_scale,
                                                    slider_thumb_scale,
                                                    -slider_thumb_scale,
                                                    slider_thumb_scale))
        self.slider.reparentTo(self)

        # command
        self.command = command

    def update_value(self):
        if not self.slider:
            return
        self.value = self.slider['value']
        self.command(self.value)

    @property
    def value(self):
        if not self.slider:
            return None
        return self.slider['value']
    @value.setter
    def value(self, val):
        if not self.slider:
            self.notify.warning("Slider not initialized")
            return
        self._value = val
