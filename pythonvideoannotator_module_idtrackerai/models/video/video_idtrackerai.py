from .objects.idtrackerai_object import IdtrackeraiObject

class IdTrackerVideo(object):


    def create_idtrackerai_object(self):
        return IdtrackeraiObject(self)

    @property
    def idtrackerai_objects(self):
        for child in self._childrens:
            if isinstance(child, IdtrackeraiObject): yield child