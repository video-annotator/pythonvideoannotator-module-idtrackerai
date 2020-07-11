import numpy as np, cv2, logging

from AnyQt import QtCore
from confapp import conf
from AnyQt.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlText
from pyforms.controls import ControlButton
from pyforms.controls import ControlCheckBox
from .idtrackerai_object_io import IdtrackeraiObjectIO
from .idtrackerai_object_mouse_events import IdtrackeraiObjectMouseEvents
from pythonvideoannotator_models.models.video.objects.video_object import VideoObject
from pythonvideoannotator_models_gui.models.imodel_gui import IModelGUI

from pythonvideoannotator_module_idtrackerai import settings

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




class IdtrackeraiObject(IdtrackeraiObjectMouseEvents, IModelGUI, IdtrackeraiObjectIO, VideoObject, BaseWidget):

    RESET_BTN_LABEL = 'Clear user updates for all identities'
    RESET_BTN_LABEL_FOR_ID = 'Clear user updates for {0}'

    INTERPOLATE_BTN_LABEL = 'Global interpolation'
    INTERPOLATE_BTN_LABEL_FOR_ID = 'Local interpolation for {0}'

    SAVE_BTN_LABEL = 'Save updated identities'
    SAVE_BTN_LABEL_SAVING = 'Saving...'

    def __init__(self, video):
        self._closepaths_btn = ControlButton( self.INTERPOLATE_BTN_LABEL, default=self.__close_trajectories_gaps)
        self._del_centroids_btn = ControlButton('Delete centroid', default=self.__delete_centroids_btn_evt)
        self._add_centroidchk = ControlCheckBox('Add centroid to selected blob', default=False, visible=False)
        self._add_blobchk = ControlCheckBox('Add blob', default=False, visible=False)
        self._first_gfrag = ControlButton('Go to first global fragment', default=self.__go_to_first_global_fragment)

        self._reset_btn = ControlButton(self.RESET_BTN_LABEL, default=self.__reset_manually_corrected_data)

        self._save_btn = ControlButton(self.SAVE_BTN_LABEL, default=self.__save_updated_identities)

        IModelGUI.__init__(self)
        VideoObject.__init__(self, video=video)
        IdtrackeraiObjectMouseEvents.__init__(self)
        BaseWidget.__init__(self, 'Idtrackerai Object', parent_win=video)

        self.name = video.generate_child_name('Idtrackerai object')

        self._video = video
        self._video += self
        self.create_tree_nodes()

        self.video_object     = None # IdtrackerAI VideoObject
        self.list_of_blobs    = None # IdtrackerAI ListOfBlobs
        self.list_of_framents = None # IdtrackerAI ListOfFragments


        self.formset = [
            '_name',
            '_first_gfrag',
            '_add_centroidchk',
            '_del_centroids_btn',
            '_add_blobchk',
            '_reset_btn',
            '_closepaths_btn',
            '_save_btn',
            ' ',
            '<a href="https://pythonvideoannotator.readthedocs.io/en/add-idtracker/modules/idtrackerai.html" target="_blank" >Idtrackerai plugin documentation</a>',
            ' '
        ]

    def create_tree_nodes(self):
        self.treenode = self.tree.create_child(self.name, icon=settings.ANNOTATOR_ICON_IDTRACKERAI, parent=self.video.treenode)
        self.treenode.win = self

        self.tree.add_popup_menu_option(
            label='Convert to contours',
            function_action=self.__convert_to_contours,
            item=self.treenode, icon=conf.ANNOTATOR_ICON_CONTOUR
        )

        self.tree.add_popup_menu_option('-', item=self.treenode)
        self.tree.add_popup_menu_option(
            label='Remove',
            function_action=self.__remove_object,
            item=self.treenode, icon=conf.ANNOTATOR_ICON_DELETE
        )

    def get_first_frame(self):
        return self.video_object.get_first_frame(self.list_of_blobs)

    ######################################################################
    ### Events ###########################################################
    ######################################################################

    def __save_updated_identities(self):
        self._save_btn.label = self.SAVE_BTN_LABEL_SAVING
        self._save_btn.enabled = False
        QApplication.processEvents()
        self.save_updated_identities()
        self._save_btn.enabled = True
        self._save_btn.label = self.SAVE_BTN_LABEL
        QApplication.processEvents()

    def __go_to_first_global_fragment(self):
        self.mainwindow.player.video_index = self.get_first_frame()
        self.mainwindow.player.call_next_frame()

    def __remove_object(self):
        item = self.tree.selected_item
        if item is not None: self.video -= item.win

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
        self.mainwindow.progress_bar.min = 0
        self.mainwindow.progress_bar.max = total_blobs
        self.mainwindow.progress_bar.show()

        for frame_index, frame_data in enumerate(self.list_of_blobs.blobs_in_video):

            # update the progress
            self.mainwindow.progress_bar.value = frame_index

            for blob in frame_data:

                fragment = blob.fragment_identifier
                crossing = blob.is_a_crossing
                contour = blob.contour_full_resolution

                for identity, centroid in zip(blob.final_identities, blob.final_centroids_full_resolution):

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
        self.mainwindow.progress_bar.value = total_blobs
        self.mainwindow.progress_bar.hide()


    def __reset_manually_corrected_data(self):


        try:
            start = self.input_int(
                'Initial frame', title='Select the initial frame for the reset', default=0)

            if start is None:
                return

            end = self.input_int(
                'Last frame', title='Select the last frame for the reset', default=self.video_object.number_of_frames)

            if end is None:
                return

            identity = self.selected.identity if self.selected else None

            self.list_of_blobs.reset_user_generated_identities_and_centroids(self.video_object, start, end, identity)

            self.mainwindow.player.refresh()

        except Exception as e:
            logger.debug(str(e), exc_info=True)
            self.warning(str(e))


    def __close_trajectories_gaps(self):
        """
        Make the interpolations.
        :return:
        """
        try:
            start = None
            end   = None
            identity = None

            if self.video_object.is_centroid_updated:

                if self.selected:
                    start = self.input_int('Initial frame', title='Select the initial frame for interpolation', default=0)

                    if start is None: return

                    end = self.input_int(
                        'Last frame', title='Select the last frame for the interpolation',
                        default=self.video_object.number_of_frames
                    )

                    if end is None:
                        return

                    identity = self.selected.identity

                else:
                    raise Exception('Global interpolation is only possible if no centroids have been modified. Select an identity to perform a local interpolation')

            self.video_object.interpolate( self.list_of_blobs, self.list_of_framents, identity, start, end )

            self.mainwindow.player.refresh()



        except Exception as e:
            logger.debug(str(e), exc_info=True)
            self.warning(str(e))


    def __delete_centroids_btn_evt(self):
        if self.selected is None:
            return

        try:
            self.selected.blob.delete_centroid(
                self.video_object,
                self.selected.identity,
                self.selected.position,
                self.list_of_blobs.blobs_in_video[self.mainwindow.timeline.value],
            )
            self.mainwindow.player.refresh()

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

        # Check the add centroid check box
        elif key == conf.SHORT_KEYS['Check/Uncheck add centroid.']:
            self.__check_uncheck_add_centroid_box()

        # Check the add blob check box
        elif key == conf.SHORT_KEYS['Check/Uncheck add blob.']:
            self.__check_uncheck_add_blob_box()

        # Delete centroid
        elif key == conf.SHORT_KEYS['Delete centroid.']:
            self.__delete_centroids_btn_evt()


    def __check_uncheck_add_centroid_box(self):
        if self._add_centroidchk.visible and self.selected is not None:
            if self._add_centroidchk.value:
                self._add_centroidchk.value = False
            else:
                self._add_centroidchk.value = True


    def __check_uncheck_add_blob_box(self):
        if self._add_blobchk.visible and self.selected is None:
            if self._add_blobchk.value:
                self._add_blobchk.value = False
            else:
                self._add_blobchk.value = True



    def __jump2previous_crossing(self):
        """
        Jump to previous crossing.
        :return:
        """
        curr_frame = self.mainwindow.timeline.value
        next_frame = self.list_of_blobs.next_frame_to_validate(curr_frame if curr_frame else 1, 'past')
        #logger.debug('previous frame: {0}'.format(next_frame))

        if next_frame is not None:
            self.mainwindow.timeline.value = next_frame

    def __jump2next_crossing(self):
        """
        Jump to the next crossing
        :return:
        """
        curr_frame = self.mainwindow.timeline.value
        next_frame = self.list_of_blobs.next_frame_to_validate(curr_frame if curr_frame else 1, 'future')
        #logger.debug('next frame: {0}'.format(next_frame))

        if next_frame is not None:
            self.mainwindow.timeline.value = next_frame

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

        if frame_index >= len(self.list_of_blobs.blobs_in_video):
            return

        image = frame.copy()
        blobs = self.list_of_blobs.blobs_in_video[frame_index]

        new_selected=None
        for blob in blobs:
            if self.selected is not None:
                if blob.fragment_identifier == self.selected.blob.fragment_identifier and self.selected.identity in blob.final_identities:
                    index_identity = blob.final_identities.index(self.selected.identity)
                    new_centroid = blob.final_centroids[index_identity]
                    new_selected = SelectedBlob(blob, self.selected.identity, new_centroid)
        self.selected=new_selected


        for blob in blobs:

            blob.draw(
                image,
                colors_lst=self.colors,
                selected_id=self.selected.identity if self.selected else None,
                is_selected=self.selected.blob==blob if self.selected else False,
            )

        #if self.selected:
            # Draw the selected position
        #    p = self.selected.position
        #    cv2.circle(image, (int(round(p[0])), int(round(p[1]))), 14, (255, 255, 0), 2, lineType=cv2.LINE_AA)

        if self._tmp_object_pos:
            cv2.circle(image, self._tmp_object_pos, 8, (50,50,50), 2, lineType=cv2.LINE_AA)

        # Draw with transparency.
        cv2.addWeighted(frame, 0.5, image, 0.5, 0, dst=frame)

    ######################################################################
    ### PROPERTIES #######################################################
    ######################################################################


    @property
    def mainwindow(self): return self.video.mainwindow

    @property
    def tree(self): return self.video.tree

    @property
    def video_capture(self): return self.video.video_capture

    @property
    def parent_treenode(self):  return self.video.treenode


    @property
    def selected(self):
        """
        Return and set the selected blob
        :return SelectedBlob: Return the selected blob.
        """
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value

        if value is None:
            self._del_centroids_btn.hide()
            self._add_centroidchk.hide()
            self._add_blobchk.show()
            self._reset_btn.label = self.RESET_BTN_LABEL
            self._closepaths_btn.label = self.INTERPOLATE_BTN_LABEL
        else:
            self._add_centroidchk.show()
            self._add_blobchk.hide()
            self._reset_btn.label = self.RESET_BTN_LABEL_FOR_ID.format(self.selected.identity)
            self._closepaths_btn.label = self.INTERPOLATE_BTN_LABEL_FOR_ID.format(self.selected.identity)

            if value.blob.removable_identity(value.identity, self.list_of_blobs.blobs_in_video[value.blob.frame_number]):
                self._del_centroids_btn.show()
            else:
                self._del_centroids_btn.hide()
