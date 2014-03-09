from pyramid.config import Configurator
from pyramid.static import static_view
from pyramid.exceptions import HTTPNotFound
from webob import Response
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import get_root
from ..collection.manage import init_model, create_tables


def app(global_config, **settings):
    """ This function returns a ``pyramid`` application object.  It
    is usually called by the PasteDeploy framework during ``paster
    serve``"""
    combined_config = {}
    combined_config.update(global_config)
    combined_config.update(settings)
    setup_model(**combined_config)
    config = Configurator(settings=combined_config)
    config.include("pyramid_mako")
    config.add_route("api", "/api/*traverse", factory=get_root)
    config.add_static_view("", combined_config.get("static_dir", None))
    static_dir_tmp = combined_config.get("static_dir_tmp", None)

    if static_dir_tmp:
        tmp_static_view = static_view(static_dir_tmp, use_subpath=True)
        def last_chance(context, request):
            try:
                return tmp_static_view(context, request)
            except HTTPNotFound:
                return Response("not found: %s" % request.path,status=404)
        config.add_view(last_chance, context=HTTPNotFound)

    config.scan()

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
