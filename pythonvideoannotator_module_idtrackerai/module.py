from . import settings as conf
from AnyQt import QtGui
from pythonvideoannotator_module_idtrackerai.models.video.objects.idtrackerai_object import IdtrackeraiObject
import cv2

class Module(object):

	def __init__(self):
		"""
        This implements the DeepLab functionality
        """
		super(Module, self).__init__()

		self.mainmenu[1]['Modules'].append(
			{'idtrackerai': self.__open_idtrackerai_window, 'icon': QtGui.QIcon(conf.ANNOTATOR_ICON_IDTRACKERAI) },
		)

	def __open_idtrackerai_window(self):
		self.message('The idtrackerai plugin is installed', 'idtrackerai plugin')


	# def process_frame_event(self, frame):
	# 	selected = self.project.tree.selected_item
	#
	# 	if selected and isinstance(selected.win, IdtrackeraiObject):
	# 		reduction = selected.win.video_object.resolution_reduction
	# 		frame = cv2.resize(frame, None, fx=reduction, fy=reduction, interpolation=cv2.INTER_AREA)
	#
	# 	return super().process_frame_event(frame)
