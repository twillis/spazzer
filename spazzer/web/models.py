from ..collection.model import FileRecord, MountPoint

class BaseModel(object):
    def __init__(self,name,parent=None):
        self.__name__ = name
        self.__parent__ = parent
class ArtistModel(BaseModel):pass
class AlbumModel(BaseModel):pass
class TitleModel(BaseModel):pass
class YearModel(BaseModel):pass
class AdminModel(BaseModel):pass
class StreamModel(BaseModel):pass
class SiteModel(object):
    __parent__ = None
    __name__ = None

    def __init__(self):
        self._models = {}
        self._models["artists"] = ArtistModel("artists", self)
        self._models["albums"] = AlbumModel("albums", self)
        self._models["titles"] = TitleModel("titles", self)
        self._models["years"] = YearModel("years", self)
        self._models["admin"] = AdminModel("admin", self)
        self._models["stream"] = StreamModel("stream", self)

    def __getitem__(self,key):
        return self._models[key]

root = SiteModel()

def get_root(request):
    return root
