from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import NodePath, CollisionHandlerQueue, CollisionTraverser, CollisionNode, CollisionRay, GeomNode, \
    TextNode

from src.Route import Route
from src.TSP import scale
from src.bus.Bus import Bus
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

        self._route = Route()
        self.calc_route_complete = True
        self.route_complete = False

        self.bus = Bus()
        self.bus.reparentTo(self)

        self.slider_nodes = []

        ## horizontal slider node
        h_slider_node = PositionSlider(range=(-100 - (scale * 5), 100), default=0, position=0, command=self.setX)

        # ## distance (y) slider node
        distance_slider_node = PositionSlider(range=(700, 100), position=1, command=self.setY, default=500)

        ## vertical slider node
        default = 100 - (scale * 100)
        v_slider_node = PositionSlider(range=(default - (scale * 75), default + (scale * 75)), default=default,
                                       position=2, command=self.setZ)
        self.slider_nodes.append(h_slider_node)
        self.slider_nodes.append(v_slider_node)
        self.slider_nodes.append(distance_slider_node)

        self.setPos(0, 0, 0)
        self.cities = []
        if self.tsp is not None:
            self.create_cities(self.tsp.coords)

    def hide_sliders(self):
        for slider in self.slider_nodes:
            slider.hide()

    def get_city(self, city_id):
        return self.cities[int(city_id) - 1]

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
        self.bus.distance_text_path.show()

    def get_current_loaded_file(self):
        if self.tsp is not None:
            return self.tsp.file_name
        return "No TSP loaded"

    def reset(self):
        for city in self.cities:
            city.selected = False
            city.first_city = False
        self.route.clear()
        self.route_complete = False
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

    def complete_route(self):
        self.notify.debug("Route complete")
        self.route_complete = True
        for city in self.cities:
            city.set_circuit_complete()

    def unselect_last_city(self):
        if len(self.route) == 0:
            return
        last_city_id = self.route.pop()
        cur_city_id = self.route[-1]
        self.bus.remove_stop(f"{cur_city_id}-{last_city_id}")
        self.bus.reset_to(self.get_city(cur_city_id).coords)
        self.get_city(last_city_id).selected = False

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
        self.route.append(int(city_id))
        self.bus.add_stop(self.cities[int(city_id) - 1].coords)

        # check if loop
        if is_selected and is_first_city and self.calc_route_complete:
            self.complete_route()
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

    def disable_text(self):
        self.bus.hide_distance_text()
        self.route.display = False

    def enable_text(self):
        self.bus.show_distance_text()
        self.route.display = True

    @property
    def tsp(self):
        return self._TSP

    @tsp.setter
    def tsp(self, value):
        self.notify.debug(f"Setting TSP to {value.name}")
        self.memory_reset()
        self._TSP = value
        self.create_cities(value.coords)

    @property
    def route(self):
        return self._route
    @route.setter
    def route(self, value):
        self._route = Route(value)
