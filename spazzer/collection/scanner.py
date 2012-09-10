"""
file system scanner seeks out music assets
"""
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
import os
import stat
from datetime import datetime
from paste.script.command import Command, BadCommand
from paste.deploy import appconfig
import sys
from .model import FileRecord, MountPoint
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker, scoped_session
import manage
import logging
log = logging.getLogger(__name__)

F_MP3 = ".mp3"
F_FLAC = ".flac"
VALID_XTNS = [F_MP3, F_FLAC]
FS_ENC = sys.getfilesystemencoding()


def get_metadata_mp3(f):
    """
    metadata parser for mp3s
    """
    return dict(EasyID3(f).items())


def get_metadata_flac(f):
    """
    metadata parser for flac
    """
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
            d["file"] = f
            d["create_date"] = datetime.fromtimestamp(stats[stat.ST_CTIME])
            d["modify_date"] = datetime.fromtimestamp(stats[stat.ST_MTIME])
            return d
        except Exception as ex:
            log.error(ex, exc_info=True)
            return dict(file=f, exception=str(ex))

    return _x

get_metadata = build_metadata_processor()


def session_committer():
    manage.meta._s().commit()


def session_rollbacker():
    manage.meta._s().rollback()


def is_contained(path, mounts):
    """
    check to make sure path does not sit on a path already registered
    """
    if not path.endswith(os.path.sep):
        path = "%s%s" % (path, os.path.sep)

    part = path
    if not mounts:
        return False
    while not os.path.ismount(part):
        if os.path.dirname(part) in dict((os.path.dirname(m.mount), m.mount) for m in mounts):
            return True
        else:
            part = os.path.dirname(part)

    return False

class Scanner(object):
    """
    callable to kick off the scan job.

    dirs - list of directories to walk
    last_update - if less than, ignore
    """

    def __init__(self,
                 dirs,
                 last_update=datetime(1900, 1, 1),
                 committer=session_committer,
                 rollbacker=session_rollbacker):
        self.dirs = dirs
        self.last_update = last_update
        self.RECORD_CACHE =  dict(FileRecord.query(FileRecord.file_name, FileRecord).all())
        self.MOUNT_CACHE = self.get_mounts()
        self.committer = committer
        self.rollbacker = rollbacker
        self.errors = []

    def _do_prune(self):
        items_to_remove = []

        for f, r in self.RECORD_CACHE.items():
            if not self.is_contained(f) or not os.path.exists(f):
                items_to_remove.append(r)

        if len(items_to_remove) > 0:
            self.prune(items_to_remove)

    def _do_scan(self):
        for dir in self.dirs:
            for f in self.scan_dir(dir, self.last_update):
                self.process_file(f)
            self.committer()

    def __call__(self):
        self._do_prune()
        self._do_scan()

    def is_contained(self, path):
        """
        check to make sure path does not sit on a path already registered
        """
        mounts = self.get_mounts()
        return is_contained(path, mounts)

    def scan_dir(self, d, last_update=datetime(1900, 1, 1)):
        """
        walk directory for each file with extension in VALID_XTNS, yield metadata
        can be further filtered by comparing modified time of file against
        last_update
        """
        d = os.path.abspath(d)
        for r, dirs, files in os.walk(d):
            for x in (os.path.join(r, f) for f in files):
                if os.path.splitext(x)[1].lower() in VALID_XTNS:
                    stats = os.stat(x)
                    file_update = datetime.fromtimestamp(stats[stat.ST_MTIME])
                    rec = self.get_file_from_db(x)
                    if not rec or (rec and file_update > rec.modify_date)\
                       and (not last_update or (last_update and \
                                                last_update < file_update)):
                        log.info("need metadata for %s" % x)
                        yield get_metadata(x)

    def get_file_from_db(self, file_name):
        """
        consult the cache if it exists, otherwise go straight to the db
        """
        fname = unicode(file_name, "utf-8") if not isinstance(file_name, unicode) else file_name
        if self.RECORD_CACHE:
            return self.RECORD_CACHE.get(file_name) or FileRecord.query().filter(
                FileRecord.file_name == fname).first()
        else:
            return FileRecord.query().filter(
                FileRecord.file_name == fname).first()

    def get_mounts(self):
        """
        in the case of scanning the collection, we generate this ahead of time
        to save time.
        """
        if hasattr(self, "MOUNT_CACHE"):
            return self.MOUNT_CACHE
        else:
            return MountPoint.query().all()

    def prune(self, reclist):
        try:
            session = manage.meta._s()
            for r in reclist:
                session.delete(r)
            self.committer()
            log.debug("done...")
        except Exception as ex:
            log.error(ex, exc_info=True)
            log.info("rolling back")
            self.rollbacker()

    def process_file(self, info):
        try:
            if "exception" in info:
                ex = info.pop("exception")
            else:
                file_name = info.pop("file")
                file_name = unicode(file_name, "utf-8") if not isinstance(file_name, unicode) else file_name
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

                rec = self.get_file_from_db(file_name)
                if not rec:
                    rec = FileRecord(file_name,
                                     create_date,
                                     modify_date,
                                     artist=artist,
                                     album=album,
                                     title=title,
                                     year=year,
                                     track=track)
                elif rec.modify_date != modify_date:
                    rec.update(create_date,
                               modify_date,
                               artist=artist,
                               album=album,
                               title=title,
                               year=year,
                               track=track)
                else:
                    rec = None  # noop

                try:
                    if rec:
                        manage.meta._s().add(rec)

                except Exception as dbex:
                    self.rollbacker()

                    raise dbex
        except Exception as ex:
            self.errors.append((info, ex))
            log.error((info, ex), exc_info=True)


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
                      help="only process files who have been updated since YYYY-MM-DD HH:MM")

    parser.add_option("--section",
                      action="store",
                      type="string",
                      dest="section",
                      help="section in config file to pickup settings")

    def parse_last_modified(self):
        if self.options.last_modified:
            try:
                self.last_modified = datetime.strptime(
                    self.options.last_modified,
                    "%Y-%m-%d %H:%M")
            except ValueError as ve:
                log.error(ve)
                self.last_modified = None
        else:
            self.last_modified = None

    def parse_section(self):
        return self.options.section

    def get_config(self, name):
        if len(self.args) == 1:
            config_file = self.args[0]
            if not os.path.isfile(config_file):
                raise BadCommand("""
                %s
                Error: CONFIG_FILE not found at %s%s.
                Please specify a CONFIG_FILE""" %
                                 (self.parser.get_usage(),
                                  os.path.sep,
                                  config_file))
            else:
                config = appconfig("config:%s" % config_file,
                                   name=name,
                                   relative_to=os.getcwd())
                return config
        else:
            raise BadCommand(self.parser.get_usage())

    def command(self):
        self.parse_last_modified()
        paste_config = self.get_config(self.parse_section())
        engine = engine_from_config(paste_config)
        session = scoped_session(sessionmaker())
        session.configure(bind=engine)
        manage.init_model(session)

        self.errors = []

        scanner = Scanner([m[0] for m in
                           session.query(MountPoint._mount).all()],
                          last_update=self.last_modified)

        scanner()

        result = "with errors" if len(scanner.errors) > 0 else "with no errors"
        log.info("scanning complete %s" % result)

        if len(scanner.errors):
            for error in scanner.errors:
                log.error(error)
                print error
    # def _callback(self, info):
    #     process_file(info, self.errors)

    # def _prune(self, reclist):
    #     prune(reclist)



