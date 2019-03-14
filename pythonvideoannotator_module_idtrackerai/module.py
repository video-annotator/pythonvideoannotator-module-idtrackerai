import os, numpy as np
from confapp import conf
from AnyQt.QtWidgets import QFileDialog
from .idtrackerai_importer import import_idtrackerai_project

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

	def __update_progress_evt(self, progress_count, max_count=None):
		if max_count is not None:
			self._progress.max = max_count
			self._progress.value = 0
			self._progress.show()
		elif self._progress.max==progress_count:
			self._progress.hide()
		else:
			self._progress.value = progress_count
		

	def __import_idtrackerai_project_evt(self):

		project_path = QFileDialog.getExistingDirectory(
			self,
			"Select the project directory"
		)
		try:
			if project_path is not None and str(project_path) != '':

				import_idtrackerai_project(
					self.project,
					project_path,
					progress_event=self.__update_progress_evt
				)

		except Exception as e:
			self.critical(str(e), 'Error')

		self._progress.hide()