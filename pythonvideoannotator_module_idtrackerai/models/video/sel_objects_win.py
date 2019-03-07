from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlCombo
from pyforms.controls   import ControlButton

class SelectObjectsWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.video = kwargs['video']

        self.set_margin(10)
        self.setMaximumHeight(200)
        self.setMaximumWidth(200)

        self._object1 = ControlCombo('Object 1')
        self._object2 = ControlCombo('Object 2')
        self._apply  = ControlButton('Switch', default=self.__apply_evt)

        self.formset = [
            ('_object1', '_object2'),
            '_apply'
        ]


    def __apply_evt(self):
        obj1 = self._object1.value
        obj2 = self._object2.value

        if obj1==obj2:
            self.alert("Can't select the same object.", 'Warning')
            return

        obj1.idtrackerai_path.idtrackerai_switch_identity(
            obj2.idtrackerai_path,
            self.video.mainwindow.timeline.value
        )

        self.hide()


    def show(self):
        super().show()

        self._object1.clear()
        self._object2.clear()
        for obj in self.video.objects2D:
            self._object1.add_item(obj.name, obj)
            self._object2.add_item(obj.name, obj)
