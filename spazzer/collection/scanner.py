"""
file system scanner seeks out music assets
"""

from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
import os
import stat
from datetime import datetime
import threading
import time
from paste.script.command import Command, BadCommand
from paste.deploy import appconfig
import sys
from .model import FileRecord, MountPoint
import manage

F_MP3 = ".mp3"
F_FLAC = ".flac"
VALID_XTNS = [F_MP3, F_FLAC]
FS_ENC = sys.getfilesystemencoding()

def get_metadata_mp3(f):
    return dict(EasyID3(f).items())

def get_metadata_flac(f):
    return dict(FLAC(f).items())

def build_metadata_processor():
    """
    maps the file type processors to the corresponding extensions
    """
    processors = {}
    processors[F_MP3] = get_metadata_mp3
    processors[F_FLAC] = get_metadata_flac

    def _x(f):
        """
        retrieves metadata from file :param:`f` by delegating
        to file type specific fucntion. returns either a dictionary
        of tag data, or if exception occurs a dict(file,exception)
        """
        try:
            d = processors[os.path.splitext(f)[1].lower()](f)
            stats = os.stat(f)
            d["file"] =f  #unicode(f, encoding = FS_ENC)
            d["create_date"] = datetime.fromtimestamp(stats[stat.ST_CTIME])
            d["modify_date"] = datetime.fromtimestamp(stats[stat.ST_MTIME])
            return d
        except Exception as ex:
#            return dict(file=unicode(f, encoding = FS_ENC), exception=str(ex))
            return dict(file=f, exception=str(ex))

    return _x

get_metadata = build_metadata_processor()

def scan_dir(d, last_update = datetime(1900,1,1)):
    """
    walk directory for each file with extension in VALID_XTNS, yield metadata
    can be further filtered by comparing modified time of file against 
    last_update
    """
    d = os.path.abspath(d)
    for r, dirs, files in os.walk(d):

        for x in (os.path.join(r,f) \
                      for f in files \
                      if os.path.splitext(f)[1].lower() in VALID_XTNS):

            stats = os.stat(x)
            if not last_update or (last_update and \
                    last_update < datetime.fromtimestamp(stats[stat.ST_MTIME])):
                yield get_metadata(x)

class Scanner(object):
    def __init__(self, dirs, last_update = datetime(1900,1,1), callback=None):
        self.dirs = dirs
        self.last_update = last_update
        self._callback = callback or self._print

    def callback(self,info):
        self._callback(info)
        
    def _print(self, info):
        print info

    def __call__(self):
        for dir in self.dirs:
            for f in scan_dir(dir, self.last_update):
                self.callback(f)

class ScannerCommand(Command):
    """
    Run scan to update the database.
    requires a config_file argument
    
    Example::
       $ paster scan production.ini
    """

    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    min_args = 1
    max_args = 2
    parser = Command.standard_parser()
    parser.add_option("--last-modified", 
                      action="store", 
                      type="string", 
                      dest="last_modified",
                      help = "only process files who have been updated since YYYY-MM-DD HH:MM")

    parser.add_option("--section",
                      action="store",
                      type="string",
                      dest="section",
                      help="section in config file to pickup settings")

    def parse_last_modified(self):
        if self.options.last_modified:
            try:
                self.last_modified = datetime.strptime(
                    self.options.last_modified,\
                    "%Y-%m-%d %H:%M")
            except ValueError as ve:
                print ve
                self.last_modified = None
        else:
            self.last_modified = None

    def parse_section(self):
        return self.options.section

    def get_config(self, name):
        if len(self.args)==1:
            config_file = self.args[0]
            if not os.path.isfile(config_file):
                raise BadCommand(
"""
%s
Error: CONFIG_FILE not found at %s%s.
Please specify a CONFIG_FILE"""% 
                    (self.parser.get_usage(), 
                    os.path.sep,
                    config_file))
            else:
                config = appconfig("config:%s" % config_file, 
                                   name = name, 
                                   relative_to = os.getcwd())
                return config
        else:
            raise BadCommand(self.parser.get_usage())
        
    def command(self):
        
        self.parse_last_modified()
        paste_config = self.get_config(self.parse_section())        
        
        
        engine = manage.engine_from_config(paste_config)
        session = manage.scoped_session(manage.sessionmaker())
        session.configure(bind=engine)
        manage.init_model(session)
        
        self.errors = []
        
        scanner = Scanner([m[0] for m in \
                               session.query(MountPoint.mount).all()], 
                          callback = self._callback,
                          last_update = self.last_modified)
        scanner()

        result = "with errors" if len(self.errors)>0 else "with no errors"
        print "scanning complete %s" % result
        
        if len(self.errors):
            for error in self.errors:
                print error
        
    def _callback(self,info):

        try:
            if "exception" in info:
                ex = info.pop("exception")
                self.errors.append((info,ex))
            else:
                file_name = info.pop("file")
                create_date = info.pop("create_date")
                modify_date = info.pop("modify_date")
                
                artist = info.get("artist")[0]\
                    if "artist" in info else None
                
                album = info.get("album")[0]\
                    if "album" in info else None
                
                year = int(info.get("date")[0].split("-")[0])\
                    if "date" in info else None
                
                track = int(info.get("tracknumber")[0].split("/")[0])\
                    if "tracknumber" in info else None
                
                title = info.get("title")[0]\
                    if "title" in info else None

                rec = FileRecord.get_by_filename(file_name)
                if not rec:
                    rec = FileRecord(file_name,
                                 create_date, 
                                 modify_date, 
                                 artist = artist,
                                 album = album,
                                 title = title,
                                 year = year,
                                 track = track)
                elif rec.modify_date != modify_date:
                    rec.update(create_date, 
                                 modify_date, 
                                 artist = artist,
                                 album = album,
                                 title = title,
                                 year = year,
                                 track = track)
                else:
                    rec = None #noop

                try:
                    if rec:
                        manage.meta._s().add(rec)
                        manage.meta._s().commit()
                except Exception as dbex:
                    manage.meta._s().rollback()
                    raise dbex
        except Exception as ex:
            self.errors.append((info,ex))
            print info,ex
