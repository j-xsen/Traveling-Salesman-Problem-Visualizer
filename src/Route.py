from panda3d.core import TextNode


class Route(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.route_text = TextNode("route")
        self.route_text.setText("Route: ")
        self.route_text.setAlign(TextNode.ALeft)
        self.route_text_path = base.a2dTopLeft.attachNewNode(self.route_text)
        self.route_text_path.setScale(0.07)
        self.route_text_path.setPos(.05, 0, -.2)

    def update_route_text(self):
        if len(self) == 0:
            self.route_text.setText("Route: ")
        else:
            self.route_text.setText(f"Route: {', '.join(map(str, self))}")

    def _trigger(self):
        self.update_route_text()

    def append(self, item):
        super().append(item)
        self._trigger()

    def extend(self, iterable):
        super().extend(iterable)
        self._trigger()

    def insert(self, index, item):
        super().insert(index, item)
        self._trigger()

    def remove(self, item):
        super().remove(item)
        self._trigger()

    def clear(self):
        super().clear()
        self._trigger()

    def pop(self, index=-1):
        value = super().pop(index)
        self._trigger()
        return value