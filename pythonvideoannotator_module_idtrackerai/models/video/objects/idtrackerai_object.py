import numpy as np, cv2, logging

from AnyQt import QtCore
from confapp import conf
from AnyQt.QtGui import QKeySequence
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlText
from pyforms.controls import ControlButton
from pyforms.controls import ControlCheckBox
from .idtrackerai_object_io import IdtrackeraiObjectIO
from .idtrackerai_object_mouse_events import IdtrackeraiObjectMouseEvents
from pythonvideoannotator_models.models.video.objects.video_object import VideoObject
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.dataset_gui import DatasetGUI

logger = logging.getLogger(__name__)

class SelectedBlob(object):
    """
    Class to store information about the selected blob.
    """
    def __init__(self, blob, blob_id, blob_pos):
        """
        :param int blob: Blob object.
        :param int blob_id: Id of the blob object.
        :param int blob_pos: Blob position.
        """
        self.blob     = blob
        self.position = blob_pos
        self.identity = blob_id




class IdtrackeraiObject(IdtrackeraiObjectMouseEvents, DatasetGUI, VideoObject, IdtrackeraiObjectIO, BaseWidget):

    def __init__(self, video):

        self._nametxt = ControlText('Name', default='idtracker object')
        self._closepaths_btn = ControlButton('Interpolate trajectories', default=self.__close_trajectories_gaps)
        self._del_centroids_btn = ControlButton('Delete centroids', default=self.__delete_centroids_btn_evt)
        self._add_blobchk = ControlCheckBox('Add centroid', default=False, visible=False)

        DatasetGUI.__init__(self)
        VideoObject.__init__(self)
        IdtrackeraiObjectMouseEvents.__init__(self)
        BaseWidget.__init__(self, 'IdtrackerAi Object', parent_win=video)

        self._video = video
        self._video += self
        self.create_tree_nodes()

        self.video_object     = None # IdtrackerAI VideoObject
        self.list_of_blobs    = None # IdtrackerAI ListOfBlobs
        self.list_of_framents = None # IdtrackerAI ListOfFragments


        self.formset = [
            '_nametxt',
            '_add_blobchk',
            '_del_centroids_btn',
            '_closepaths_btn',
            ' '
        ]

    def create_tree_nodes(self):
        self.treenode = self.tree.create_child(self.name, icon=conf.ANNOTATOR_ICON_OBJECT, parent=self.video.treenode)
        self.treenode.win = self

        self.tree.add_popup_menu_option(
            label='Convert to contours',
            function_action=self.__convert_to_contours,
            item=self.treenode, icon=conf.ANNOTATOR_ICON_CONTOUR
        )

    ######################################################################
    ### Events events ####################################################
    ######################################################################



    def __delete_centroids_btn_evt(self):
        if self.selected is None:
            return

        self.selected.blob.remove_centroid(
            self.selected.position
        )




    def __close_trajectories_gaps(self):
        """
        Make the interpolations.
        :return:
        """

        try:

            start = None
            end = None
            identity = None

            if self.video_object.is_centroid_updated:

                if self.selected:
                    start = self.input_int(
                        'Initial frame',
                        title='Select the initial frame for interpolation',
                        default=0
                    )

                    if start is None: return

                    end = self.input_int(
                        'Last frame',
                        title='Select the last frame for the interpolation',
                        default=0
                    )

                    identity = self.selected.identity

                else:
                    raise Exception('No identity selected.')


            self.video_object.interpolate( self.list_of_blobs, self.list_of_framents, identity, start, end )


        except Exception as e:
            logger.debug(str(e), exc_info=True)
            self.warning(str(e))

    ######################################################################
    ### Key events #######################################################
    ######################################################################

    def key_release_event(self, evt):

        key = QKeySequence(evt.modifiers() | evt.key()).toString().encode("ascii", "ignore").decode()

        logger.debug(key)

        # Jump to the next crossing.
        if key == conf.SHORT_KEYS['Go to next crossing.']:
            self.__jump2next_crossing()

        # Jump to the previous crossing.
        elif key == conf.SHORT_KEYS['Go to previous crossing.']:
            self.__jump2previous_crossing()


    def __jump2previous_crossing(self):
        """
        Jump to previous crossing.
        :return:
        """
        frame_index = self.mainwindow.timeline.value
        frames = self.list_of_blobs.blobs_in_video

        for i in range(frame_index-1, -1, -1):
            for blob in frames[i]:
                if blob.is_a_crossing:
                    self.mainwindow.timeline.value = blob.frame_number
                    return

    def __jump2next_crossing(self):
        """
        Jump to the next crossing
        :return:
        """
        frame_index = self.mainwindow.timeline.value
        frames = self.list_of_blobs.blobs_in_video

        for i in range(frame_index+1, len(frames) ):
            for blob in frames[i]:
                if blob.is_a_crossing:
                    self.mainwindow.timeline.value = blob.frame_number
                    return


    ######################################################################
    ### PROPERTIES #######################################################
    ######################################################################

    def draw(self, frame, frame_index):
        """
        Draw the objects in the current frame of the video.
        :param numpy.array frame: Image of the current frame.
        :param int frame_index: Index of the current frame in the video.
        :return numpy.array: The frame to draw.
        """
        if self.list_of_blobs is None: return

        image = frame.copy()
        blobs = self.list_of_blobs.blobs_in_video[frame_index]

        for blob in blobs:
            blob.draw( image, colors_lst=self.colors )

        if self.selected:
            # Draw the selected position
            p = self.selected.position
            cv2.circle(image, (int(round(p[0])), int(round(p[1]))), 10, (0, 0, 255), 2, lineType=cv2.LINE_AA)

        if self._tmp_object_pos:
            cv2.circle(image, self._tmp_object_pos, 8, (50,50,50), 2, lineType=cv2.LINE_AA)

        # Draw with transparency.
        cv2.addWeighted(frame, 0.5, image, 0.5, 0, dst=frame)

    ######################################################################
    ### PROPERTIES #######################################################
    ######################################################################

    @property
    def name(self):
        return self._nametxt.value

    @property
    def mainwindow(self): return self.video.mainwindow

    @property
    def tree(self): return self.video.tree

    @property
    def video_capture(self): return self.video.video_capture

    @property
    def parent_treenode(self):  return self.video.treenode








    def __convert_to_contours(self):

        resolution = self.video_object._resolution_reduction
        video = self.video

        objs = {}
        paths = {}
        crossings = {}
        fragments = {}
        modifications = {}
        idswitchs = {}

        total_blobs = len(self.list_of_blobs.blobs_in_video)

        # update the progress
        #if progress_event is not None:
        #    progress_event(0, max_count=total_blobs)

        for frame_index, frame_data in enumerate(self.list_of_blobs.blobs_in_video):

            # update the progress
            #if progress_event is not None:
            #    progress_event(frame_index, max_count=total_blobs)

            for blob in frame_data:

                fragment = blob.fragment_identifier
                crossing = blob.is_a_crossing
                contour = blob.contour

                for identity, centroid in zip(blob.final_identities, blob.final_centroids):

                    if identity not in objs:
                        obj = video.create_object()
                        obj.name = str(identity)
                        objs[identity] = obj

                        path = obj.create_path()
                        path.show_object_name = True
                        path.name = 'path'
                        paths[identity] = path

                        cnt = obj.create_contours()
                        cnt.name = 'contours'

                        c = obj.create_value()
                        c.name = 'crossings'
                        crossings[identity] = c

                        f = obj.create_value()
                        f.name = 'path fragments'
                        fragments[identity] = f

                        m = obj.create_value()
                        m.name = 'modifications'
                        modifications[identity] = m

                        i = obj.create_value()
                        i.name = 'switch identities'
                        idswitchs[identity] = i

                        obj.idtrackerai_path = path
                        path.contours = cnt
                        path.crossings = c
                        path.fragments = f
                        path.modifications = m
                        path.switch_identity = i

                    centroid = (int(round(centroid[0] / resolution)),
                                int(round(centroid[1] / resolution))) if centroid is not None else None

                    paths[identity].contours.set_contour(frame_index, np.int32(np.rint(contour / resolution)))
                    paths[identity][frame_index] = centroid
                    crossings[identity][frame_index] = 1 if crossing else 0
                    fragments[identity][frame_index] = fragment

        # update the progress
        #if progress_event is not None:
        #    progress_event(len(b.blobs_in_video), max_count=total_blobs)
