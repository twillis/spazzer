"""
Database model for collection metadata
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.sql import or_
from meta import _s
from alchemyextra.schema import id_column
import os
from cStringIO import StringIO
import zipfile

Base = declarative_base()

def cleanse_filename(fname):
    fname = os.path.split(fname)[1]
    INVALID = u"\"*/:<>?\\|"
    VALID_RANGE = range(128)
    result = []
    for c in fname:
        val = ord(c)
        if not c in INVALID and val in VALID_RANGE:
            result.append(c)
        else:
            result.append(u"_")
    result = u"".join(result)
    return result.replace(u" ", u"_")
    

class MountPoint(Base):
    __tablename__ = "mount_points"
    id = id_column()
    mount = Column(Unicode(1024), unique = True)

class FileRecord(Base):
    __tablename__ = "files"
    id = id_column()
    file_name = Column(Unicode(1024), unique = True, index = True)
    artist = Column(Unicode(255), nullable = True, index = True)
    album = Column(Unicode(255), nullable = True, index = True)
    title = Column(Unicode(255), nullable = True, index = True)
    year = Column(Integer, nullable = True, index = True)
    track = Column(Integer, nullable = True)
    create_date = Column(DateTime(), nullable = False)
    modify_date = Column(DateTime(), nullable = False)

    @classmethod
    def get_by_id(cls,id):
        return cls.query().get(id)

    @classmethod
    def get_by_filename(cls,file_name):
        return cls.query().filter(cls.file_name == file_name).first()

    @classmethod
    def query(cls,*attrs):
        """
        attrs to select if None then entire class
        """
        if len(attrs) == 0:
            attrs = [cls]
        print attrs
        return _s().query(*attrs)

    def __init__(self, file_name,create_date,modify_date,
                 artist=None,
                 title=None,
                 album=None,
                 year=None,
                 track=None):

        self.file_name = file_name

        self.update(create_date, modify_date, 
                    artist,
                    album,
                    title,
                    year,
                    track)

    def update(self,create_date, modify_date,
               artist = None, 
               album = None,
               title = None,
               year = None, 
               track = None):

        self.create_date = create_date
        self.modify_date = modify_date
        self.artist = artist
        self.album = album
        self.year = year
        self.track = track
        self.title = title

    def _safe_file_name(self):
        FMT_STR = "%s - %s - %s (%d) - %s%s"
        return cleanse_filename(FMT_STR % (self.track,
                                            self.artist,
                                            self.album,
                                            self.year,
                                            self.title,
                                            os.path.splitext(self.file_name)[1]))
    safe_file_name = property(_safe_file_name)

#    These have nothing to do with db persistence, column/table mapping or anything
class ArtistView(object):
    """
    Represents an Artist view of the collection
    """
    def __init__(self, name):
        self.name = name

    @classmethod
    def query(cls):
        return FileRecord.query(FileRecord.artist).filter(FileRecord.artist!=None).distinct()
        
    @classmethod
    def search_list(cls, criteria = None):
        qry = cls.query()
        if criteria:
            qry = qry.filter(FileRecord.artist.like(u"%s" % criteria))
        
        results = []
        
        for result in qry.all():
            results.append(cls(*result))

        return results
            
    @classmethod
    def get(cls,name):
        result = cls.query().filter(FileRecord.artist==name).first()

        if result and len(result)>0:
            return cls(*result)
        else:
            return None

    def __repr__(self):
        return self.name
        return self.name.title()

    def get_albums(self):
        return AlbumView.get_by_artist(self.name)

class AlbumView(object):
    def __init__(self, name, year):
        self.name = name
        self.year = year

    def __repr__(self):
        return u"%s - %s" % (self.name.title(),self.year)

    @classmethod
    def query(cls):
        return FileRecord.query(FileRecord.album, FileRecord.year).filter(FileRecord.album != None).distinct()

    @classmethod
    def get(cls,name, artist = None, year = None):
        qry = cls.query().filter(FileRecord.album==name)

        if artist:
            qry = qry.filter(FileRecord.artist == artist)

        if year:
            qry = qry.filter(FileRecord.year == year)
        result = qry.first()

        if result and len(result)>0:
            return cls(*result)
        else:
            return None
        
    @classmethod
    def get_by_artist(cls,artist):
        results = cls.query().filter(FileRecord.artist==artist).order_by(FileRecord.year).all()
        albums = []
        if results and len(results) > 0:
            for result in results:
                albums.append(cls(*result))

            return albums

        return albums

    def get_tracks(self):
        return TrackView.get_by_album(self.name)

    @classmethod
    def search_list(cls, criteria = None):
        qry = cls.query()
        if criteria:
            qry = qry.filter(FileRecord.artist.like(u"\%%s\%" % criteria))
        
        results = []
        
        for result in qry.all():
            results.append(cls(*result))

        return results

    def get_zip_file(self):
        """
        relying on caller to close the string io
        """
        io = StringIO()
        zf = zipfile.ZipFile(io,"w")
        try:
            for track in self.get_tracks():
                zf.write(track.file_name,
                         track.safe_file_name,
                         zipfile.ZIP_DEFLATED)
        finally:
            zf.close()

        io.reset()
        io.seek(0,2)
        length = io.tell()
        io.reset()
        return io,cleanse_filename("%s - %s.zip" % (self.name, self.year)),length
        
class TrackView(object):
    def __init__(self,fileRecord):
        self.__record = fileRecord

    @classmethod
    def query(cls):
        return FileRecord.query()

    @classmethod
    def get(cls,fid):
        print "File Id: %s" % fid
        val = cls.query().get(fid)
        assert val is not None
        print "File: %s" % val
        return cls(val)

    @classmethod
    def get_by_album(cls,album,artist = None, year = None):
        qry = cls.query().filter(FileRecord.album == album)

        if artist:
            qry = qry.filter(FileRecord.artist == artist)

        if year:
            qry = qry.filter(FileRecord.year == year)

        results = qry.order_by(FileRecord.track).all()
        tracks = []
        if results and len(results)>0:
            for result in results:
                tracks.append(cls(result))

        return results

    @classmethod
    def get_by_artist(cls,artist):
        results = cls.query().filter(FileRecord.artist == artist)
        tracks = []
        if results and len(results)>0:
            for result in results:
                tracks.append(cls(result))
        return tracks

    def __getattr__(self, name):
        """
        happy path to staying in sync with FileRecord via delegation
        """
        return getattr(self.__record, name)

    def __repr__(self):
        return u"%d - %s" % (self.track, self.title.title())

        
