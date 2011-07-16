from pyramid.configuration import Configurator
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import get_root
from ..collection.manage import init_model, create_tables


def app(global_config, **settings):
    """ This function returns a ``pyramid`` application object.  It
    is usually called by the PasteDeploy framework during ``paster
    serve``"""
    config = {}
    config.update(global_config)
    config.update(settings)
    setup_model(**config)
    config = Configurator(root_factory=get_root, settings=settings)
    config.scan()
    config.add_static_view(name="static", path="spazzer.web:templates/static")
    return config.make_wsgi_app()


def setup_model(**config):
    """
    sets up collection model according to configuration
    """
    engine = engine_from_config(config)
    session = scoped_session(sessionmaker(bind=engine,
                               extension=ZopeTransactionExtension()))
    init_model(session)
    create_tables()
