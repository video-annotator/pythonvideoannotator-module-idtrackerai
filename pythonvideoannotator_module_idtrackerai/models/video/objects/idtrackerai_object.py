from pythonvideoannotator_models.models.video.objects.video_object import VideoObject
from pythonvideoannotator_models_gui.models.imodel_gui import IModelGUI
from pyforms.controls import ControlText
from pyforms.basewidget import BaseWidget
from confapp import conf
import numpy as np, cv2, math

class IdtrackeraiObject(IModelGUI, VideoObject, BaseWidget):

    def __init__(self, video):

        self._nametxt = ControlText('Name', default='Untitled')

        IModelGUI.__init__(self)
        VideoObject.__init__(self)
        BaseWidget.__init__(self, 'IdtrackerAi Object', parent_win=video)

        self._path = None
        self._data = None

        self._video = video
        self._video += self

        self._selected_id = None

        self.create_tree_nodes()

        self.formset = ['_nametxt']



    def create_tree_nodes(self):
        self.treenode = self.tree.create_child(self.name, icon=conf.ANNOTATOR_ICON_OBJECT, parent=self.video.treenode)
        self.treenode.win = self

    def on_click(self, event, x, y):
        pass

    def draw(self, frame, frame_index):

        if self._data is None: return

        blobs = self._data.blobs_in_video[frame_index]

        for blob in blobs:

            print(blob.next, blob.previous)

            identities = blob.final_identity if isinstance(blob.final_identity, list) else [blob.final_identity]
            centroids  = blob.interpolated_centroids if hasattr(blob, 'interpolated_centroids') else [blob.centroid]
            fragment   = blob.fragment_identifier
            crossing   = blob.is_a_crossing
            contour    = blob.contour

            for identity, centroid in zip(identities, centroids):

                pos = int(round(centroid[0],0)), int(round(centroid[1],0))

                cv2.polylines(frame, np.array([contour]), True, (0, 255, 0), 1)

                cv2.circle(frame, pos, 8, (255, 255, 255), -1, lineType=cv2.LINE_AA)
                cv2.circle(frame, pos, 6, (100, 0, 100), -1, lineType=cv2.LINE_AA)

                if self._selected_id==identity:
                    cv2.circle(frame, pos, 10, (0, 0, 255), 2, lineType=cv2.LINE_AA)

                if identity is not None:

                    if blob.user_generated_identity is not None:
                        idroot = 'u-'
                    elif blob.identity_corrected_closing_gaps is not None and blob.is_an_individual:
                        idroot = 'i-'
                    elif blob.identity_corrected_closing_gaps is not None:
                        idroot = 'c-'
                    elif blob.identity_corrected_solving_jumps is not None:
                        idroot = 'd-'
                    elif not blob.used_for_training:
                        idroot = 'a-'
                    else:
                        idroot = ''

                    idstr      = idroot + str(identity)
                    text_size  = cv2.getTextSize(idstr, cv2.FONT_HERSHEY_SIMPLEX, 1.0, thickness=2)
                    text_width = text_size[0][0]
                    str_pos    = pos[0] - text_width // 2, pos[1] - 12

                    cv2.putText(frame, idstr, str_pos, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), thickness=3, lineType=cv2.LINE_AA)
                    cv2.putText(frame, idstr, str_pos, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (100, 0, 100), thickness=2, lineType=cv2.LINE_AA)
                else:
                    bounding_box = blob.bounding_box_in_frame_coordinates
                    rect_color = blob.rect_color if hasattr(blob, 'rect_color') else (255,0,0)
                    cv2.rectangle(frame, bounding_box[0], bounding_box[1], rect_color, 2)




    def on_click(self, event, x, y):

        p0 = x, y
        frame_index = self.mainwindow.timeline.value

        blobs = self._data.blobs_in_video[frame_index]

        for blob in blobs:
            identities = blob.final_identity if isinstance(blob.final_identity, list) else [blob.final_identity]
            centroids  = blob.interpolated_centroids if hasattr(blob, 'interpolated_centroids') else [blob.centroid]

            for identity, p1 in zip(identities, centroids):
                if math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)<10:
                    self._selected_id = identity
                    self.mainwindow.player.stop()
                    new_blob_identity = self.input_int('Type in the new identity', title='New identity', default=identity)
                    if new_blob_identity!=identity:
                        blob._user_generated_identity = new_blob_identity

                        modified_blob = blob
                        # to take into account the modification already done in the current frame
                        count_past_corrections = 1
                        count_future_corrections = 0
                        new_blob_identity = modified_blob.user_generated_identity
                        if modified_blob.is_an_individual:
                            print("is and individual")
                            print("fragment_identifier ", modified_blob.fragment_identifier)
                            current = modified_blob

                            while len(current.next) == 1 and \
                                current.next[0].fragment_identifier == modified_blob.fragment_identifier:
                                print("in first while")
                                current.next[0]._user_generated_identity = new_blob_identity
                                current = current.next[0]
                                count_future_corrections += 1

                            current = modified_blob

                            while len(current.previous) == 1 and \
                                current.previous[0].fragment_identifier == modified_blob.fragment_identifier:
                                print("in second while")
                                current.previous[0]._user_generated_identity = new_blob_identity
                                current = current.previous[0]
                                count_past_corrections += 1

                    self.mainwindow.player.refresh()
                    break

    ######################################################################
    ### PROPERTIES #######################################################
    ######################################################################

    @property
    def name(self):
        return self._nametxt.value

    @property
    def mainwindow(self): return self.video.mainwindow

    @property
    def tree(self):        return self.video.tree

    @property
    def video_capture(self): return self.video.video_capture

    @property
    def parent_treenode(self):  return self.video.treenode

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._data = np.load(value).item()
        self._data.reconnect()
        self._path = value
