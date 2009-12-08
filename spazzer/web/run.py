from repoze.bfg.configuration import Configurator
from zope.sqlalchemy import ZopeTransactionExtension

from .models import get_root
from ..collection.manage import engine_from_config, init_model,\
    sessionmaker, scoped_session, init_model, create_tables

def app(global_config, **settings):
    """ This function returns a ``repoze.bfg`` application object.  It
    is usually called by the PasteDeploy framework during ``paster
    serve``"""
    config = {}
    config.update(global_config)
    config.update(settings)
    setup_model(**config)
    config = Configurator(root_factory=get_root, settings=settings)
    zcml_file = settings.get('configure_zcml', 'configure.zcml')
    config.load_zcml(zcml_file)
    return config.make_wsgi_app()

def setup_model(**config):
    """
    sets up collection model according to configuration
    """
    engine = engine_from_config(config)
    session = scoped_session(sessionmaker(bind = engine, 
                                          extension = ZopeTransactionExtension()))
    init_model(session)
    create_tables()
    
