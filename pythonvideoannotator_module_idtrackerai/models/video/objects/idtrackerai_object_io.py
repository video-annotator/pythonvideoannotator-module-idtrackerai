import time, copy, numpy as np, os, logging

from datetime import datetime
from idtrackerai.utils.py_utils import get_spaced_colors_util
from idtrackerai.postprocessing.get_trajectories import produce_output_dict
from idtrackerai.postprocessing.identify_non_assigned_with_interpolation import assign_zeros_with_interpolation_identities

logger = logging.getLogger(__name__)

class IdtrackeraiObjectIO(object):

    FACTORY_FUNCTION = 'create_idtrackerai_object'


    def save(self, data={}, obj_path=None):

        idtrackerai_prj_path = os.path.relpath(self.idtrackerai_prj_path, obj_path)
        data['idtrackerai-project-path'] = idtrackerai_prj_path

        self.list_of_blobs.disconnect()
        self.list_of_blobs_no_gaps = copy.deepcopy(self.list_of_blobs)

        path = os.path.join(obj_path, idtrackerai_prj_path, 'preprocessing', 'blobs_collection_no_gaps.npy')
        np.save(path, self.list_of_blobs)

        timestamp_str = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H%M%S')

        trajectories_wo_gaps_file = os.path.join(
            obj_path,
            idtrackerai_prj_path,
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
            obj_path,
            self.video_object.trajectories_folder,
            'trajectories_{}.npy'.format(timestamp_str)
        )
        trajectories = produce_output_dict(
            self.list_of_blobs.blobs_in_video,
            self.video_object
        )
        np.save(trajectories_file, trajectories)
        self.video_object.save()

        return super().save(data, obj_path)



    def load(self, data, obj_path):
        idtrackerai_prj_path = os.path.join(obj_path, data['idtrackerai-project-path'])

        videoobj = np.load(os.path.join(idtrackerai_prj_path, 'video_object.npy'), allow_pickle=True).item()

        self.load_from_idtrackerai(
            idtrackerai_prj_path,
            videoobj
        )




    def load_from_idtrackerai(self, project_path, video_object=None):

        if video_object is None:
            vidobj_path = os.path.join(project_path, 'video_object.npy')
            video_object = np.load(vidobj_path, allow_pickle=True).item()

        self.idtrackerai_prj_path = project_path

        self.video_object = video_object
        path = os.path.join(project_path, 'preprocessing', 'blobs_collection_no_gaps.npy')
        if not os.path.exists(path):
            path = os.path.join(project_path, 'preprocessing', 'blobs_collection.npy')

        self.list_of_blobs = np.load(path, allow_pickle=True).item()
        self.list_of_blobs.reconnect()
        path = os.path.join(project_path, 'preprocessing', 'fragments.npy')
        self.list_of_framents = np.load(path, allow_pickle=True).item()
        self.colors = get_spaced_colors_util(self.video_object.number_of_animals, black = True)



