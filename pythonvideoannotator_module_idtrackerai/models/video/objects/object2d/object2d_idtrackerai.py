
class IdTrackerObject2d(object):

    def save(self, data, object2d_path=None):

        if hasattr(self, 'idtrackerai_path'):
            data['idtrackerai-path'] = self.idtrackerai_path.name
        data = super().save(data, object2d_path)

        return data

    def load(self, data, object2d_path=None):
        super().load(data, object2d_path)

        for dt in self.datasets:
            if hasattr(dt, 'post_load'):
                dt.post_load()

        if 'idtrackerai-path' in data:
            self.idtrackerai_path = self.find_dataset(data['idtrackerai-path'])
