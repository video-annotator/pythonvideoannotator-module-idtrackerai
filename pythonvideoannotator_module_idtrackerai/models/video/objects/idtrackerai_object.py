from pythonvideoannotator_models.models.video.objects.video_object import VideoObject
from idtrackerai.postprocessing.assign_them_all import close_trajectories_gaps
from pythonvideoannotator_models_gui.models.imodel_gui import IModelGUI
from pyforms.controls import ControlText
from pyforms.controls import ControlButton
from pyforms.basewidget import BaseWidget
from AnyQt import QtCore
from confapp import conf
import numpy as np, cv2, math, os


class IdtrackeraiObject(IModelGUI, VideoObject, BaseWidget):

    def __init__(self, video):

        self._nametxt = ControlText('Name', default='Untitled')
        self._closepaths_btn = ControlButton('Close trajectories', default=self.__close_trajectories_gaps)

        IModelGUI.__init__(self)
        VideoObject.__init__(self)
        BaseWidget.__init__(self, 'IdtrackerAi Object', parent_win=video)

        self._video = video
        self._video += self
        self.create_tree_nodes()

        self.video_object     = None # IdtrackerAI VideoObject
        self.list_of_blobs    = None # IdtrackerAI ListOfBlobs
        self.list_of_framents = None # IdtrackerAI ListOfFragments

        self._selected_id = None

        self.formset = ['_nametxt', '_closepaths_btn']


    def save(self, data={}, project_path=None):
        self.list_of_blobs.disconnect()
        path = os.path.join(project_path, 'preprocessing', 'blobs_collection_no_gaps.npy')
        np.save(path, self.list_of_blobs)
        return {}

    def load_from_idtrackerai(self, project_path, video_object):
        self.video_object = video_object
        path = os.path.join(project_path, 'preprocessing', 'blobs_collection_no_gaps.npy')
        self.list_of_blobs = np.load(path).item()
        self.list_of_blobs.reconnect()
        path = os.path.join(project_path, 'preprocessing', 'fragments.npy')
        self.list_of_framents = np.load(path).item()

    def create_tree_nodes(self):
        self.treenode = self.tree.create_child(self.name, icon=conf.ANNOTATOR_ICON_OBJECT, parent=self.video.treenode)
        self.treenode.win = self


    def draw(self, frame, frame_index):

        if self.list_of_blobs is None: return

        blobs = self.list_of_blobs.blobs_in_video[frame_index]

        for blob in blobs:

            identities = blob.final_identity if isinstance(blob.final_identity, list) else [blob.final_identity]
            centroids  = blob.interpolated_centroids if hasattr(blob, 'interpolated_centroids') else [blob.centroid]
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

        p0          = x, y
        frame_index = self.mainwindow.timeline.value

        # blobs in the current frame
        blobs = self.list_of_blobs.blobs_in_video[frame_index]

        for blob in blobs:

            identities = blob.final_identity if isinstance(blob.final_identity, list) else [blob.final_identity]
            centroids  = blob.interpolated_centroids if hasattr(blob, 'interpolated_centroids') else [blob.centroid]

            for identity, p1 in zip(identities, centroids):

                # check if which blob was selected
                if math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)<10:

                    self.mainwindow.player.stop()

                    self._selected_id = identity

                    # ask the new blob identity
                    new_blob_identity = self.input_int(
                        'Type in the new identity',
                        title='New identity',
                        default=identity
                    )

                    # Update only if the new identity is different from the old one.
                    if new_blob_identity!=identity:

                        blob._user_generated_identity = new_blob_identity

                        modified_blob = blob
                        # to take into account the modification already done in the current frame
                        count_past_corrections   = 1
                        count_future_corrections = 0
                        new_blob_identity        = modified_blob.user_generated_identity

                        if modified_blob.is_an_individual:
                            current = modified_blob

                            while len(current.next) == 1 and \
                                current.next[0].fragment_identifier == modified_blob.fragment_identifier:

                                current.next[0]._user_generated_identity = new_blob_identity
                                current = current.next[0]
                                count_future_corrections += 1

                            current = modified_blob
                            while len(current.previous) == 1 and \
                                current.previous[0].fragment_identifier == modified_blob.fragment_identifier:
                                current.previous[0]._user_generated_identity = new_blob_identity
                                current = current.previous[0]
                                count_past_corrections += 1

                    self.mainwindow.player.refresh()
                    break



    def __jump2next_crossing(self):
        frame_index = self.mainwindow.timeline.value
        frames = self.list_of_blobs.blobs_in_video

        for i in range(frame_index+1, len(frames) ):
            for blob in frames[i]:
                if blob.is_a_crossing:
                    self.mainwindow.timeline.value = blob.frame_number
                    return

    def __jump2previous_crossing(self):
        frame_index = self.mainwindow.timeline.value
        frames = self.list_of_blobs.blobs_in_video

        for i in range(frame_index-1, -1, -1):
            for blob in frames[i]:
                if blob.is_a_crossing:
                    self.mainwindow.timeline.value = blob.frame_number
                    return

    def key_release_event(self, evt):

        if evt.key() == QtCore.Qt.Key_E:
            self.__jump2next_crossing()

        elif evt.key() == QtCore.Qt.Key_Q:
            self.__jump2previous_crossing()


    def __close_trajectories_gaps(self):
        self.list_of_blobs = close_trajectories_gaps(
            self.video_object,
            self.list_of_blobs,
            self.list_of_framents
        )





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