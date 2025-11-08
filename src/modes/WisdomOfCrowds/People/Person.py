from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject


class Person(DirectObject):
    def __init__(self, _cities):
        DirectObject.__init__(self)
        self.notify = directNotify.newCategory("Person")
        self.cities = _cities

    def generate_route(self):
        pass
