import numpy as np, os

def import_idtrackerai_project(project, project_path, progress_event=None):
    """

    :param pythonvideoannotator_models.Project project: Python video annotator project
    :param str project_path: IdtrackerAI project.
    :param func progress_event: Function to update the progress. func(progress_count, max_count=None)
    :return:
    """

    blobs_path = os.path.join(project_path, 'preprocessing', 'blobs_collection_no_gaps.npy')
    vidobj_path = os.path.join(project_path, 'video_object.npy')

    b = np.load(blobs_path).item()
    v = np.load(vidobj_path).item()

    resolution = v._resolution_reduction

    video = project.create_video()
    video.filepath = v._video_path

    objs = {}
    paths = {}
    crossings = {}
    fragments = {}

    # update the progress
    if progress_event is not None:
        progress_event(0, max_count=len(b.blobs_in_video))

    for frame_index, frame_data in enumerate(b.blobs_in_video):

        # update the progress
        if progress_event is not None:
            progress_event(frame_index)

        for blob in frame_data:

            identities = blob.final_identity if isinstance(blob.final_identity, list) else [blob.final_identity]
            centroids = blob.interpolated_centroids if hasattr(blob, 'interpolated_centroids') else [blob.centroid]
            fragment = blob.fragment_identifier
            crossing = blob.is_a_crossing
            contour = blob.contour

            for identity, centroid in zip(identities, centroids):

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

                    v1 = obj.create_value()
                    v1.name = 'path modifications'

                    v2 = obj.create_value()
                    v2.name = 'switch identity'

                    obj.idtrackerai_path = path
                    path.contours = cnt
                    path.crossings = c
                    path.fragments = f
                    path.modifications = v1
                    path.switch_identity = v2

                centroid = (int(round(centroid[0] / resolution)),
                            int(round(centroid[1] / resolution))) if centroid is not None else None

                paths[identity].contours.set_contour(frame_index, np.int32(np.rint(contour / resolution)))
                paths[identity][frame_index] = centroid
                crossings[identity][frame_index] = 1 if crossing else 0
                fragments[identity][frame_index] = fragment

    # update the progress
    if progress_event is not None:
        progress_event( len(b.blobs_in_video) )