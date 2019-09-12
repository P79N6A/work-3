# coding: utf-8
import redis

from sqlalchemy import create_engine, event, exc

import settings

_engine = None
_redis = None


def ping_connection(dbapi_connection, connection_record, connection_proxy):
    """检测mysql连接状态"""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except exc.OperationalError as ex:
        import logging
        logging.warn("", exc_info=True)
        if ex.args[0] in (2006,  # MySQL server has gone away
                          2013,  # Lost connection to MySQL server during query
                          2055,  # Lost connection to MySQL server at '%s', system error: %d
                          ):
            raise exc.DisconnectionError()
        else:
            raise
    cursor.close()


def get_engine():
    global _engine
    if not _engine:
        _engine = create_engine(
            settings.DB_URL,
            echo=settings.DEBUG,
            echo_pool=True,
            pool_recycle=3600,
        )
    return _engine

