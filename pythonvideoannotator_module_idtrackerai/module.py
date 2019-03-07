from confapp import conf
from .idtrackerai_window import IdTrackerAIWindow

class Module(object):

	def __init__(self):
		"""
		This implements the Path edition functionality
		"""
		super(Module, self).__init__()

		self._idtrackerai_win = IdTrackerAIWindow(parent=self)

		self.mainmenu[1]['Modules'].append({
			'IdTracker.ai': self.__show_idtrackerai_window,
			'icon': conf.PYFORMS_ICON_EVENTTIMELINE_EXPORT
		})


	def __show_idtrackerai_window(self):

		self._idtrackerai_win.show()
