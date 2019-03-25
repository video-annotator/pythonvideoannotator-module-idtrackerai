from .sel_objects_win import SelectObjectsWindow
from pyforms.controls import ControlButton

class IdTrackerVideo(object):

    def __init__(self, project=None):
        super().__init__(project)

        self.sel_object_win = SelectObjectsWindow(
            title='Switch identification with',
            video=self,
            parent_win=self.mainwindow
        )

        self._switchid_btn = ControlButton('Switch identification', default=self.__switchid_btn_evt)

        formset = [
            'h3:IdTracker.ai',
            '_switchid_btn'
        ]

        self.formset += formset



    def init_form(self):
        super().init_form()

    def __switchid_btn_evt(self):
        self.sel_object_win.show()
