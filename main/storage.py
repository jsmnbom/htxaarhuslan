from django.core.files.storage import FileSystemStorage
from sorl.thumbnail import delete


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        delete(name)
        self.delete(name)
        return name
