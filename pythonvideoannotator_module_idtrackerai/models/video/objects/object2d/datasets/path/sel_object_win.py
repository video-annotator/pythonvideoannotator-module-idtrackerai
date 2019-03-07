from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlCombo
from pyforms.controls   import ControlButton

class SelectObjectWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path = kwargs.get('path')

        self.set_margin(10)
        self.setMaximumHeight(100)
        self.setMaximumWidth(200)

        self._object = ControlCombo('Object')
        self._apply  = ControlButton('Switch', default=self.__apply_evt)

        self.formset = [
            '_object',
            '_apply'
        ]


    def __apply_evt(self):
        obj = self._object.value

        self.path.idtrackerai_switch_identity(
            obj.idtrackerai_path,
            self.path.mainwindow.timeline.value
        )

        self.hide()


    def show(self):
        super().show()

        self._object.clear()
        for obj in self.path.object2d.video.objects2D:
            self._object.add_item(obj.name, obj)
