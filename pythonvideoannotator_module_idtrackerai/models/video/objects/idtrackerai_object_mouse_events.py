import math, logging

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
        self.position = blob_pos[0], blob_pos[1]
        self.identity = blob_id




class IdtrackeraiObjectMouseEvents(object):

    RADIUS_TO_SELECT_BLOB = 10

    def __init__(self):

        self._tmp_object_pos = None # used to store the temporary object position on drag
        self.selected        = None # Store information about the the selected blob.
        self._drag_active = True


    def on_click(self, event, x, y):
        """
        Event on click, it is used to select a blob.
        :param event: Click event.
        :param int x: X coordinate.
        :param int y: Y coordinate.
        """

        frame_index = self.mainwindow.timeline.value
        if not self._add_centroidchk.value:

            selected = False

            p0          = x, y


            # no blobs to select, exit the function
            if not self.list_of_blobs.blobs_in_video[frame_index]:
                self.selected = None
                return

            # blobs in the current frame
            blobs = self.list_of_blobs.blobs_in_video[frame_index]

            for blob in blobs:

                for identity, p1 in zip(blob.final_identities, blob.final_centroids_full_resolution):

                    # check if which blob was selected
                    if math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)<self.RADIUS_TO_SELECT_BLOB:

                        self.mainwindow.player.stop()

                        self.selected = SelectedBlob(blob, identity, p1)
                        selected = True
                        break

            if not selected:
                self.selected = None

        elif self.selected and self.selected.blob.frame_number == frame_index:

            # ask the new blob identity
            identity = self.input_int(
                'Type in the centroid identity',
                title='Identity',
                default=1
            )

            if not( identity in ['', None]):
                try:
                    self.selected.blob.add_centroid(self.video_object, (x,y), identity )
                except Exception as e:
                    logger.debug(str(e), exc_info=True)
                    self.warning(str(e), 'Error')

            self._add_centroidchk.value = False
            self._tmp_object_pos = None
            self._drag_active = False

        elif self.selected and self.selected.blob.frame_number != frame_index:
            self.selected = None
            self._add_centroidchk.value = False



    def on_double_click(self, event, x, y):

        p0          = x, y
        frame_index = self.mainwindow.timeline.value

        # if one object is selected
        if self.selected is not None:

            identity = self.selected.identity
            blob     = self.selected.blob
            centroid = self.selected.position

            # ask the new blob identity
            new_blob_identity = self.input_int(
                'Type in the new identity',
                title='New identity',
                default=identity if identity is not None else 0
            )

            # Update only if the new identity is different from the old one.
            if new_blob_identity is not None:
                try:
                    blob.update_identity(identity, new_blob_identity, centroid)
                    blob.propagate_identity(identity, new_blob_identity, centroid)
                except Exception as e:
                    logger.debug(str(e), exc_info=True)
                    self.warning(str(e), 'Error')

        elif self._add_blobchk.value:
            new_blob_identity = self.input_int(
                'Type the identity for the new blob',
                title='New identity',
                default=0
            )
            if not( new_blob_identity in ['', None]):
                try:
                    self.list_of_blobs.add_blob(self.video_object, frame_index,
                                                (x, y), new_blob_identity)
                except Exception as e:
                    logger.debug(str(e), exc_info=True)
                    self.warning(str(e), 'Error')


    def on_drag(self, p1, p2):

        if self.selected and \
           self.selected.identity and \
           math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)>5:

            self._tmp_object_pos = int(round(p2[0],0)), int(round(p2[1],0))


    def on_end_drag(self, p1, p2):

        if self._tmp_object_pos and self.selected and self.selected.blob:

            self.selected.blob.update_centroid(self.video_object, self.selected.position, p2, self.selected.identity)
            self.selected.position = p2

        self._tmp_object_pos = None
