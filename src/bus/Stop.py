import math

from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import GeomNode, CollisionNode, CollisionBox, NodePath

from src.UIGlobals import Colors
from src.bus.distance import distance


class Stop(NodePath):
    def __init__(self, from_city, to_city, name="", selected=False):
        NodePath.__init__(self, name)
        self.setTag("Stop", f"{name}")
        self.notify = directNotify.newCategory("Stop")
        self.notify.debug(f"Creating stop from {from_city} to {to_city}")
        self.from_city = from_city
        self.to_city = to_city

        self._selected = selected
        self._route_complete = False

        # # ARROW BODY
        self.model = loader.loadModel("arrow_body.bam")
        self.model.setColor((1, 1, 1, 1))

        # compute roll
        dx = to_city.x - from_city.x
        dz = to_city.y - from_city.y
        theta = math.degrees(math.atan2(dz, dx))
        roll = (90 - theta) % 360

        # position and scale
        self.model.setHpr(0, 0, roll)
        self.model.setPos(from_city.x - 50 + (to_city.x - from_city.x) / 2,
                          0,
                          from_city.y - 50 + (to_city.y - from_city.y) / 2)
        self.model.setScale(2, 5, 4*distance(from_city, to_city)/10)

        # # ARROW HEAD
        head_x = from_city.x - 50 + (to_city.x - from_city.x) * 0.9
        head_z = from_city.y - 50 + (to_city.y - from_city.y) * 0.9
        arrow_head = loader.loadModel("arrow_head.bam")
        arrow_head.setColor((1, 1, 1, 1))
        arrow_head.setHpr(0, 0, roll)
        arrow_head.setPos(head_x, 0, head_z)
        arrow_head.setScale(3, 3, 3)
        arrow_head.reparentTo(self)

        # collider
        collision_rectangle = CollisionBox(-1, 1)  # Back to the original simple box
        c_node = CollisionNode(name)
        c_node.addSolid(collision_rectangle)
        c_node.setIntoCollideMask(GeomNode.getDefaultCollideMask())
        collider = self.model.attachNewNode(c_node)

        # reparent
        self.model.reparentTo(self)

    @property
    def selected(self):
        return self._selected
    @selected.setter
    def selected(self, value):
        self._selected = value
        for children in self.getChildren():
            children.setColor(Colors.SELECTED if value else Colors.WHITE)

    @property
    def route_complete(self):
        return self._route_complete
    @route_complete.setter
    def route_complete(self, value):
        self._route_complete = value
        if value:
            for children in self.getChildren():
                children.setColor(Colors.CIRCUIT_COMPLETE)
