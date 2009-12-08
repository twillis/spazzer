from ..collection.model import FileRecord, MountPoint, ArtistView, AlbumView, TrackView
from ..collection.meta import _s
import transaction

class BaseModel(object):
    __modelview__ = None
    def __init__(self,name,parent=None):
        self.__name__ = name
        self.__parent__ = parent

    def list_items(self, request):
        if self.__modelview__ is None:
            return None

        if "search" in request.params:
            search = u"\%%s\%" % request.params.get("search")
        elif "start" in request.params:
            search = u"%s\%" % request.params.get("start")
        else:
            search = None
        return self.__modelview__.search_list(search)

class ArtistModel(BaseModel):
    __modelview__ = ArtistView
    def __getitem__(self, key):
        """
        key = artist name
        """
        result = self.__modelview__.get(key)
        if not result:
            raise KeyError, key
        result.__parent__ = self
        result.__name__ = key
        #monkeypath
        def _x_(view):
            def _x(_key):
                return view.models[_key]
            return _x
        result.models = dict(albums=AlbumModel("albums",result))
        result.__getitem__ = _x_(result)
        return result

        
class AlbumModel(BaseModel):
    __modelview__ = AlbumView
    def __getitem__(self, key):
        #should have an ArtistView as parent hack?
        result = self.__modelview__.get(key, artist = self.__parent__.name)
        if not result:
            raise KeyError, key

        result.__parent__ = self
        result.__name__ = key

        return result

    def list_items(self, request):
        if self.__modelview__ is None:
            return None

        if "search" in request.params:
            search = u"\%%s\%" % request.params.get("search")
        elif "start" in request.params:
            search = u"%s\%" % request.params.get("start")
        else:
            search = None
        return self.__modelview__.get_by_artist(self.__parent__.name)

class TrackModel(BaseModel):
    __modelview__ = TrackView
    def __getitem__(self, key):
        result = self.__modelview__.get(key)
        if not result:
            raise KeyError, key

        result.__parent__ = self
        result.__name__ = key
        return result

class YearModel(BaseModel):pass

class AdminModel(BaseModel):pass

class StreamModel(BaseModel):pass

class SiteModel(object):
    __parent__ = None
    __name__ = None

    def __init__(self):
        self._models = {}
        self._models["artists"] = ArtistModel("artists", self)

        self._models["tracks"] = TrackModel("tracks", self)
        self._models["years"] = YearModel("years", self)
        self._models["admin"] = AdminModel("admin", self)
        self._models["stream"] = StreamModel("stream", self)

    def __getitem__(self,key):
        return self._models[key]

root = SiteModel()

def get_root(request):
    return root
