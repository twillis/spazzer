"""
Database model for collection metadata
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode, Integer, DateTime
from meta import _s
from alchemyextra.schema import id_column

Base = declarative_base()

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
    def query(cls,attrs = None):
        """
        attrs to select if None then entire class
        """
        if not attrs:
            attrs = [cls]
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

