from pyforms.controls import ControlButton
from .sel_object_win import SelectObjectWindow
from AnyQt import QtCore
import numpy as np, copy


class IdTrackerPath(object):

    def __init__(self, obj=None):
        super().__init__(obj)

        self.sel_object_win = SelectObjectWindow(
            title='Switch identification with',
            path=self,
            parent_win=obj.mainwindow
        )




    def __switchid_btn_evt(self):
        self.sel_object_win.show()

    def idtrackerai_switch_identity(self, other_path, frame_index):

        path1 = self
        path2 = other_path

        fragment_id1 = path1.fragments[frame_index]
        fragment_id2 = path2.fragments[frame_index]

        begin1 = frame_index
        for i in range(frame_index - 1, -1, -1):
            if path1.fragments[i] == fragment_id1:
                begin1 = i
            else:
                break

        end1 = frame_index
        for i in range(frame_index + 1, len(path1)):
            if path1.fragments[i] == fragment_id1:
                end1 = i
            else:
                break

        begin2 = frame_index
        for i in range(frame_index - 1, -1, -1):
            if path2.fragments[i] == fragment_id2:
                begin2 = i
            else:
                break

        end2 = frame_index
        for i in range(frame_index + 1, len(path2)):
            if path2.fragments[i] == fragment_id2:
                end2 = i
            else:
                break

        cnt1 = path1.contours
        cnt2 = path2.contours

        tmp        = copy.deepcopy(path1.data)
        cnt_tmp    = cnt1.data.copy()
        angles_tmp = copy.deepcopy(cnt1.angles)

        cnt1.data[begin1:end1+1] = cnt2.data[begin1:end1+1].copy()

        for i in range(begin1, end1 + 1):
            path1[i] = path2[i]
            path1.switch_identity[i] = 1
            cnt1.set_angle(i, cnt2.angles[i])

        cnt2.data[begin2:end2+1] = cnt_tmp[begin2:end2+1]
        for i in range(begin2, end2+1):
            path2[i] = tmp[i]
            path2.switch_identity[i] = 1
            cnt2.set_angle(i, angles_tmp[i])

       
    def on_click(self, event, x, y):
        if event.button== 1:
            frame_index = self.mainwindow.timeline.value
            if self._mark_pto_btn.checked:
                self.modifications[frame_index] = 1
        super().on_click(event, x, y)



    def load(self, data, dataset_path=None):

        if 'crossings-value' in data:
            self._crossings_val_name = data['crossings-value']

        if 'fragments-value' in data:
            self._fragments_val_name = data['fragments-value']

        if 'contours-value' in data:
            self._contours_val_name = data['contours-value']

        if 'modifications-value' in data:
            self._modifications_val_name = data['modifications-value']

        if 'switch-identity-value' in data:
            self._switch_identity_val_name = data['switch-identity-value']

        return super().load(data, dataset_path)




    def post_load(self):

        modifications = self.object2d.find_dataset('modifications')
        crossings = self.object2d.find_dataset('crossings')
        fragments = self.object2d.find_dataset('path fragments')
        contours  = self.object2d.find_dataset('contours')
        switch    = self.object2d.find_dataset('switch identities')

        if modifications is not None:
            self.modifications = modifications

        if fragments is not None:
            self.fragments = fragments

        if contours is not None:
            self.contours = contours

        if switch is not None:
            self.switch_identity = switch

        if crossings is not None:
            self.crossings = crossings

        self.object2d.idtrackerai_path = self
