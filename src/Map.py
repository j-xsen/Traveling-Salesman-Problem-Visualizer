import os
import time
from itertools import permutations

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectSlider import DirectSlider
from panda3d.core import NodePath, CollisionHandlerQueue, CollisionTraverser, CollisionNode, CollisionRay, GeomNode, \
    TextNode

from src.Bus import Bus
from src.City import City

class Map(NodePath):
    def __init__(self, TSP=None):
        NodePath.__init__(self, "map")
        self.reparentTo(render)
        self._TSP = TSP
        self.notify = directNotify.newCategory("Map")

        self.rendering = True

        # add collision traverser and handler
        self.c_trav = CollisionTraverser()
        self.c_handler = CollisionHandlerQueue()

        self.route_text = TextNode("route")
        self.route_text.setText("Route: ")
        self.route_text.setAlign(TextNode.ALeft)
        self.route_text_path = aspect2d.attachNewNode(self.route_text)
        self.route_text_path.setScale(0.07)
        self.route_text_path.setPos(-1.3, 0, 0.8)
        self.route = []
        self.route_complete = False

        self.bus = Bus()
        self.bus.reparentTo(self)

        ## distance slider node
        distance_slider_node = NodePath("DistanceSlider")
        distance_slider_node.setPos(-.95, 0, -.4)
        distance_slider_node.reparentTo(aspect2d)

        # text
        distance_slider_text = TextNode("distance_slider")
        distance_slider_text.setText("Zoom")
        distance_slider_text.setAlign(TextNode.ACenter)
        distance_slider_node_path = distance_slider_node.attachNewNode(distance_slider_text)
        distance_slider_node_path.setScale(0.07)
        distance_slider_node_path.setPos(0, 0, 0.1)

        # slider
        self.slider = DirectSlider(range=(1000, 0), value=500, scale=0.3,
                                   command=lambda: self.setY(self.slider['value']),)
        self.slider.reparentTo(distance_slider_node)


        self.setPos(0, self.slider['value'], 0)
        self.cities = []
        if self.TSP is not None:
            self.create_cities(self.TSP.coords, self.rendering)

    def disable_rendering(self):
        self.rendering = False
        self.bus.making_stops = False
        self.clear_cities()
        self.recreate_cities()

    def enable_rendering(self):
        self.rendering = True
        self.bus.making_stops = True
        self.slider.show()
        for city in self.cities:
            city.show()
        self.route_text_path.show()
        self.bus.distance_text_path.show()

    def get_current_loaded_file(self):
        if self.TSP is not None:
            return self.TSP.file_name
        return ""

    def reset(self):
        for city in self.cities:
            city.selected = False
            city.first_city = False
        self.route = []
        self.route_complete = False
        self.route_text.setText("Route: ")
        self.bus.reset()

    def memory_reset(self):
        self.reset()
        self.clear_cities()

    def clear_cities(self):
        for city in self.cities:
            city.removeNode()
        self.cities = []

    def create_city(self, name, coords):
        new_city = City(name, coords, self.rendering)
        new_city.reparentTo(self)
        self.cities.append(new_city)

    def create_cities(self, coords_list):
        city_id = 1
        for coords in coords_list:
            self.create_city(city_id, coords)
            city_id += 1

    def recreate_cities(self):
        if self.TSP is not None:
            self.create_cities(self.TSP.coords)

    def select_city(self, city_id):
        is_selected = self.cities[int(city_id) - 1].selected
        is_first_city = (len(self.route) == 0) or self.cities[int(city_id) - 1].first_city
        self.notify.debug(f"Selecting city {city_id}")
        # check if city already selected
        if is_selected:
            # check if not first city
            if not is_first_city:
                self.notify.warning(f"City {city_id} already selected")
                return
        self.route.append(city_id)
        self.route_text.setText(f"Route: {', '.join(self.route)}")
        self.bus.add_stop(self.cities[int(city_id) - 1].coords)

        # check if loop
        if is_selected and is_first_city:
            self.notify.debug("Route complete")
            self.route_complete = True
            for city in self.cities:
                city.set_circuit_complete()
            return

        self.cities[int(city_id) - 1].selected = True
        self.cities[int(city_id) - 1].first_city = is_first_city

    def on_mouse_click(self):
        # https://docs.panda3d.org/1.10/python/programming/collision-detection/clicking-on-3d-objects
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            pickerNode = CollisionNode('mouseRay')
            pickerNP = base.camera.attachNewNode(pickerNode)
            pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
            pickerRay = CollisionRay()
            pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            pickerNode.addSolid(pickerRay)
            self.c_trav.addCollider(pickerNP, self.c_handler)
            self.c_trav.traverse(base.render)
            if self.c_handler.getNumEntries() > 0:
                self.c_handler.sortEntries()
                pickedObj = self.c_handler.getEntry(0).getIntoNodePath()
                pickedObj = pickedObj.findNetTag("ClickableCity")
                if not pickedObj.isEmpty():
                    # check if reset needed
                    if self.route_complete:
                        self.reset()
                    self.select_city(str(pickedObj).split("-")[1])
            pickerNP.removeNode()

    @property
    def TSP(self):
        return self._TSP
    @TSP.setter
    def TSP(self, value):
        self.notify.debug(f"Setting TSP to {value.name}")
        self.memory_reset()
        self._TSP = value
        self.create_cities(value.coords)
