from panda3d.core import NodePath, TextNode

from src.UIGlobals import Colors


class City(NodePath):
    def __init__(self, name, coord, rendering=True):
        NodePath.__init__(self, f"city-{name}")
        self.setTag("ClickableCity", str(name))
        self.coords = coord
        self._name = name
        self.rendering = rendering
        if rendering:
            self.model = loader.loadModel("square.bam")
            self.model.setColor((0, 1, 0, 1))
            self.model.reparentTo(self)
            self.model.setScale(2, 2, 2)
            self.model.setPos(coord.x - 50, 0, coord.y - 50)
            self.title_node = TextNode("title")
            self.title_node.setText(f"{name}")
            self.title_node.setAlign(TextNode.ACenter)
            self.title_node_path = self.model.attachNewNode(self.title_node)
            self.title_node_path.setScale(5)
            self.title_node_path.setPos(0, 0, 2)
            self.title_node_path.setBillboardPointEye()
        self.selected = False
        self.first_city = False

    def set_circuit_complete(self):
        if self.rendering:
            self.model.setColor(Colors.CIRCUIT_COMPLETE)

    def reset(self):
        self.selected = False
        self.first_city = False
        if self.rendering:
            self.model.setColor(Colors.UNSELECTED)

    @property
    def coords(self):
        return self._coords

    @coords.setter
    def coords(self, value):
        self._coords = value

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        try:
            if self._selected == value:
                return
        except AttributeError:
            pass
        self._selected = value
        if self.rendering:
            if self.first_city:
                self.model.setColor(Colors.FIRST_SELECTED)
            else:
                self.model.setColor(Colors.SELECTED if value else Colors.UNSELECTED)

    @property
    def first_city(self):
        return getattr(self, "_first_city", False)

    @first_city.setter
    def first_city(self, value):
        self._first_city = value
        if self.rendering:
            if value and self.selected:
                self.model.setColor(Colors.FIRST_SELECTED)
            else:
                self.model.setColor(Colors.SELECTED if self.selected else Colors.UNSELECTED)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
