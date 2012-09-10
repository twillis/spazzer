"""
common things needed by the tests
"""
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from spazzer.collection import manage

__here__ = os.path.abspath(os.path.dirname(__name__))
TMP_DBPATH = os.path.join(__here__, "tmpdb")

if not os.path.isdir(TMP_DBPATH):
    os.mkdir(TMP_DBPATH)


class TestDB(object):
    """create a database and method for removing it"""
    def __init__(self, echo=False):
        self.db_path = "%s.db" % os.path.join(TMP_DBPATH, str(uuid.uuid4()))
        db_url = "sqlite:///%s" % self.db_path
        self.engine = create_engine(db_url,
                                    echo=echo)
        session = scoped_session(sessionmaker())
        session.configure(bind=self.engine)
        manage.init_model(session)
        self.db_url = db_url

    def tearDown(self):
        if os.path.isfile(self.db_path):
            os.remove(self.db_path)
