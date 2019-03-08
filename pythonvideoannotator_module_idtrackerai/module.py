import os, numpy as np
from confapp import conf
from AnyQt.QtWidgets import QFileDialog

class Module(object):

	def __init__(self):
		"""
		This implements the Path edition functionality
		"""
		super(Module, self).__init__()

		self.mainmenu[0]['File'].insert(1, {
			'Open IdTracker.ai project': self.__import_idtrackerai_project_evt,
			'icon': conf.ANNOTATOR_ICON_OPEN
		})

	def __import_idtrackerai_project_evt(self):

		project_path = QFileDialog.getExistingDirectory(
			self,
			"Select the project directory"
		)

		try:

			if project_path is not None and str(project_path) != '':

				blobs_path  = os.path.join(project_path, 'preprocessing', 'blobs_collection_no_gaps.npy')
				vidobj_path = os.path.join(project_path, 'video_object.npy')

				b = np.load(blobs_path).item()
				v = np.load(vidobj_path).item()

				resolution = v._resolution_reduction

				video = self.project.create_video()
				video.filepath = v._video_path

				objs  = {}
				paths = {}
				crossings = {}
				fragments = {}

				self._progress.max = len(b.blobs_in_video)
				self._progress.value = 0
				self._progress.show()


				for frame_index, frame_data in enumerate(b.blobs_in_video):
					self._progress.value = frame_index

					for blob in frame_data:

						identities = blob.final_identity if isinstance(blob.final_identity, list) else [blob.final_identity]
						centroids  = blob.interpolated_centroids if hasattr(blob, 'interpolated_centroids') else [blob.centroid]
						fragment   = blob.fragment_identifier
						crossing   = blob.is_a_crossing
						contour    = blob.contour

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

							centroid = (int(round(centroid[0]/resolution)), int(round(centroid[1]/resolution))) if centroid is not None else None

							paths[identity].contours.set_contour(frame_index, np.int32(np.rint(contour/resolution)) )
							paths[identity][frame_index]     = centroid
							crossings[identity][frame_index] = 1 if crossing else 0
							fragments[identity][frame_index] = fragment
		except Exception as e:
			self.critical(str(e), 'Error')

		self._progress.hide()