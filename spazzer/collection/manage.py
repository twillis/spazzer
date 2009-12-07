"""
routines to setup the model
"""
import meta
from model import Base
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker, scoped_session
 
def init_model(session, engine = None):
    """
    must be called before using any of the model objects to setup
    metadata,sessionmaker etc....
    """
    meta._session = session
    
    if not engine:
        meta._engine = meta._session.bind
    else:
        meta._engine = engine

    create_tables()

def create_tables():
    Base.metadata.create_all(meta._session.bind)
