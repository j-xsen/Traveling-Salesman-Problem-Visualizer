from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import NodePath, CollisionHandlerQueue, CollisionTraverser, CollisionNode, CollisionRay, GeomNode, \
    TextNode

from src.TSP import scale
from src.Bus import Bus
from src.City import City
from src.PositionSlider import PositionSlider

# type: ignore
# Panda3D globals
render: 'NodePath'  # type: ignore
aspect2d: 'NodePath'  # type: ignore
base: 'ShowBase'  # type: ignore


class Map(NodePath):
    def __init__(self, tsp=None):
        NodePath.__init__(self, "map")
        self.reparentTo(render)
        self._TSP = tsp
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

        ## horizontal slider node
        h_slider_node = PositionSlider(range=(-100 - (scale * 5), 100), default=0, position=0, command=self.setX)

        # ## distance (y) slider node
        distance_slider_node = PositionSlider(range=(700, 100), position=1, command=self.setY, default=500)

        ## vertical slider node
        default = (200 - (scale * 100))
        v_slider_node = PositionSlider(range=(default - (scale * 75), default + (scale * 75)), default=default,
                                       position=2, command=self.setZ)

        self.setPos(0, 0, 0)
        self.cities = []
        if self.tsp is not None:
            self.create_cities(self.tsp.coords)

    def setX(self, x):
        self.setPos(x, self.getY(), self.getZ())

    def disable_rendering(self):
        self.rendering = False
        self.bus.making_stops = False
        self.clear_cities()
        self.recreate_cities()

    def enable_rendering(self):
        self.rendering = True
        self.bus.making_stops = True
        for city in self.cities:
            city.show()
        self.route_text_path.show()
        self.bus.distance_text_path.show()

    def get_current_loaded_file(self):
        if self.tsp is not None:
            return self.tsp.file_name
        return "No TSP loaded"

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
        if self.tsp is not None:
            self.create_cities(self.tsp.coords)

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
        self.bus.add_stop(self.cities[int(city_id) - 1].coords)
        self.route_text.setText(f"Route: {', '.join(str(x) for x in self.route)}")

        # check if loop
        if is_selected and is_first_city:
            self.notify.debug("Route complete")
            self.route_complete = True
            for city in self.cities:
                city.set_circuit_complete()
            return

        self.cities[int(city_id) - 1].selected = True
        self.cities[int(city_id) - 1].first_city = is_first_city

    def on_mouse_click(self, tag="ClickableCity"):
        # https://docs.panda3d.org/1.10/python/programming/collision-detection/clicking-on-3d-objects
        if base.mouseWatcherNode.hasMouse():
            m_pos = base.mouseWatcherNode.getMouse()
            picker_node = CollisionNode('mouseRay')
            picker_np = base.camera.attachNewNode(picker_node)
            picker_node.setFromCollideMask(GeomNode.getDefaultCollideMask())
            picker_ray = CollisionRay()
            picker_ray.setFromLens(base.camNode, m_pos.getX(), m_pos.getY())
            picker_node.addSolid(picker_ray)
            self.c_trav.addCollider(picker_np, self.c_handler)
            self.c_trav.traverse(base.render)
            if self.c_handler.getNumEntries() > 0:
                self.c_handler.sortEntries()
                picked_obj = self.c_handler.getEntry(0).getIntoNodePath()
                picked_obj = picked_obj.findNetTag(tag)
                picker_np.removeNode()
                return picked_obj if not picked_obj.isEmpty() else None
            picker_np.removeNode()
        return None

    @property
    def tsp(self):
        return self._TSP

    @tsp.setter
    def tsp(self, value):
        self.notify.debug(f"Setting TSP to {value.name}")
        self.memory_reset()
        self._TSP = value
        self.create_cities(value.coords)
