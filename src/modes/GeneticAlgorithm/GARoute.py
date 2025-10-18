import random
import string

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(random.choice(characters) for _ in range(length))


class GARoute(DirectObject):
    def __init__(self, distance, route):
        DirectObject.__init__(self)
        self.notify = directNotify.newCategory("GARoute")
        self.distance = distance
        self.route = route
