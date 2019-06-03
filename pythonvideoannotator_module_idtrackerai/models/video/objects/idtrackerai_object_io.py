import time, copy, numpy as np, os

from datetime import datetime
from idtrackerai.utils.py_utils import get_spaced_colors_util
from idtrackerai.postprocessing.get_trajectories import produce_output_dict
from idtrackerai.postprocessing.identify_non_assigned_with_interpolation import assign_zeros_with_interpolation_identities


class IdtrackeraiObjectIO(object):


    def save(self, data={}, project_path=None):

        self.list_of_blobs.disconnect()
        self.list_of_blobs_no_gaps = copy.deepcopy(self.list_of_blobs)

        path = os.path.join(project_path, 'preprocessing', 'blobs_collection_no_gaps.npy')
        np.save(path, self.list_of_blobs)

        timestamp_str = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H%M%S')

        trajectories_wo_gaps_file = os.path.join(
            project_path,
            'trajectories_wo_gaps',
            'trajectories_wo_gaps_{}.npy'.format(timestamp_str)
        )

        trajectories_wo_gaps = produce_output_dict(
            self.list_of_blobs_no_gaps.blobs_in_video,
            self.video_object
        )
        np.save(trajectories_wo_gaps_file, trajectories_wo_gaps)

        self.list_of_blobs = assign_zeros_with_interpolation_identities(
            self.list_of_blobs,
            self.list_of_blobs_no_gaps
        )

        trajectories_file = os.path.join(
            self.video_object.trajectories_folder,
            'trajectories_{}.npy'.format(timestamp_str)
        )
        trajectories = produce_output_dict(
            self.list_of_blobs.blobs_in_video,
            self.video_object
        )
        np.save(trajectories_file, trajectories)
        self.video_object.save()

        return {}



    def load_from_idtrackerai(self, project_path, video_object):

        self.video_object = video_object
        path = os.path.join(project_path, 'preprocessing', 'blobs_collection_no_gaps.npy')
        self.list_of_blobs = np.load(path, allow_pickle=True).item()
        self.list_of_blobs.reconnect()
        path = os.path.join(project_path, 'preprocessing', 'fragments.npy')
        self.list_of_framents = np.load(path, allow_pickle=True).item()
        self.colors = get_spaced_colors_util(self.video_object.number_of_animals, black = True)



