from .objects.idtrackerai_object import IdtrackeraiObject

from pythonvideoannotator_module_idtrackerai import settings as conf

from AnyQt.QtWidgets import QFileDialog

class IdTrackerVideo(object):

    def create_tree_nodes(self):

        super().create_tree_nodes()

        self.tree.add_popup_menu_option('-', item=self.treenode)
        self.tree.add_popup_menu_option(
            label='Add idtrackerai object',
            function_action=self.__import_idtrackerai_prj,
            item=self.treenode, icon=conf.ANNOTATOR_ICON_IDTRACKERAI
        )




    def __import_idtrackerai_prj(self):

        project_path = QFileDialog.getExistingDirectory(self, "Select the Idtrackerai project directory")

        if project_path is not None and str(project_path) != '':
            obj = self.create_idtrackerai_object()
            obj.load_from_idtrackerai(str(project_path))


    def create_idtrackerai_object(self):
        return IdtrackeraiObject(self)

    @property
    def idtrackerai_objects(self):
        for child in self._children:
            if isinstance(child, IdtrackeraiObject): yield child