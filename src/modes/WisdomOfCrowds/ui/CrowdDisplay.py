from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.showbase.DirectObject import DirectObject


class CrowdDisplay(DirectObject):
    def __init__(self, parent):
        DirectObject.__init__(self)
        self.notify = directNotify.newCategory("CrowdDisplay")
        color = 0.8
        self.node = DirectFrame(frameColor=(color, color, color, 1),
                                frameSize=(-.5, .5, -.2, .7),
                                pos=(-0.6, 0, .7),
                                parent=parent)

        # nav buttons
        left_button = DirectButton(frameColor=(color, color, color, 1),
                                   text="<",
                                   scale=0.15,
                                   pos=(-0.45, 0, -.175),
                                   parent=self.node,
                                   command=self.scroll_left)
        right_button = DirectButton(frameColor=(color, color, color, 1),
                                    text=">",
                                    scale=0.15,
                                    pos=(0.44, 0, -.175),
                                    parent=self.node,
                                    command=self.scroll_right)

    def scroll_left(self):
        self.notify.debug("Scrolling left...")

    def scroll_right(self):
        self.notify.debug("Scrolling right...")

    def update_display(self, crowd):
        self.notify.debug("Updating crowd display...")
        # build 5 x 4 grid
        spacing = 2.0
        for i in range(4):
            for j in range(5):
                index = i * 5 + j
                if index < len(crowd):
                    new_node = DirectButton(parent=self.node,
                                            frameColor=(1, 1, 1, 1),
                                            frameSize=(-0.09, 0.09, -0.09, 0.09),
                                            borderWidth=(0.01, 0.01),
                                            text=f"{index+1}\n{crowd[index].distance:.1f}",
                                            pos=(-0.4 + j * spacing * .1, 0, 0.6 - i * spacing * .1),
                                            text_scale=.06,
                                            command=lambda idx=index: self.show_individual(crowd[idx]),
                                            )
                                            # command=lambda index : print(f"crowd:{crowd}/index:{index}"),)
                else:
                    break

    def show_individual(self, person):
        self.notify.debug(f"Showing individual: {person}")
        base.map.reset()
        for stop in person.route:
            base.map.select_city(stop.get_name()[5:])
