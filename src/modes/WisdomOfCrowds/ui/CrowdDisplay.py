from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.showbase.DirectObject import DirectObject
from direct.gui import DirectGuiGlobals as DGG


color = 0.8


class CrowdDisplay(DirectObject):
    def __init__(self, parent, elite_percent=0.2):
        DirectObject.__init__(self)
        self.notify = directNotify.newCategory("CrowdDisplay")
        self._page_number = 0
        self.crowd_per_page = 20
        self.crowd = []
        self.elite_percent = elite_percent
        self.left_button = None
        self.right_button = None
        self.node = DirectFrame(frameColor=(color, color, color, 1),
                                frameSize=(-.5, .5, -.2, .7),
                                pos=(-0.6, 0, .7),
                                parent=parent)

        # nav buttons
        self.create_nav_buttons(self.node)

    @property
    def page_number(self):
        return self._page_number
    @page_number.setter
    def page_number(self, value):
        self.notify.debug(f"Setting page number to {value}")
        self._page_number = value
        self.refresh_node()
        self.update_display()

    def edit_crowd(self, new_crowd):
        self.notify.debug("Editing crowd...")
        self.crowd = new_crowd
        self.refresh_node()
        self.update_display()

    def create_nav_buttons(self, parent):
        # nav buttons
        left_state = DGG.NORMAL if self.page_number > 0 else DGG.DISABLED
        right_state = DGG.NORMAL if self.page_number < len(self.crowd) / self.crowd_per_page - 1 else DGG.DISABLED
        self.left_button = DirectButton(frameColor=(
                                   (0.8, 0.8, 0.8, 1),  # Normal
                                   (0.9, 0.9, 0.9, 1),  # Click
                                   (0.7, 0.7, 0.7, 1),  # Hover
                                   (0.5, 0.5, 0.5, 1)  # Disabled
                               ),
                                   text="<",
                                   scale=0.15,
                                   pos=(-0.45, 0, -.175),
                                   parent=parent,
                                        state=left_state,
                                   command=self.scroll_left)
        self.right_button = DirectButton(frameColor=(
                                   (0.8, 0.8, 0.8, 1),  # Normal
                                   (0.9, 0.9, 0.9, 1),  # Click
                                   (0.7, 0.7, 0.7, 1),  # Hover
                                   (0.5, 0.5, 0.5, 1)  # Disabled
                               ),
                                    text=">",
                                    scale=0.15,
                                    pos=(0.44, 0, -.175),
                                    parent=parent,
                                         state=right_state,
                                    command=self.scroll_right)

    def refresh_node(self):
        parent = self.node.getParent()
        self.node = DirectFrame(frameColor=(color, color, color, 1),
                                frameSize=(-.5, .5, -.2, .7),
                                pos=(-0.6, 0, .7),
                                parent=parent)
        # nav buttons
        self.create_nav_buttons(self.node)

    def scroll_left(self):
        if not self.crowd:
            self.notify.debug("No crowd to scroll.")
            return
        if self.page_number == 0:
            self.notify.debug("Already at first page, cannot scroll left.")
            return
        self.notify.debug("Scrolling left...")
        self.page_number -= 1

    def scroll_right(self):
        if not self.crowd:
            self.notify.debug("No crowd to scroll.")
            return
        if self.page_number >= len(self.crowd) / self.crowd_per_page - 1:
            self.notify.debug("Already at last page, cannot scroll right.")
            return
        self.notify.debug("Scrolling right...")
        self.page_number += 1

    def update_display(self):
        self.notify.debug("Updating crowd display...")
        sorted_crowd = sorted(self.crowd, key=lambda person: person.distance)
        tags = []
        for c in sorted_crowd[:max(1, int(len(self.crowd) * self.elite_percent))]:
            tags.append(str(c.tag))

        # colors
        chosen_color = (0,1,0,1)
        normal_color = (1,1,1,1)

        # build 5 x 4 grid
        spacing = 2.0
        offset = self.page_number * self.crowd_per_page
        for i in range(4):
            for j in range(5):
                index = i * 5 + j + offset
                if index < len(self.crowd):
                    cur_color = normal_color
                    if str(self.crowd[index].tag) in tags:
                        cur_color = chosen_color
                    new_node = DirectButton(parent=self.node,
                                            frameColor=cur_color,
                                            frameSize=(-0.09, 0.09, -0.09, 0.09),
                                            borderWidth=(0.01, 0.01),
                                            text=f"{index+1}\n{self.crowd[index].name[:4]}\n{self.crowd[index].distance:.1f}",
                                            pos=(-0.4 + j * spacing * .1, 0, 0.6 - i * spacing * .1),
                                            text_scale=.06,
                                            text_pos=(0, 0.05),
                                            command=lambda idx=index: self.show_individual(self.crowd[idx]),
                                            )
                else:
                    break

    def show_individual(self, person):
        self.notify.debug(f"Showing individual: {person}")
        base.map.reset()
        first = None
        for stop in person.route:
            if not first:
                first = stop
            base.map.select_city(stop.get_name()[5:])
        base.map.select_city(first.get_name()[5:])

