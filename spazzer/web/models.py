from ..collection.model import FileRecord, MountPoint, ArtistView, AlbumView, TrackView, or_
from ..collection.meta import _s
import transaction
import uuid
import os

class BaseModel(object):
    __modelview__ = None
    def __init__(self,name,parent=None):
        self.__name__ = name
        self.__parent__ = parent


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

    def search_artists(self,criteria):
        return self.__modelview__.search("%%%s%%" % criteria)

    def search_albums(self,criteria):
        return AlbumView.search(criteria)

    def search_tracks(self,criteria):
        return TrackView.search(criteria)

    def list_items(self, request):
        if self.__modelview__ is None:
            return None

        if "search" in request.params:
            search = u"%%%s%%" % request.params.get("search")
        elif "start" in request.params:
            if request.params.get("start") == "__num__":
                #maybe move this into collection model
                qry_results =  self.__modelview__.query().filter(or_(*(FileRecord.artist.like("%s%%" % x) for x in xrange(0,10)))).all()

                results = []
                for qr in qry_results:
                    results.append(ArtistView(*qr))

                return results
            else:
                search = u"%s%%" % request.params.get("start")

        else:
            search = None

        return self.__modelview__.search(search)

        
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
        key = uuid.UUID(key)
        result = self.__modelview__.get(key)
        if not result:
            raise KeyError, key

        result.__parent__ = self
        result.__name__ = key
        return result

class DownloadModel(BaseModel):
    """
    all downloads should go through this...
    need to shove params into querystring because names can have '/'
    which screws up paths.
    """
    def __getitem__(self, key):
        """
        no need for this
        """
        raise KeyError, key
    def get_track_file(self,track_id):
        result = TrackModel.__modelview__.get(uuid.UUID(track_id))

        if result:
            return (open(result.file_name, "rb"),
                  result.safe_file_name,
                  os.path.getsize(result.file_name))
        else:
            return None

    def get_album_file(self,album_name,artist = None, year = None):
        result = AlbumModel.__modelview__.get(album_name, artist, year)
        if result:
            return result.get_zip_file()
        else:
            return None

    def get_file(self,request):
        """
        this should ba called by the view,
        will deciper meaning from the request and 
        return the proper file
        """
        artist = request.params.get("artist")
        album = request.params.get("album")
        year = request.params.get("year")
        track = request.params.get("track")
        print artist,album,track,year
        if track:
            return  self.get_track_file(track)
        else:
            if album:
                return self.get_album_file(album,artist,year)
            else:
                return None
            
        
    

class AdminModel(BaseModel):pass

class SiteModel(object):
    __parent__ = None
    __name__ = None

    def __init__(self):
        self._models = {}
        self._models["artists"] = ArtistModel("artists", self)
        self._models["tracks"] = TrackModel("tracks", self)
        self._models["admin"] = AdminModel("admin", self)
        self._models["download"] = DownloadModel("download", self)

    def __getitem__(self,key):
        return self._models[key]

root = SiteModel()

def get_root(request):
    return root
