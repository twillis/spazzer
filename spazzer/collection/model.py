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


class Queryable(object):
    """
    adds query class method as a convenience.
    """

    @classmethod
    def query(cls, *attrs):
        """
        attrs to select if None then entire class
        """
        if len(attrs) == 0:
            attrs = [cls]
        return _s().query(*attrs)


def cleanse_filename(fname):
    """
    make filename safe for fat32(lowest common denominator)
    since we're going off tag info which can (and likely will) include
    characters that are not handled too well in a filename. this function
    will just replace any offending characters with "_"
    """
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


class MountPoint(Base, Queryable):
    """
    A collection is made up of filesystem mountpoints(directories).
    we hold them for periodic scanning in the db rather than
    make the user edit another config file.
    """
    __tablename__ = "mount_points"
    id = id_column() #perhaps superfulous
    _mount = Column("mount", Unicode(1024), unique = True)

    def __init__(self, mount):
        self._mount = mount

    def _get_mount(self):
        """
        depending on how it was saved to db we may need to append a path
        sep so that we can traverse up the rest of it during scanning
        """
        if not self._mount.endswith(os.path.sep):
            return "%s%s" % (self._mount, os.path.sep)
        else:
            return self._mount

    mount = property(_get_mount)


class FileRecord(Base, Queryable):
    """
    tag information that was gleaned from a file during scan.
    as far as I can figure, there's no reasonable way to de-normalize this
    without making assumptions that will be invalid by someone's obscure
    music taste. So the approach is we are merely indexing the tagf information
    and providing canned queries to help navigate to what you want to hear.

    anything else is an excercise in enginering masturbation in my opinion.
    """
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
    def get_by_id(cls, id):
        """
        by primary key (uuid)
        """
        return cls.query().get(id)

    @classmethod
    def get_by_filename(cls, file_name):
        """
        by unique filename, needs entire path
        """
        return cls.query().filter(cls.file_name == file_name).first()

    def __init__(self, file_name, create_date, modify_date,
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

    def update(self, create_date, modify_date,
               artist = None,
               album = None,
               title = None,
               year = None,
               track = None):
        """
        set all attributes
        """
        self.create_date = create_date
        self.modify_date = modify_date
        self.artist = artist
        self.album = album
        self.year = year
        self.track = track
        self.title = title

    def on_compilation(self):
        """
        is this track on an album that has multiple artists?
        """
        if not hasattr(self, "__compilation"):
            self.__compilation = self.query(FileRecord.artist).filter(
                FileRecord.album == self.album).filter(
                FileRecord.year == self.year).distinct().count() > 1
        return self.__compilation

    def _safe_file_name(self):
        """
        generate a fat32 safe filename based on information in the tags
        """
        FMT_STR = "%s - %s - %s (%d) - %s%s"
        return cleanse_filename(FMT_STR % (self.track,
                                            self.artist.replace("/", "\\"),
                                            self.album.replace("/", "\\"),
                                            self.year,
                                            self.title.replace("/", "\\"),
                                       os.path.splitext(self.file_name)[1]))

    safe_file_name = property(_safe_file_name)

#These have nothing to do with db persistence, column/table mapping or anything

class ArtistView(object):
    """
    Represents an Artist view of the collection
    """

    def __init__(self, name):
        self.name = name

    @classmethod
    def query(cls):
        return FileRecord.query(FileRecord.artist).filter(
            FileRecord.artist!=None).distinct()

    @classmethod
    def search(cls, criteria = None):
        """
        Find by artist name, handles the case where 'Artist' and 'The Artist'
        are regarded as the same artist depending on how pretentious you are.
        """
        qry = cls.query()

        if criteria:
            qry = qry.filter(or_(
                FileRecord.artist.like(u"%s" % criteria),
                FileRecord.artist.like(u"The %s" % criteria)))

        results = []

        for result in qry.all():
            results.append(cls(*result))

        return results

    @classmethod
    def get(cls, name):
        """
        find by exact artist name, we're pretending that we have a table
        of artists whose primary key is name.
        """
        result = cls.query().filter(FileRecord.artist==name).first()

        if result and len(result)>0:
            return cls(*result)
        else:
            return None

    def __repr__(self):
        return self.name

    def get_albums(self):
        """
        here for convenience, dispatch to AlbumView
        """
        return AlbumView.get_by_artist(self.name)


class AlbumView(object):
    """
    respresents an album in the collection. and album is loosely defined to
    be a unique(title,year), though i'm sure there are edge cases which make
    this false.
    """

    def __init__(self, name, year):
        self.name = name
        self.year = year

    def __repr__(self):
        return u"%s - %s" % (self.name.title(), self.year)

    @classmethod
    def query(cls):
        return FileRecord.query(FileRecord.album, FileRecord.year).filter(
            FileRecord.album != None).distinct()

    @classmethod
    def get(cls, name, artist = None, year = None):
        """
        We're pretending we have a normalized database, and providing
        a method to select by primary key optionally refined by artist
        """
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
    def get_by_artist(cls, artist):
        """
        get all albums by artist sorted by year
        """
        results = cls.query().filter(FileRecord.artist==artist).order_by(
            FileRecord.year).all()
        albums = []
        if results and len(results) > 0:
            for result in results:
                albums.append(cls(*result))

            return albums

        return albums

    def get_tracks(self):
        return TrackView.get_by_album(self.name)

    @classmethod
    def search(cls, criteria = None):
        """
        find album where album.name like criteria
        """
        qry = cls.query()
        if criteria:
            qry = qry.filter(FileRecord.album.like(u"%%%s%%" % criteria))

        results = []

        for result in qry.all():
            results.append(cls(*result))

        return results

    def get_zip_file(self):
        """
        build zip file of all tracks associated with this album.
        relying on caller to close the string io
        """
        io = StringIO()
        zf = zipfile.ZipFile(io, "w")
        try:
            for track in self.get_tracks():
                zf.write(track.file_name,
                         track.safe_file_name,
                         zipfile.ZIP_DEFLATED)
        finally:
            zf.close()

        io.reset()
        io.seek(0, 2)
        length = io.tell()
        io.reset()
        return io,\
               cleanse_filename("%s - %s.zip" % (self.name, self.year)),\
               length

    def _get_artist(self):
        """
        if multiple artists, then returns 'Various Artists' otherwise
        the artist name or '(Unknown)' if the tag lacks an artist
        """
        artists = FileRecord.query(FileRecord.artist).distinct().filter(
            FileRecord.album == self.name).filter(
            FileRecord.year == self.year).all()

        if len(artists)>1:
            return "Various Artists"
        elif len(artists) == 1:
            return artists[0][0]
        else:
            return "(Unknown)"

    artist = property(_get_artist)


class TrackView(object):
    """
    nearly identical to filerecord, adds a bit more to present tracks like
    they were coming from normalized data.
    """

    def __init__(self, fileRecord):
        self.__record = fileRecord

    @classmethod
    def query(cls):
        return FileRecord.query()

    @classmethod
    def get(cls, fid):
        val = cls.query().get(fid)
        assert val is not None
        return cls(val)

    @classmethod
    def search(cls, criteria = None):
        qry = cls.query()
        if criteria:
            qry = qry.filter(FileRecord.title.like(u"%%%s%%" % criteria))

        results = []

        for result in qry.all():
            results.append(cls(result))

        return results

    @classmethod
    def get_by_album(cls, album, artist = None, year = None):
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
    def get_by_artist(cls, artist):
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
        return u"%d - %s" % (self.track or 0, self.title.title())
