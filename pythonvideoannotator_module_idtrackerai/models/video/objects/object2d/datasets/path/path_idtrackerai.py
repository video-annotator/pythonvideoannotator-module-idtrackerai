from pyforms.controls import ControlButton
from .sel_object_win import SelectObjectWindow
import numpy as np

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

        tmp        = list(path1.data)
        cnt_tmp    = np.array(cnt1.data)
        angles_tmp = list(cnt1.angles)

        for i in range(begin1, end1 + 1):
            cnt1.set_contour(i, cnt2[i], cnt2.get_angle(i))
        path1.switch_identity(path2, begin=begin1, end=end1)

        for i in range(begin2, end2 + 1):
            cnt2.set_contour(i, cnt_tmp[i] if len(cnt_tmp)<i else None, angles_tmp[i] if len(angles_tmp)<i else None)
        path2.switch_identity(tmp, begin=begin1, end=end1)


    def on_click(self, event, x, y):
        if event.button== 1:
            frame_index = self.mainwindow.timeline.value
            if self._mark_pto_btn.checked:
                self.modifications[frame_index] = 1
        super().on_click(event, x, y)

    def save(self, data, dataset_path=None):
        """
        Saves the connection between the values required for the idtrackerai plugin
        :param dict data: Data from the path conf json.
        :param str dataset_path: Path to the json.
        :return: data
        """
        data['contours-value']  = self.contours.name
        data['crossings-value'] = self.crossings.name
        data['fragments-value'] = self.fragments.name

        return super().save(data, dataset_path)

    def load(self, data, dataset_path=None):

        if 'crossings-value' in data:
            self._crossings_val_name = data['crossings-value']

        if 'fragments-value' in data:
            self._fragments_val_name = data['fragments-value']

        if 'contours-value' in data:
            self._contours_val_name = data['contours-value']


        return super().load(data, dataset_path)




    def post_load(self):

        if hasattr(self, '_crossing_val_name'):
            self.crossings = self.object2d.find_dataset(self._crossing_val_name)
            del self._crossing_val_name

        if hasattr(self, '_fragments_val_name'):
            self.fragments = self.object2d.find_dataset(self._fragments_val_name)
            del self._fragments_val_name

        if hasattr(self, '_contours_val_name'):
            self.contours = self.object2d.find_dataset(self._contours_val_name)
            del self._contours_val_name
