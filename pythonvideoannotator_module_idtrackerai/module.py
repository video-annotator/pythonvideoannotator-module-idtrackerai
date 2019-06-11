from . import settings as conf
from AnyQt import QtGui

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