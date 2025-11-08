from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectFrame import DirectFrame
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, NodePath, FrameBufferProperties


class CrowdManager(DirectObject):
    def __init__(self, _show_base):
        DirectObject.__init__(self)
        self.show_base = _show_base
        self.notify = directNotify.newCategory("CrowdManager")
        self.crowd_manager_scene = NodePath('CrowdManagerScene')
        self.crowd_manager_scene.reparentTo(render)
        self.crowd_manager_cam = None
        self.ui = []

    def destroy(self):
        self.notify.debug("Destroying Crowd Manager...")
        self.crowd_manager_scene.removeNode()
        if self.crowd_manager_cam:
            self.crowd_manager_cam.removeNode()
        self.ignoreAll()
        for item in self.ui:
            item.destroy()
        self.ui.clear()

    def open(self):
        self.notify.debug("Opening Crowd Manager...")
        window_properties = WindowProperties()
        window_properties.setSize(800, 600)
        window_properties.setOrigin(1000, 100)
        crowd_manager = ShowBase.openWindow(self.show_base, props=window_properties,
                                            scene=self.crowd_manager_scene, name="CrowdManager",
                                            keepCamera=False,makeCamera=False)
        self.crowd_manager_cam = ShowBase.makeCamera2d(self.show_base, win=crowd_manager,
                                                     cameraName="CMCam",
                                                       displayRegion=(0,1,0,1),
                                                       coords=(-1,1,-3,-1))
        self.build_ui()

    def build_ui(self):
        frame = DirectFrame(frameColor=(1, 1, 1, 1),
                            frameSize=(0, 2,0, 2),
                            pos=(-1,0,-3))
        frame.reparentTo(self.crowd_manager_cam)
        self.ui.append(frame)
