import time, copy, numpy as np, os, logging

from confapp import conf

try:
    import sys

    sys.path.append(os.getcwd())
    import local_settings

    conf += local_settings
except Exception as e:
    print(e)
    pass

from datetime import datetime
from idtrackerai.utils.py_utils import get_spaced_colors_util
from idtrackerai.tracker.get_trajectories import produce_output_dict
from idtrackerai.tracker.trajectories_to_csv import (
    convert_trajectories_file_to_csv_and_json,
)
from idtrackerai.groundtruth_utils.generate_groundtruth import (
    generate_groundtruth,
)
from idtrackerai.groundtruth_utils.compute_groundtruth_statistics_general import (
    compute_and_save_session_accuracy_wrt_groundtruth,
)

logger = logging.getLogger(__name__)


class IdtrackeraiObjectIO(object):

    FACTORY_FUNCTION = "create_idtrackerai_object"

    def save(self, data={}, obj_path=None):
        idtrackerai_prj_path = os.path.relpath(
            self.idtrackerai_prj_path, obj_path
        )
        data["idtrackerai-project-path"] = idtrackerai_prj_path
        return super().save(data, obj_path)

    def save_updated_identities(self):
        logger.info("Disconnecting list of blobs...")
        self.list_of_blobs.disconnect()

        logger.info("Saving list of blobs...")
        path = os.path.join(
            self.idtrackerai_prj_path,
            "preprocessing",
            "blobs_collection_no_gaps.npy",
        )
        np.save(path, self.list_of_blobs)
        logger.info("List of blobs saved")

        timestamp_str = datetime.fromtimestamp(time.time()).strftime(
            "%Y-%m-%d_%H%M%S"
        )

        trajectories_wo_gaps_file = os.path.join(
            self.idtrackerai_prj_path,
            "trajectories_wo_gaps",
            "trajectories_wo_gaps_{}.npy".format(timestamp_str),
        )
        logger.info("Producing trajectories without gaps ...")
        trajectories_wo_gaps = produce_output_dict(
            self.list_of_blobs.blobs_in_video, self.video_object
        )
        logger.info("Saving trajectories without gaps...")
        np.save(trajectories_wo_gaps_file, trajectories_wo_gaps)
        if conf.CONVERT_TRAJECTORIES_DICT_TO_CSV_AND_JSON:
            logger.info("Saving trajectories in csv format...")
            convert_trajectories_file_to_csv_and_json(
                trajectories_wo_gaps_file
            )
        logger.info("Trajectories without gaps saved")

        trajectories_file = os.path.join(
            self.idtrackerai_prj_path,
            "trajectories",
            "trajectories_{}.npy".format(timestamp_str),
        )
        logger.info("Producing trajectories")
        trajectories = produce_output_dict(
            self.list_of_blobs.blobs_in_video, self.video_object
        )
        logger.info("Saving trajectories...")
        np.save(trajectories_file, trajectories)
        if conf.CONVERT_TRAJECTORIES_DICT_TO_CSV_AND_JSON:
            logger.info("Saving trajectories in csv format...")
            convert_trajectories_file_to_csv_and_json(trajectories_file)
        logger.info("Trajectories saved")
        logger.info("Saving video object...")
        self.video_object.save()
        logger.info("Video saved")

    def compute_gt_accuracy(self, generate=True, start=0, end=-1):
        if generate:
            generate_groundtruth(
                self.video_object,
                blobs_in_video=self.list_of_blobs.blobs_in_video,
                start=start,
                end=end,
                save_gt=True,
            )

        compute_and_save_session_accuracy_wrt_groundtruth(
            self.video_object, "normal"
        )
        logger.info(f"{self.video_object.gt_accuracy}")

    def load(self, data, obj_path):
        path = data.get("idtrackerai-project-path", None)
        if path is None:
            return

        idtrackerai_prj_path = os.path.join(obj_path, path)

        logger.info("Loading video object...")
        vidobj_path = os.path.join(idtrackerai_prj_path, "video_object.npy")
        videoobj = np.load(vidobj_path, allow_pickle=True).item()
        videoobj.update_paths(vidobj_path)
        logger.info("Video object loaded")

        self.load_from_idtrackerai(idtrackerai_prj_path, videoobj)

    def load_from_idtrackerai(self, project_path, video_object=None):

        vidobj_path = os.path.join(project_path, "video_object.npy")
        if video_object is None:
            video_object = np.load(vidobj_path, allow_pickle=True).item()
            video_object.update_paths(vidobj_path)

        self.idtrackerai_prj_path = project_path

        logger.info("Updating paths in video object")
        self.video_object = video_object
        video_object.update_paths(vidobj_path)
        logger.info("Paths updated")

        path = os.path.join(
            project_path, "preprocessing", "blobs_collection_no_gaps.npy"
        )
        if not os.path.exists(path):
            path = os.path.join(
                project_path, "preprocessing", "blobs_collection.npy"
            )

        logger.info("Loading list of blobs...")
        self.list_of_blobs = np.load(path, allow_pickle=True).item()
        logger.info("List of blobs loaded")
        logger.info("Connecting list of blobs...")
        self.list_of_blobs.compute_overlapping_between_subsequent_frames()
        logger.info("List of blobs connected")
        logger.info("Loading fragments...")
        path = os.path.join(project_path, "preprocessing", "fragments.npy")
        if (
            not os.path.exists(path)
            and self.video_object.user_defined_parameters["number_of_animals"]
            == 1
        ):
            self.list_of_framents = None
            logger.info("Fragments did not exist")
        else:
            self.list_of_framents = np.load(path, allow_pickle=True).item()
            logger.info("Loading fragments...")
        self.colors = get_spaced_colors_util(
            self.video_object.user_defined_parameters["number_of_animals"],
            black=True,
        )
