"""
database meta stuff
"""
from sqlalchemy import MetaData

_metadata = MetaData()
_session = None
_engine = None

def _s():
    """
    returns session object used internally in queries for the model, presumably the session has already been 
    initialized by calling init_model_
    """
    global _session
    assert _session is not None,"session not initialized, init_model probably not called first..."

    return _session()


