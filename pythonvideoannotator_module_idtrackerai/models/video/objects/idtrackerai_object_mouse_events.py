import math

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




class IdtrackeraiObjectMouseEvents(object):

    def __init__(self):

        self._tmp_object_pos = None # used to store the temporary object position on drag
        self.selected        = None # Store information about the the selected blob.


    def on_click(self, event, x, y):
        """
        Event on click, it is used to select a blob.
        :param event: Click event.
        :param int x: X coordinate.
        :param int y: Y coordinate.
        """
        selected = False

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

                    self.selected = SelectedBlob(blob, identity, p1)
                    selected = True
                    break

        if not selected:
            self.selected = None


    def on_double_click(self, event, x, y):

        # if one object is selected
        if self.selected is not None:

            identity = self.selected.identity
            blob     = self.selected.blob

            # ask the new blob identity
            new_blob_identity = self.input_int(
                'Type in the new identity',
                title='New identity',
                default=identity if identity is not None else 0
            )

            # Update only if the new identity is different from the old one.
            if new_blob_identity!=identity:
                pass
                """
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
                """
        #else:
        # if no object is selected





    def on_drag(self, p1, p2):

        if self.selected and self.selected.identity and \
           math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)>5:

            self._tmp_object_pos = int(round(p2[0],0)), int(round(p2[1],0))


    def on_end_drag(self, p1, p2):

        if self._tmp_object_pos and self.selected.blob:

            if hasattr(self.selected.blob, 'interpolated_centroids'):
                index = self.selected.blob.final_identity.index(self.selected.id)
                self._selected.blob.interpolated_centroids[index] = p2
            else:
                self.selected.blob.centroid = p2

        self._tmp_object_pos = None





    ######################################################################
    ### PROPERTIES #######################################################
    ######################################################################

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

        elif hasattr(value.blob, 'interpolated_centroids'):
            self._del_centroids_btn.show()